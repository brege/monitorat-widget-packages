# monitor@packages Widget

This widget was generated entirely by an AI agent from **prompt.md** and **AGENTS.md**. These files constitute the complete specification needed to build a functional monitor@ widget. 

This widget provides the number of packages installed on Fedora Workstation that are tracked via:
- `dnf`
- `flatpak`
- `pip`
- `npm`

It's not all that useful, but it is a good pilot because it spans the full stack and has quantifiable numbers that are easy to verify at the command line.

It took codex 12 minutes to produce this widget through two prompts only.

- [prompt-1 log][logs/codex-20251117-prompt-1.log]
- [prompt-2 log][logs/codex-20251117-prompt-2.log]

## Setup

First, clone the repo itself and install:
```bash
git clone https://github.com/brege/monitorat.git
cd monitorat
pip install .
```

Configure `~/.config/monitor@/config.yaml` to point to the sandbox and enable the widget:
```yaml
paths:
  widgets: /path/to/monitorat/testing/widgets

widgets:
  enabled:
    - packages
    - # other widgets you use
  packages:
    name: System Packages
```

## Testing

Start the server:
```bash
gunicorn --bind localhost:6161 monitorat.monitor:app
```

Access the widget at `http://localhost:6161` and verify the API endpoint:
```bash
curl http://localhost:6161/api/system-packages
```

## Agent

To regenerate this widget, give an agent **prompt.md** and **AGENTS.md** while in monitor@'s source code directory. The agent builds the widget from scratch in `testing/widgets/packages/`.

Use this as an archetype to build out new widgets.

## Deployment

Once satisfied, move the widget to production:
```bash
mv testing/widgets/packages ~/.config/monitor@/widgets/packages
```

Update `~/.config/monitor@/config.yaml` to point to the production location.

