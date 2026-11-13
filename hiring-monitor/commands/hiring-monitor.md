---
description: Manage or run the hiring monitor (add/remove/list/run/pause/resume/settings/setup)
argument-hint: "add <Company> | remove <Company> | list | run | leads | pause | resume | settings <changes> | setup"
---

Use the `hiring-monitor` skill to handle this request: $ARGUMENTS

If no arguments were given, show the watchlist, the time of the last run from `monitor/log.md`, and the number of new leads in `monitor/hiring-leads.csv`, then list the available commands. If `monitor/` doesn't exist yet, start first-time setup.
