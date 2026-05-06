// DreamCleanrMenubar — entry point. SwiftUI MenuBarExtra app.
//
// Responsibilities:
//   - Render menu bar icon (color reflects disk pressure)
//   - Expose Scan / Clean / Open Reports / Schedule menu items
//   - Run dreamcleanr CLI subprocesses with argument allowlist (security)
//   - Refresh disk-pressure indicator every 60s in the background
//   - Sparkle auto-update on launch + every 24h
//
// Security model: this app NEVER reads file contents — it only invokes
// the dreamcleanr CLI which is what actually makes filesystem decisions.
// All cleanup operations stay in the CLI's safety model (dry-run by
// default, protected paths refuse to be touched, etc.).

import SwiftUI
import Sparkle

@main
struct DreamCleanrMenubarApp: App {
    @StateObject private var diskMonitor = DiskPressureMonitor()
    @StateObject private var scheduleState = ScheduleState()
    private let updaterController: SPUStandardUpdaterController

    init() {
        // Sparkle: standard updater with default user driver.
        // Appcast URL configured in Info.plist via SUFeedURL.
        updaterController = SPUStandardUpdaterController(
            startingUpdater: true,
            updaterDelegate: nil,
            userDriverDelegate: nil
        )
    }

    var body: some Scene {
        MenuBarExtra {
            MenuBarContent(
                diskMonitor: diskMonitor,
                scheduleState: scheduleState,
                updater: updaterController.updater
            )
        } label: {
            Image(systemName: diskMonitor.symbolName)
                .symbolRenderingMode(.palette)
                .foregroundStyle(diskMonitor.tint, .secondary)
        }
        .menuBarExtraStyle(.menu)
    }
}

struct MenuBarContent: View {
    @ObservedObject var diskMonitor: DiskPressureMonitor
    @ObservedObject var scheduleState: ScheduleState
    let updater: SPUUpdater

    @State private var lastScanResult: String? = nil
    @State private var isWorking: Bool = false

    var body: some View {
        // Status row
        Text(diskMonitor.statusText)
            .font(.system(size: 12, weight: .medium))

        Divider()

        // Actions
        Button("Scan now") {
            Task { await runCli(["scan"]) }
        }
        .disabled(isWorking)
        .keyboardShortcut("s")

        Button("Clean now (balanced, dry-run)") {
            Task { await runCli(["clean", "--mode=balanced"]) }
        }
        .disabled(isWorking)

        Button("Apply last cleanup") {
            Task { await runCli(["clean", "--mode=balanced", "--apply"]) }
        }
        .disabled(isWorking)
        .keyboardShortcut("c", modifiers: [.command, .shift])

        Divider()

        // Schedule toggle
        Toggle(isOn: $scheduleState.installed) {
            Text("Daily background cleanup at 3:30am")
        }
        .onChange(of: scheduleState.installed) { _, newValue in
            Task {
                await runCli([newValue ? "schedule" : "schedule", newValue ? "install" : "uninstall"])
            }
        }

        Divider()

        // Open reports
        Button("Open last report") {
            openReportsFolder()
        }

        Button("Open changelog") {
            NSWorkspace.shared.open(URL(string: "https://dreamcleanr.jonlynchfinancial.com/changelog/")!)
        }

        Button("Open docs") {
            NSWorkspace.shared.open(URL(string: "https://dreamcleanr.jonlynchfinancial.com/docs/")!)
        }

        Divider()

        // Updates
        Button("Check for updates…") {
            updater.checkForUpdates()
        }

        Button("Quit DreamCleanr") {
            NSApp.terminate(nil)
        }
        .keyboardShortcut("q")

        if let result = lastScanResult {
            Divider()
            Text(result).font(.caption2).foregroundColor(.secondary)
        }
    }

    private func runCli(_ args: [String]) async {
        isWorking = true
        defer { isWorking = false }
        let result = await CliRunner.shared.run(args)
        lastScanResult = result
        diskMonitor.refresh()
    }

    private func openReportsFolder() {
        let url = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Library/Logs/DreamCleanr/reports", isDirectory: true)
        NSWorkspace.shared.open(url)
    }
}
