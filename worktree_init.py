"""Initialize a new checkout from Herdr's worktree.created event."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile


def git(root, *args, stdin=None, optional=False):
    result = subprocess.run(
        ["git", "-C", root, *args], input=stdin, stdout=subprocess.PIPE
    )
    if optional and result.returncode == 1:
        return b""
    result.check_returncode()
    return result.stdout


def copy_includes(source, target):
    rules = source / ".worktreeinclude"
    if not rules.is_file():
        return 0
    # Let Git interpret both sets of ignore rules, including ** and negation.
    candidates = git(source, "ls-files", "-z", "--others", "--ignored",
                     "--exclude-from", rules)
    if not candidates:
        return 0
    ignored = git(source, "check-ignore", "-z", "--stdin", stdin=candidates,
                  optional=True)
    copied = 0
    for raw in ignored.split(b"\0"):
        if not raw:
            continue
        relative = Path(os.fsdecode(raw))
        src = source / relative
        dst = target / relative
        if src.resolve() != src or not stat.S_ISREG(src.stat().st_mode):
            continue
        if dst.parent.resolve() != dst.parent or os.path.lexists(dst):
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        # Publish a complete copy without overwriting a concurrently created file.
        with tempfile.NamedTemporaryFile(dir=dst.parent) as tmp:
            shutil.copy2(src, tmp.name)
            try:
                os.link(tmp.name, dst)
            except FileExistsError:
                continue
        copied += 1
    return copied


def main():
    data = json.loads(os.environ["HERDR_PLUGIN_EVENT_JSON"])["data"]
    state = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state")
    log = state / "herdr/worktree-init/runs.log"
    try:
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as stream:
            timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
            print(timestamp, "started", json.dumps(data["worktree"]["path"]), file=stream)
    except OSError as error:
        print(f"Could not write {log}: {error}", file=sys.stderr)
    target = Path(data["worktree"]["path"]).resolve(strict=True)
    source = Path(data["workspace"]["worktree"]["repo_root"]).resolve(strict=True)
    if source == target:
        raise ValueError("source and new worktree paths are identical")
    count = copy_includes(source, target)
    print(f"Copied {count} included file(s) into {target}", flush=True)
    setting = git(source, "config", "--local", "--null", "--get",
                  "herdr.worktreeInitScript", optional=True)
    if setting:
        script = source / os.fsdecode(setting.rstrip(b"\0"))
        subprocess.run([script], cwd=target, check=True)


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, OSError, subprocess.CalledProcessError) as error:
        sys.exit(f"worktree-init: {error}")
