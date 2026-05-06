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
    platforms: [.macOS(.v13)],   // macOS 13+ for MenuBarExtra
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
