# Herdr Worktree Init

When Herdr creates a Git worktree, this plugin copies selected local files from the main checkout and then runs an optional setup script in the new worktree. You can use either feature independently.

## Install

With Herdr, Git, and Python 3.8+ on Linux or macOS, run this from the plugin directory:

```sh
herdr plugin link .
```

## Include local files

In your project's main checkout, create a root-level `.worktreeinclude` using Git ignore patterns. For example:

```gitignore
/.env.local
/config/*.secret
!/config/example.secret
```

The plugin copies regular files that Git ignores and that match the include rules. It preserves relative paths, file modes, and existing destination files. It skips symbolic links. Matching uses Git directly, including for patterns inside ignored directories. Claude Code has additional traversal rules for leading `**/` patterns inside ignored directories. [Claude Code worktree documentation](https://code.claude.com/docs/en/worktrees#copy-gitignored-files-into-worktrees)

## Configure a setup script

From the project repository, point its local Git configuration at an executable script:

```sh
chmod +x scripts/worktree-init.sh
git config --local herdr.worktreeInitScript scripts/worktree-init.sh
```

Use a script with a shebang. Relative paths select a script in the main checkout. Absolute paths also work. The script's working directory is the new checkout, so a command such as `npm ci` installs dependencies there. To disable the script, run `git config --local --unset herdr.worktreeInitScript`.

## Try it

From the project repository, create a worktree and check the hook's output:

```sh
herdr worktree create --cwd "$PWD" --branch try-worktree-init
herdr plugin log list --plugin victorhsb.worktree-init
```

Each worktree creation appends its UTC start time and checkout path to a local log, even when there are no files to copy or the setup script later fails. To see the most recent run:

```sh
tail -n 1 "${XDG_STATE_HOME:-$HOME/.local/state}/herdr/worktree-init/runs.log"
```

Herdr dispatches the hook after creation. Reopening an existing worktree does not trigger setup. If copying or setup fails, the hook exits with an error and the worktree remains available. [Herdr plugin documentation](https://herdr.dev/tui/docs/plugins/)
