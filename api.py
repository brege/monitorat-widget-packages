#!/usr/bin/env python3
import json
import logging
import subprocess
import threading
from datetime import datetime, timezone

from flask import jsonify, request

from monitor import config, get_data_path

logger = logging.getLogger(__name__)
CACHE_FILE = "packages.json"

PARSERS = {
    "lines": lambda stdout: sum(1 for line in stdout.splitlines() if line.strip()),
    "pip": lambda stdout: len(json.loads(stdout or "[]")),
    "npm": lambda stdout: len((json.loads(stdout or "{}").get("dependencies") or {})),
}
COLLECTORS = [
    ("dnf", ["dnf", "repoquery", "--installed"], PARSERS["lines"]),
    ("pip", ["python3", "-m", "pip", "list", "--format=json"], PARSERS["pip"]),
    ("npm", ["npm", "list", "-g", "--depth=0", "--json"], PARSERS["npm"]),
    ("flatpak", ["flatpak", "list", "--app", "--columns=application"], PARSERS["lines"]),
]

_refresh_thread = None
_refresh_lock = threading.Lock()


def register_routes(app):
    @app.route("/api/system-packages", methods=["GET"])
    def system_packages():
        try:
            widget_conf = config["widgets"]["packages"].get(dict)
        except Exception:
            widget_conf = {}

        payload = _load_cache()

        global _refresh_thread
        if payload["updated"] is None or request.args.get("refresh") == "1":
            with _refresh_lock:
                if not (_refresh_thread and _refresh_thread.is_alive()):
                    _refresh_thread = threading.Thread(
                        target=_refresh_worker, daemon=True
                    )
                    _refresh_thread.start()
            updating = True
        else:
            with _refresh_lock:
                updating = bool(_refresh_thread and _refresh_thread.is_alive())
        payload["updating"] = updating
        payload["refresh_seconds"] = widget_conf.get("refresh_seconds", 5)
        return jsonify(payload)


def _load_cache():
    path = get_data_path() / CACHE_FILE
    if not path.exists():
        return {"packages": {}, "updated": None}

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
            data.setdefault("packages", {})
            data.setdefault("updated", None)
            return data
    except Exception as exc:  # pragma: no cover - best-effort
        logger.warning("Unable to read packages cache: %s", exc)
        return {"packages": {}, "updated": None}


def _refresh_worker():
    try:
        packages = {
            name: _run_collector(name, command, parser)
            for name, command, parser in COLLECTORS
        }
        payload = {
            "packages": packages,
            "updated": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        path = get_data_path() / CACHE_FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle)
    except Exception as exc:  # pragma: no cover - best-effort
        logger.error("packages refresh failed: %s", exc)


def _run_collector(name, command, parser):
    info = {"count": 0}
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=60
        )
        if completed.returncode != 0:
            info["error"] = completed.stderr.strip() or f"exit {completed.returncode}"
        else:
            info["count"] = parser(completed.stdout)
    except FileNotFoundError:
        info["error"] = "command not found"
    except subprocess.TimeoutExpired:
        info["error"] = "timed out"
    except json.JSONDecodeError:
        info["error"] = "invalid JSON"
    except Exception as exc:  # pragma: no cover - best-effort
        info["error"] = str(exc)
    return info
