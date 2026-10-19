# Open questions

- **Key handoff** (deferred 2026-10-18): how a mission's HMAC key reaches an uplink station without passing through a repo, and how a station proves it holds the right key. Proposed: copy over SSH from the flight-secrets folder, verify by hash published in the mission pack. Receive stations are unaffected.
