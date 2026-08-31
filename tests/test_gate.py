"""Pro gate tests.

The gate is the piece that was missing entirely: check_pro() existed but
nothing ever called it, so even the old licence was unenforced.

Note on the assertion style: apply_actions() is always invoked — it takes a
dry_run flag rather than being skipped — so these tests assert on that flag,
not on whether the function ran.
"""

import argparse

import pytest

from dreamcleanr import cli


def _clean_args(**kw):
    base = dict(
        apply=True, mode="safe", scope="storage", yes=True, trash=None,
        output_dir=None, json_out=None, html_out=None, open=False,
        retention_count=3,
    )
    base.update(kw)
    return argparse.Namespace(**base)


# ── the gate helper ──────────────────────────────────────────────────────────


def test_helper_blocks_and_downgrades_when_unlicensed(monkeypatch, capsys):
    monkeypatch.setattr(cli, "check_pro", lambda: False)
    args = _clean_args()
    assert cli._requires_pro_or_downgrade(args) is False
    assert args.apply is False, "must force the run back to dry-run"
    assert "6.99" in capsys.readouterr().out


def test_helper_allows_when_licensed(monkeypatch):
    monkeypatch.setattr(cli, "check_pro", lambda: True)
    args = _clean_args()
    assert cli._requires_pro_or_downgrade(args) is True
    assert args.apply is True, "a licensed run must stay an apply"


def test_upgrade_message_names_the_price_and_the_activate_command():
    assert "$6.99" in cli.UPGRADE_MESSAGE
    assert "license activate" in cli.UPGRADE_MESSAGE
    # Guard against the five stale prices the site used to show.
    for stale in ("$4.99", "$24", "$29", "$49", "$29.99", "$49.99"):
        assert stale not in cli.UPGRADE_MESSAGE


# ── clean --apply ────────────────────────────────────────────────────────────


def test_clean_apply_is_forced_to_dry_run_when_unlicensed(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cli, "check_pro", lambda: False)
    seen = {}

    def _spy(before, actions, dry_run=True, trash=False):
        seen["dry_run"] = dry_run
        return []

    monkeypatch.setattr(cli, "apply_actions", _spy)
    rc = cli.command_clean(_clean_args(output_dir=str(tmp_path)))

    assert rc == 0, "unlicensed --apply must not error; the dry-run report is still useful"
    assert seen.get("dry_run") is True, "unlicensed run MUST stay dry"
    assert "6.99" in capsys.readouterr().out


def test_clean_apply_actually_applies_when_licensed(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "check_pro", lambda: True)
    seen = {}

    def _spy(before, actions, dry_run=True, trash=False):
        seen["dry_run"] = dry_run
        return []

    monkeypatch.setattr(cli, "apply_actions", _spy)
    cli.command_clean(_clean_args(output_dir=str(tmp_path)))
    assert seen.get("dry_run") is False, "licensed --apply must really apply"


def test_clean_without_apply_never_consults_the_licence(monkeypatch, tmp_path):
    """A free dry-run must not be gated, nor pay the cost of a licence check."""
    def _boom():
        raise AssertionError("check_pro must not be called for a plain dry-run")

    monkeypatch.setattr(cli, "check_pro", _boom)
    monkeypatch.setattr(cli, "apply_actions", lambda *a, **k: [])
    assert cli.command_clean(_clean_args(apply=False, output_dir=str(tmp_path))) == 0


# ── schedule ─────────────────────────────────────────────────────────────────


def test_schedule_install_refuses_without_licence(monkeypatch, capsys):
    monkeypatch.setattr(cli, "check_pro", lambda: False)
    installed = {}
    monkeypatch.setattr(cli, "install_launch_agent",
                        lambda *a, **k: installed.setdefault("ran", True))
    args = argparse.Namespace(output_dir=None, hour=3, minute=0, mode="safe",
                              retention_count=3)
    rc = cli.command_schedule_install(args)
    assert rc != 0, "must fail loudly — unlike clean, there is no useful partial result"
    assert "ran" not in installed, "LaunchAgent must NOT be installed"
    assert "6.99" in capsys.readouterr().out
