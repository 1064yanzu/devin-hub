# Roadmap and acceptance criteria

## Stage 0 — Runnable foundation (current)
- [x] Event receiver and idempotent storage
- [x] Deterministic warnings for test failures and risky file changes
- [x] Git path-metadata collector
- [x] Alert retrieval API and CLI
- [x] Tests and GitHub Actions workflow

## Stage 1 — Reliable cross-device transport
- [ ] Enroll two workstation nodes with independent identities
- [ ] Secure Mini PC access over a private encrypted network
- [ ] Retry queue, acknowledgments, and offline replay
- [ ] Track event processing latency, loss, and duplicate rate
- [ ] Prove two devices can report distinct changes into one hub

**Exit criterion:** unplug one node during an event burst, reconnect, and confirm each event is stored once.

## Stage 2 — IDE / terminal context
- [ ] VS Code diagnostic and test runner integration
- [ ] Explicit consent for terminal metadata capture
- [ ] Context filters, allowlists, and retention controls
- [ ] Desktop notifications with deep links to local context

**Exit criterion:** reproduce a build failure and receive a useful warning with a local reference.

## Stage 3 — Cross-device review
- [ ] Shared repository identity and branch/commit lineage
- [ ] API/schema contract extraction and compatibility tests
- [ ] Decision log and user-defined project constraints
- [ ] Reproducible cross-branch conflicts with evidence
- [ ] Feedback: acknowledge, dismiss, verify false positives

**Exit criterion:** detect a deliberately introduced incompatible change on a second workstation, explain the evidence, and verify the warning through a failing test.

## Stage 4 — Optional semantic agents
- [ ] Pluggable local/remote LLM review with explicit privacy policy
- [ ] Cost/risk budget and deterministic prefilter
- [ ] Sandbox-based patch proposals, never silent application
- [ ] Evaluation corpus and false-positive-rate reporting

**Exit criterion:** demonstrate measured improvement over rules alone, with user approval for changes.
