// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "DreamCleanrApple",
    platforms: [
        .macOS(.v14),
        .iOS(.v17),
    ],
    products: [
        .library(name: "DreamCleanrAppleShared", targets: ["DreamCleanrAppleShared"]),
        .library(name: "DreamCleanrCompanionKit", targets: ["DreamCleanrCompanionKit"]),
        .executable(name: "DreamCleanrShellPrototype", targets: ["DreamCleanrShellPrototype"]),
    ],
    targets: [
        .target(name: "DreamCleanrAppleShared"),
        .target(
            name: "DreamCleanrCompanionKit",
            dependencies: ["DreamCleanrAppleShared"]
        ),
        .executableTarget(
            name: "DreamCleanrShellPrototype",
            dependencies: ["DreamCleanrAppleShared"]
        ),
    ]
)
