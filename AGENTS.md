# Repository Guidelines

## Project structure

`herdr-plugin.toml` registers the `worktree.created` event and invokes `worktree_init.py`. In that module, `main()` reads the Herdr event, logs the run, calls `copy_includes()`, and runs the optional setup script in the new worktree. Update `README.md` when installation, configuration, or hook behavior changes. `INTENT.md` records the original plugin scope.

## Local development

The plugin runs directly from source on Linux and macOS with Python 3.8+, Git, and Herdr 0.7.0 or later.

- Run `herdr plugin link .` from this directory to register the local plugin.
- From a disposable Git project, run `herdr worktree create --cwd "$PWD" --branch try-worktree-init` to trigger the hook. Use a fresh branch name for each run.
- Run `herdr plugin log list --plugin victorhsb.worktree-init` to inspect the hook output.

## Coding style

Use four-space indentation and `snake_case` for Python functions and variables. Follow the existing use of `pathlib.Path` for paths and argument lists for subprocess calls. Keep syntax compatible with Python 3.8. The repository has no configured formatter or linter.

## Testing

Verification is manual. For copy changes, put a dummy file in the source checkout and match it in both `.gitignore` and `.worktreeinclude`. Create a worktree and check the file’s relative path, contents, and mode. Exercise negated patterns, symlinks, and existing destinations when changing file selection. For setup changes, configure `herdr.worktreeInitScript` as described in the README and verify the script can read the copied file from its working directory.

## Commits and pull requests

Use Jujutsu for changes to this repository. Review edits with `jj diff`, then use `jj describe -m "…"` to give the change a concise imperative subject. The initial commit uses “Initialize new Herdr worktrees with local files and a setup script.” In a pull request, describe the behavior change and the worktree scenario you used to verify it.
