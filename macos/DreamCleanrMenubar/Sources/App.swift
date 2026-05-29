// DreamCleanrMenubar — entry point. SwiftUI MenuBarExtra app.
//
// Responsibilities:
//   - Render menu bar icon (color reflects disk pressure)
//   - Expose Scan / Clean / Open Reports / Schedule menu items
//   - Show last cleanup's actual outcome inline (LatestReportReader)
//   - Show a submenu of recent reports — click to open the HTML receipt
//   - Run dreamcleanr CLI subprocesses with argument allowlist (security)
//   - Refresh disk-pressure indicator every 60s in the background
//   - Sparkle auto-update on launch + every 24h (Info.plist SUFeedURL)
//
// Security model: this app NEVER reads file contents (other than its own
// receipts on disk) — it only invokes the dreamcleanr CLI which is what
// actually makes filesystem decisions. All cleanup operations stay in
// the CLI's safety model (dry-run by default, protected paths refuse to
// be touched, etc.).

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
    @State private var latestReport: LatestReportSummary? = nil
    @State private var recentReports: [ReportEntry] = []

    var body: some View {
        Group {
            // Status row
            Text(diskMonitor.statusText)
                .font(.system(size: 12, weight: .medium))

            // Latest receipt — shows the last cleanup's actual outcome
            // without re-running the CLI. Loaded on .task; updates on
            // every CLI run via runCli().
            if let r = latestReport {
                Text(r.menuLine)
                    .font(.system(size: 11))
                Text(r.subline)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }

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
                    await runCli(["schedule", newValue ? "install" : "uninstall"])
                }
            }

            Divider()

            // Recent reports — submenu lists the last 5 HTML receipts.
            // Each click opens the receipt in the default browser (file://).
            // No reports yet → menu shows nothing under this item.
            Menu("Recent reports") {
                if recentReports.isEmpty {
                    Text("No reports yet — run a Scan or Clean.")
                        .foregroundColor(.secondary)
                } else {
                    ForEach(recentReports) { entry in
                        Button(entry.menuLabel) {
                            openReport(entry)
                        }
                    }
                    Divider()
                    Button("Open reports folder…") {
                        openReportsFolder()
                    }
                }
            }

            // Quick action — opens the single latest HTML receipt directly.
            Button("Open last report") {
                Task { await openLatestReport() }
            }
            .keyboardShortcut("r", modifiers: [.command])

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
        .task {
            await refreshFromDisk()
        }
    }

    // MARK: - CLI + receipt refresh

    private func runCli(_ args: [String]) async {
        isWorking = true
        defer { isWorking = false }
        let result = await CliRunner.shared.run(args)
        lastScanResult = result
        diskMonitor.refresh()
        await refreshFromDisk()
    }

    /// Refresh latestReport + recentReports from the on-disk receipt dir.
    /// Called on view appear AND after every CLI run.
    private func refreshFromDisk() async {
        latestReport = await LatestReportReader.shared.read()
        recentReports = await ReportsHistoryReader.shared.recent(limit: 5)
    }

    // MARK: - Open helpers

    /// Open the single most-recent HTML receipt. Falls back to the folder
    /// when no HTML report has been produced yet.
    private func openLatestReport() async {
        let url = await ReportsHistoryReader.shared.latestHTMLOrFolder()
        NSWorkspace.shared.open(url)
    }

    /// Open a specific receipt — prefers the HTML, falls back to the JSON
    /// (which most browsers will pretty-print).
    private func openReport(_ entry: ReportEntry) {
        NSWorkspace.shared.open(entry.htmlURL ?? entry.jsonURL)
    }

    private func openReportsFolder() {
        let url = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Library/Logs/DreamCleanr/reports", isDirectory: true)
        NSWorkspace.shared.open(url)
    }
}
