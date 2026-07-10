# Client brief — MedRemind (E2E test feature)

RxKart is a 40-store pharmacy chain with an existing mobile app (250k monthly active patients)
and an existing pharmacist back-office web portal. They want a **prescription refill reminder
and approval module**:

- Patients receive refill reminders (push + SMS) when a prescription is due, and can request
  a refill in one tap.
- Pharmacists see a refill-request queue in the portal, approve/reject each, and can suggest
  a generic substitution (patient must accept the substitution before dispensing).
- **Controlled substances (Schedule II-V)** cannot be auto-reminded or one-tap refilled: they
  require an extra identity verification step and pharmacist-initiated contact.
- SMS goes through Twilio; push through the existing Firebase setup.
- **HIPAA applies** — PHI in notifications must be minimized (no drug names in SMS).
- Business target: raise on-time refill rate from 41% to 60% within 2 quarters.
- NFRs the client stated: reminder delivered within 5 minutes of its scheduled time;
  queue page loads < 2s at 500 concurrent pharmacists; 99.9% availability during store hours.
- Team: 1 PM (acting PO), 1 architect, 4 developers, 1 QA. Two-week sprints. Azure DevOps.
- Timeline pressure: leadership wants a first shippable slice in 3 sprints.
