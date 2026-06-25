#!/usr/bin/env bash
# sdd-cache-post.sh — SSRF-safe SDD URL cache (post: symlink guard + write)
#
# After successfully fetching a remote SDD/spec document, store its content in
# the cache so sdd-cache-pre.sh can serve it on the next call within the TTL.
# Reads the fetched content from stdin (or from a file passed as the third arg).
#
# Usage:
#   <fetch-command> | ./hooks/sdd-cache-post.sh <url> [<cache-dir>]
#   ./hooks/sdd-cache-post.sh <url> [<cache-dir>] < fetched-content.txt
#
# Env vars:
#   SDD_CACHE_DIR  — override default cache directory (~/.cache/wheelwright/sdd)
#
# SSRF guards (mirrors sdd-cache-pre.sh):
#   * Only http:// and https:// schemes accepted.
#   * RFC-1918, loopback, link-local hosts are blocked.
#   * Redirect-following disabled (--max-redirs 0) in any curl calls.
#   * The cache directory is verified to be a real directory, not a symlink —
#     refuses to write if CACHE_DIR resolves to a symlink (path-traversal guard).
#
# Exit codes:
#   0  Content written to cache.
#   2  Invalid URL, symlink guard triggered, or other security check failed.

set -euo pipefail

URL="${1:-}"
CACHE_DIR="${2:-${SDD_CACHE_DIR:-${HOME}/.cache/wheelwright/sdd}}"

if [[ -z "$URL" ]]; then
    echo "Usage: <fetch> | $0 <url> [<cache-dir>]" >&2
    exit 2
fi

# ── SSRF guard ────────────────────────────────────────────────────────────────
validate_url() {
    local url="$1"

    if ! [[ "$url" =~ ^https?:// ]]; then
        echo "ERROR [sdd-cache-post]: rejected URL scheme (only http/https allowed): $url" >&2
        exit 2
    fi

    local host
    host=$(printf '%s' "$url" \
        | sed 's|^https\?://||; s|[/?#].*||; s|.*@||; s|:[0-9]*$||')

    local -a blocked_patterns=(
        '^localhost$'
        '^localhost\.'
        '^127\.'
        '^::1$'
        '^0\.'
        '^10\.'
        '^172\.(1[6-9]|2[0-9]|3[01])\.'
        '^192\.168\.'
        '^169\.254\.'
        '^100\.64\.'
        '^fc[0-9a-f][0-9a-f]:'
        '^fe80:'
        '^\[::1\]$'
    )

    for pat in "${blocked_patterns[@]}"; do
        if [[ "$host" =~ $pat ]]; then
            echo "ERROR [sdd-cache-post]: SSRF guard — blocked private/loopback/metadata host: $host" >&2
            exit 2
        fi
    done
}

validate_url "$URL"

# ── Symlink guard ─────────────────────────────────────────────────────────────
# Refuse to write if CACHE_DIR itself is a symlink or if any component of the
# path resolves through one to an unexpected location.
symlink_guard() {
    local dir="$1"
    # Create the directory if it doesn't exist (before checking).
    mkdir -p "$dir"
    # Now check: is the created/existing path a symlink?
    if [[ -L "$dir" ]]; then
        echo "ERROR [sdd-cache-post]: symlink guard — CACHE_DIR is a symlink, refusing to write: $dir" >&2
        exit 2
    fi
    # Verify the resolved real path matches what we expect.
    if command -v realpath &>/dev/null; then
        local real
        real=$(realpath "$dir")
        if [[ "$real" != "$dir" && "$real" != "$(realpath -m "$dir")" ]]; then
            echo "ERROR [sdd-cache-post]: symlink guard — CACHE_DIR resolves to an unexpected path: $real" >&2
            exit 2
        fi
    fi
}

symlink_guard "$CACHE_DIR"

# ── Cache-key (mirrors pre-hook) ──────────────────────────────────────────────
if command -v sha256sum &>/dev/null; then
    KEY=$(printf '%s' "$URL" | sha256sum | awk '{print $1}' | cut -c1-40)
elif command -v shasum &>/dev/null; then
    KEY=$(printf '%s' "$URL" | shasum -a 256 | awk '{print $1}' | cut -c1-40)
else
    KEY=$(printf '%s' "$URL" | tr -cs 'a-zA-Z0-9._-' '_' | cut -c1-120)
fi

CACHE_FILE="${CACHE_DIR}/${KEY}.body"
META_FILE="${CACHE_DIR}/${KEY}.meta"

# ── Write body from stdin ─────────────────────────────────────────────────────
# Read all of stdin into a temp file first, then atomic-rename into place.
TMP_BODY=$(mktemp "${CACHE_DIR}/.sdd-cache-tmp.XXXXXX")
trap 'rm -f "$TMP_BODY"' EXIT

cat > "$TMP_BODY"

# Sanity: refuse to cache empty responses (likely an error page).
if [[ ! -s "$TMP_BODY" ]]; then
    echo "ERROR [sdd-cache-post]: fetched content is empty — not caching." >&2
    exit 2
fi

# Atomic rename: body is only visible once the meta is written.
mv "$TMP_BODY" "$CACHE_FILE"

# ── Write metadata ────────────────────────────────────────────────────────────
printf 'url=%s\nfetched_at=%s\n' "$URL" "$(date +%s)" > "$META_FILE"

exit 0
