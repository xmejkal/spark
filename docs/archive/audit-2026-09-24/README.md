# Audit, 2026-09-24

Three reviewers were given the plugin cold and worked separately: one auditing for gaps, one
using it as a stranger on their own project, one testing whether an unattended agent could drive
it. All three independently opened on the same defect — `check_all.py` calling a function that has
never existed, so the flagship check has never run through the runner.

These are their reports verbatim, kept because roughly sixty findings are more detail than a
backlog should carry. The verified subset, and what it changes, is `BACKLOG.md` §4c.

**They are reviews, not facts.** Everything promoted into §4c was reproduced first. The rest is
unverified and should be treated as a lead.
