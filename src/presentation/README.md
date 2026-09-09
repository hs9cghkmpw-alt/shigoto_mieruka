# Presentation boundary

The domain is intentionally UI-independent. A production UI should consume repository read APIs and must expose:

- chronological WorkTrace timeline
- unassigned/ambiguous tray
- candidate score and linked evidence IDs
- human confirmation/correction
- FACT/ANALYSIS/KNOWLEDGE distinction
- capability hypotheses with context and review state
- audit history

No UI is claimed complete until these workflows are exercised against persisted data.
