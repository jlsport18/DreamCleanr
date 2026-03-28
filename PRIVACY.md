# DreamCleanr Privacy

DreamCleanr is designed to run locally on the user's machine.

## What DreamCleanr touches

- local process lists
- selected cache and storage directories on the local machine
- optional local scheduling via `launchd`
- optional Docker CLI metadata when Docker is installed

## What DreamCleanr does not upload by default

- process inventories
- cleanup reports
- auth material from Claude, Codex, Docker, or other tools
- local session history from `~/.codex`, `~/.claude`, or protected application support directories

## Public Site

The public site is informational and provides install/download guidance. It should not collect telemetry by default unless future product decisions explicitly add analytics with disclosure.

## Protected State

DreamCleanr intentionally avoids auto-deleting:

- `~/.codex`
- `~/.claude`
- the Claude VM bundle
- Docker raw VM storage
- active Codex and Claude support roots when those families are live
