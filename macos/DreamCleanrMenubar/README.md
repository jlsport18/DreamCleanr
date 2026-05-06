# DreamCleanr Menubar (macOS)

Native SwiftUI menu-bar frontend on top of the `dreamcleanr` CLI.

## Status

**v0.1.0 scaffold** — committed 2026-05-06. Builds cleanly via Swift Package Manager once Xcode 15+ is available; not yet signed/notarized for distribution.

## What it does

- Live disk-pressure indicator in the menu bar (icon color: green/orange/red)
- Quick actions: **Scan now**, **Clean (dry-run)**, **Apply last cleanup**, **Open last report**
- Toggle for daily background cleanup (wraps `dreamcleanr schedule install/uninstall`)
- Sparkle in-app updates from `https://dreamcleanr.jonlynchfinancial.com/appcast.xml`
- One-click jumps to the .com docs and changelog

## Architecture

- `App.swift` — `MenuBarExtra` SwiftUI app entry point
- `CliRunner.swift` — actor that subprocess-invokes the `dreamcleanr` CLI with strict argument allowlisting
- `DiskPressureMonitor.swift` — `@MainActor ObservableObject` polling free-disk-space every 60s
- `ScheduleState.swift` — observes `launchctl list com.jlfg.dreamcleanr` to reflect schedule install state
- `Info.plist` — `LSUIElement=true` (no Dock icon), Sparkle keys

## Build (when ready to ship)

```bash
cd macos/DreamCleanrMenubar
swift build -c release
# Then sign + notarize with your Apple Developer ID:
codesign --force --options=runtime --sign "Developer ID Application: Jon Lynch (TEAMID)" .build/release/DreamCleanrMenubar
xcrun notarytool submit DreamCleanrMenubar.zip --keychain-profile "AC_PASSWORD" --wait
xcrun stapler staple DreamCleanrMenubar.app
# Package as DMG with create-dmg
```

## Distribution roadmap

1. **Phase A**: Signed + notarized DMG hosted at `https://dreamcleanr.jonlynchfinancial.com/releases/DreamCleanrMenubar-0.1.0.dmg`
2. **Phase B**: Sparkle-driven auto-updates from `appcast.xml` on the .com
3. **Phase C**: Mac App Store submission (once UX is mature + sandbox-compatible — CLI subprocess invocation may need review for App Store entitlements)

## Keys/secrets needed before first release

- Apple Developer ID Application certificate (in Keychain)
- App-specific password for `xcrun notarytool` (set as `AC_PASSWORD` keychain entry)
- Sparkle ED25519 private key + matching `SUPublicEDKey` in Info.plist (replace placeholder)
- `appcast.xml` template + signing tooling

## Why ship this

The current DreamCleanr surface is CLI-only (open-source) + a marketing
site. A native menu-bar app:
- Lowers the activation barrier ("install + tick a checkbox" vs "remember a CLI")
- Surfaces value continuously (the colored icon in the menu bar = ambient awareness of disk pressure)
- Justifies the Pro tier ($29/mo) — the GUI features can be tier-gated
- Proves we ship native macOS, not just web — important brand signal for a developer-tools product
