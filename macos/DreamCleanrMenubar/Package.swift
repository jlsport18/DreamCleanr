// swift-tools-version: 5.9
// DreamCleanr Menubar — native macOS frontend on top of the Python CLI.
//
// Wraps `dreamcleanr` shell calls in a SwiftUI MenuBarExtra app. Surfaces:
//   - Live disk-pressure indicator in the menu bar (icon changes color)
//   - Quick "Scan now" / "Clean now (balanced)" / "Open last report"
//   - Scheduled-cleanup toggle (wraps `dreamcleanr schedule install/uninstall`)
//   - "Open Reports folder" → opens ~/Library/Logs/DreamCleanr/reports/ in Finder
//
// Distribution: signed + notarized DMG outside the Mac App Store first.
// Sparkle for in-app auto-updates. Requires the dreamcleanr CLI in PATH
// (the curl|bash installer puts it at ~/.local/bin/dreamcleanr).

import PackageDescription

let package = Package(
    name: "DreamCleanrMenubar",
    // macOS 14+ — for the two-arg `.onChange(of:_:)` closure used in the
    // schedule-toggle. Pre-existing code already used this API; bumping the
    // declared minimum to match what the code requires. macOS 14 shipped
    // 2023-09, well within the AI-dev support window.
    platforms: [.macOS(.v14)],
    products: [
        .executable(name: "DreamCleanrMenubar", targets: ["DreamCleanrMenubar"])
    ],
    dependencies: [
        // Sparkle for auto-update (signed appcasts)
        .package(url: "https://github.com/sparkle-project/Sparkle", from: "2.6.0"),
    ],
    targets: [
        .executableTarget(
            name: "DreamCleanrMenubar",
            dependencies: [
                .product(name: "Sparkle", package: "Sparkle"),
            ],
            path: "Sources",
            resources: [
                .process("Resources"),
            ]
        ),
        .testTarget(
            name: "DreamCleanrMenubarTests",
            dependencies: ["DreamCleanrMenubar"],
            path: "Tests"
        ),
    ]
)
