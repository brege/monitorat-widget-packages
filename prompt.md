The rules in AGENTS.md are non-negotiable. These rules must always be followed.

You are working in the [monitor@ source code](https://github.com/brege/monitorat) directory. Before touching anything, read AGENTS.md for repo norms and skim README.md for widget architecture.

Goal: build a `packages` widget in the sandbox at `testing/widgets/packages/` (not yet deployed to user config). The widget follows the standard widget pattern. Backend must expose `/api/system-packages`. It should:

* Run the following collectors (use exactly these commands; capture stdout and count entries):
  - `dnf repoquery --installed`
  - `python3 -m pip list --format=json`
  - `npm list -g --depth=0 --json`
  - `flatpak list --app --columns=application`
* Cache results to monitor@’s `paths.data` directory (use `get_data_path()`) so page reloads
immediately show the last counts. On cache-miss or when `?refresh=1` is requested, refresh
asynchronously (background thread) while returning the cached payload plus `updating:true`.
* Include updated timestamp and `updating` flag in the API response.

Frontend requirements:

* Place HTML/JS under `testing/widgets/packages/`. JS must register `window.widgets.packages` and fetch
`widgets/packages/packages.html`.
* On init, load cached data immediately, request `?refresh=1`, and poll every `refresh_seconds`
(configurable, default 5s) until `updating:false`. Display counts plus a “Last updated … /
Refreshing…” metadata line.

Implementation notes:

* Keep the implementation minimal. Study the **services** widget in `www/widgets/services/` as your reference for simplicity, not metrics or reminders.
* Avoid over-engineering error handling, type hints, or defensive coding patterns. Simple try/except blocks are sufficient.
* Write straightforward code without unnecessary helper functions or abstractions.

Config/documentation:

* Add `testing/widgets/packages/config_default.yaml` with a minimal block (`name`, `collapsible`,
`hidden`, `refresh_seconds`). Access via `config["widgets"]["packages"]` using confuse's `.get(type)`
pattern as shown in AGENTS.md.
* README snippet is optional unless something is clearly incorrect; focus on the widget files.

To test your work, run:
```
pip install .
gunicorn --bind localhost:6161 monitorat.monitor:app
```
Then verify the API endpoint with `curl http://localhost:6161/api/system-packages` (should return JSON with packages, updated, and updating keys). The user will verify the full widget at http://localhost:6161.


Deliverables: 
```
testing/widgets/packages/
.
├── api.py
├── config_default.yaml
├── __init__.py
├── packages.html
└── packages.js
```
Note: Once the user is satisfied, they will move the widget from the sandbox (`testing/widgets/packages/`) to their config root (`~/.config/monitor@/widgets/packages/`).


Do not edit `www/monitor.py`. Do not run `sudo`. Do not run state-changing git commands (commit, push, rebase, etc.). Do not run `systemctl`.

If something blocks you (permissions, missing tools), explain the issue before proceeding.
