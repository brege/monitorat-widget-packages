# AGENTS.md

This file provides guidance to GPT-style coding agents (Codex, ChatGPT, etc.) when working with this repository.

## Project Overview

@README.md

### Key Architecture Components

- **Backend**: Flask web server (`www/monitor.py`) served via Gunicorn
- **Configuration**: `confuse` library for hierarchical YAML config with type validation and default merging
- **Widget System**: Modular widgets located in `www/widgets/` with paired backend APIs and HTML/JS frontends
- **Config Manager**: Thread-safe reload system with callback support
- **Data Storage**: CSV files for historical metrics plus filesystem paths for other widget data

### Widget Architecture

Each widget follows:
- `api.py` – exposes `register_routes(app)` and optional background hooks
- `{widget}.html` – widget template
- `{widget}.js` – frontend logic and API calls

Available widgets: metrics, network, reminders, services, speedtest, wiki.

## Development Commands

### Setup
```bash
cd www
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running the Server
```bash
# Development
source .venv/bin/activate
gunicorn --bind localhost:6161 monitor:app
```

## Configuration with confuse

### Access Patterns
```python
from monitor import config

interval = config["widgets"]["metrics"]["daemon"]["interval_seconds"].get(int)
enabled_widgets = config["widgets"]["enabled"].get(list)
items = config["widgets"]["services"]["items"].get(dict)

widget_config = config["widgets"]["metrics"]
```

### Structure
- `www/config_default.yaml` – canonical schema and defaults (reference only; do not edit for env-specific changes): **confuse**
- User overrides merge automatically via **confuse**
- **confuse** enforces types and hierarchy handling
- Ask the user to run `git clone https://github.com/beetbox/confuse.git` if you need clarity on its library and documentation.

## Key Implementation Details

### Configuration System
- Thread-safe `ConfigManager` controls reloads via confuse
- Widgets register callbacks to respond to config changes

### Widget Development

**Widget Discovery:**
`www/monitor.py` reads `config["widgets"]["enabled"]` (ordered list of widget names). For each widget:
1. It reads the widget's config block: `config["widgets"][widget_name].get(dict)`
2. It determines the widget type (defaults to widget name): `widget_type = config_block.get("type", widget_name)`
3. It imports the module: `importlib.import_module(f"widgets.{widget_type}.api")`
4. It calls the module's `register_routes(app)` function, passing the Flask app

Widgets can live in `www/widgets/{type}/api.py` or in user-configured paths (e.g., `~/.config/monitor@/widgets/{type}/`). The `extend_widget_package_path()` function adds user widget directories to Python's import path so agents can find them.

**Implementation:**
- Create `{widget_dir}/api.py` with a `register_routes(app)` function that registers Flask routes.
- Backends live either under `www/widgets/<type>/api.py` or user paths referenced in config includes; stick to that layout.
- Frontend scripts are loaded lazily per widget type (see `www/app.js`), so ensure `window.widgets.<type>` is set when your script executes.
- Access widget config via `config["widgets"]["widget_name"]`
- Use `get_data_path()` helper for file storage
- Lean on confuse for validation and conversion instead of manual parsing.

**Widget Archetypes:**
Study existing widgets in `www/widgets/` to understand patterns for:
- Data collection and background workers (metrics, network)
- Subprocess execution and error handling (if applicable)
- Frontend polling and real-time updates (network, reminders)
- API response structure and caching (metrics, services)
- Configuration parsing and defaults (all widgets)

### Background Processes
- Metrics daemon polls system stats
- Reminders daemon triggers Apprise notifications
- Daemons respect widget enable/disable flags

## File Structure Notes

- `systemd/monitor@.service` – template for multi-host deployments
- `scripts/yamlfixfix.py` – YAML formatter that preserves HH:MM time strings
- `www/shared/` – shared JS utilities (ChartManager, DataFormatter, TableManager)
- `vendors/` – auto-downloaded markdown rendering deps

## Rules

- NEVER run `sudo`
- NEVER run state-changing git commands (commit, push, rebase, etc.)
- ALWAYS ask before editing DOCS or README.md
- Prefer existing libraries to re-implementation
- Use confuse’s validation/type conversion instead of manual parsing
- NEVER use emojis
- NO sycophancy
- NO ass-kissing
- NO casual talk / cool guy-talk / therapy-speak
- NO vacuous jargon: "robust" "enhanced" "wire" "hydrate" etc.
- Execute requests efficiently without unnecessary exposition unless asked
- Treat user configuration (`~/.config/monitor@/config.yaml` or includes) as the authoritative place for changes; do not tell users to edit `www/config_default.yaml` unless explicitly instructed.
- Avoid hidden or unexplained automation: document any non-trivial command or transformation you run so the user can follow the change.
