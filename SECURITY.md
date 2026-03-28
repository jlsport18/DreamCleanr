# Security Policy

## Supported Versions

The latest tagged release on `main` receives fixes first.

## Reporting a Vulnerability

Please do not open a public issue for a credential leak, unsafe deletion path, or destructive cleanup bug.

Instead:

- email the maintainer directly if you have a private contact path
- or open a private advisory through GitHub Security Advisories when enabled

## Safety Principles

- preview-first behavior stays the default
- protected Claude, Codex, and Docker VM state must never be auto-deleted
- new cleanup targets require regression coverage before release
