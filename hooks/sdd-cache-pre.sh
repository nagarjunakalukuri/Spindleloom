#!/usr/bin/env bash
# sdd-cache-pre.sh — SSRF-safe SDD URL cache (pre: validate + TTL check)
#
# Before fetching a remote SDD/spec document, check whether a fresh cached copy
# already exists.  Prints the cached content to stdout and exits 0 on a hit so
# the caller can skip the network fetch entirely.  Exits 1 on miss / expired so
# the caller knows to fetch and then call sdd-cache-post.sh.
#
# Usage:
#   ./hooks/sdd-cache-pre.sh <url> [<cache-dir>]
#
# Env vars:
#   SDD_CACHE_DIR      — override default cache directory (~/.cache/spindleloom/sdd)
#   SDD_CACHE_MAX_AGE  — TTL in seconds (default: 604800 = 7 days)
#
# SSRF guards:
#   * Only http:// and https:// schemes are allowed.
#   * RFC-1918, loopback, link-local, and 0.x/0::/metadata-range hosts are blocked.
#   * Redirect-following is disabled (--max-redirs 0) — callers that invoke curl
#     directly must use the same flag.
#
# Exit codes:
#   0  Cache hit — content printed to stdout.
#   1  Cache miss or expired — caller should fetch.
#   2  Invalid URL (SSRF guard triggered) — caller must NOT fetch.

set -euo pipefail

URL="${1:-}"
CACHE_DIR="${2:-${SDD_CACHE_DIR:-${HOME}/.cache/spindleloom/sdd}}"
SDD_CACHE_MAX_AGE="${SDD_CACHE_MAX_AGE:-604800}"   # 7 days

if [[ -z "$URL" ]]; then
    echo "Usage: $0 <url> [<cache-dir>]" >&2
    exit 2
fi

# ── SSRF guard ────────────────────────────────────────────────────────────────
validate_url() {
    local url="$1"

    # Allow only http/https schemes.
    if ! [[ "$url" =~ ^https?:// ]]; then
        echo "ERROR [sdd-cache-pre]: rejected URL scheme (only http/https allowed): $url" >&2
        exit 2
    fi

    # Extract the bare hostname (strip scheme, path, port, credentials).
    local host
    host=$(printf '%s' "$url" \
        | sed 's|^https\?://||; s|[/?#].*||; s|.*@||; s|:[0-9]*$||')

    # Block RFC-1918, loopback, link-local, metadata, and 0.x.
    local -a blocked_patterns=(
        '^localhost$'
        '^localhost\.'
        '^127\.'
        '^::1$'
        '^0\.'
        '^10\.'
        '^172\.(1[6-9]|2[0-9]|3[01])\.'
        '^192\.168\.'
        '^169\.254\.'      # link-local / AWS IMDS range
        '^100\.64\.'       # RFC 6598 shared address space
        '^fc[0-9a-f][0-9a-f]:'   # IPv6 unique-local
        '^fe80:'           # IPv6 link-local
        '^\[::1\]$'
    )

    for pat in "${blocked_patterns[@]}"; do
        if [[ "$host" =~ $pat ]]; then
            echo "ERROR [sdd-cache-pre]: SSRF guard — blocked private/loopback/metadata host: $host" >&2
            exit 2
        fi
    done
}

validate_url "$URL"

# ── Cache-key + directory setup ───────────────────────────────────────────────
# Use a stable file-system-safe key: sha256 of the URL, truncated.
if command -v sha256sum &>/dev/null; then
    KEY=$(printf '%s' "$URL" | sha256sum | awk '{print $1}' | cut -c1-40)
elif command -v shasum &>/dev/null; then
    KEY=$(printf '%s' "$URL" | shasum -a 256 | awk '{print $1}' | cut -c1-40)
else
    # Fallback: URL with unsafe chars replaced (not collision-safe, acceptable for dev).
    KEY=$(printf '%s' "$URL" | tr -cs 'a-zA-Z0-9._-' '_' | cut -c1-120)
fi

CACHE_FILE="${CACHE_DIR}/${KEY}.body"
META_FILE="${CACHE_DIR}/${KEY}.meta"

# ── TTL enforcement: expire stale entries ─────────────────────────────────────
expire_old_entries() {
    [[ -d "$CACHE_DIR" ]] || return 0
    local now
    now=$(date +%s)
    # Scan all .meta files; remove body+meta pairs older than TTL.
    while IFS= read -r -d '' mf; do
        if [[ -f "$mf" ]]; then
            local ts
            ts=$(grep '^fetched_at=' "$mf" 2>/dev/null | cut -d= -f2 || echo 0)
            local age=$(( now - ts ))
            if (( age > SDD_CACHE_MAX_AGE )); then
                local base="${mf%.meta}"
                rm -f "${base}.body" "$mf"
            fi
        fi
    done < <(find "$CACHE_DIR" -maxdepth 1 -name '*.meta' -print0 2>/dev/null)
}

expire_old_entries

# ── Cache lookup ──────────────────────────────────────────────────────────────
if [[ -f "$CACHE_FILE" && -f "$META_FILE" ]]; then
    now=$(date +%s)
    ts=$(grep '^fetched_at=' "$META_FILE" 2>/dev/null | cut -d= -f2 || echo 0)
    age=$(( now - ts ))

    if (( age <= SDD_CACHE_MAX_AGE )); then
        # Fresh hit — print body to stdout.
        cat "$CACHE_FILE"
        exit 0
    fi
    # Expired — fall through to miss path (expired_old_entries already removed it).
fi

# ── Cache miss ────────────────────────────────────────────────────────────────
exit 1
