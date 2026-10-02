## Agent skills

### Issue tracker

GitHub Issues on the fork `EnderWolf50/AhabAssistantLimbusCompany` (always pass `--repo`). See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Automation notes

- **Validating on the emulator** (running a mirror from source, weekly-bonus safety, archiving logs, burst screenshots): `docs/agents/device-testing.md`.
- **Screenshots, waits, template matching, OCR, MuMu input**: before replacing a sleep, adding a template, or matching for an irreversible action, read `docs/agents/recognition-pitfalls.md`.
- **Battle** (starting turns, defense, polling): `docs/agents/battle-notes.md`.
- **Shop, theme pack, floor map, events**: observed UI behaviour and coordinates in `docs/agents/mirror-ui-behaviour.md`.
- **Speed claims**: measure per action, not per run; `docs/agents/perf-measurement.md`.
