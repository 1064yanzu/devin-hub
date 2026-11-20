# Security notes

This is a prototype, not a hardened service.

- Server defaults to `127.0.0.1`; never bind directly to a public interface.
- Set a high-entropy `DEVIN_HUB_TOKEN` in the environment. Do not commit it.
- The HTTP prototype **does not implement TLS**. For two machines, deploy through a trusted encrypted/private transport and restrict inbound access; do not expose credentials over the open internet.
- Git scanning submits names of staged, unstaged and untracked files. Even filenames can contain confidential information: audit them before sending to any central node.
- The ingestion API validates event IDs, kinds, and payload type and limits bodies to 64 KiB, but does not implement comprehensive schema validation, quota enforcement, retention expiry, or per-node permissions.
- No remote shell actions, automated code modification, or automatic patching.
- Store database under `data/` (gitignored), restrict file-system permissions, and arrange backups appropriate to your threat model.
- Do not submit credentials, shell transcript bodies, secrets, tokens, or proprietary source into the event payload.
- In a production version, implement mutual node authentication, TLS, node-specific authorization, audit logs, rate limits, redaction, retention enforcement, and secure secret storage.

## Disclosure

Please avoid filing real secrets or private repository data in public GitHub issues. Report a suspected security issue privately to the repository maintainer rather than posting exploit details publicly.
