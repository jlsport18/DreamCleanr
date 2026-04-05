import Foundation
import SwiftUI
import DreamCleanrAppleShared

@MainActor
final class ShellSummaryModel: ObservableObject {
    @Published var summary: ReceiptSummary?
    @Published var errorMessage: String?
    @Published var runningCommand = false

    func refresh() {
        do {
            summary = try ReceiptSummaryLoader.load(from: DreamCleanrArtifactPaths.latestSummaryURL())
            errorMessage = nil
        } catch {
            summary = nil
            errorMessage = error.localizedDescription
        }
    }

    func runPreview() {
        runningCommand = true
        errorMessage = nil
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        process.arguments = ["dreamcleanr", "clean", "--mode", "balanced"]
        process.terminationHandler = { [weak self] process in
            DispatchQueue.main.async {
                self?.runningCommand = false
                if process.terminationStatus == 0 {
                    self?.refresh()
                } else {
                    self?.errorMessage = "Preview run failed with status \(process.terminationStatus)."
                }
            }
        }
        do {
            try process.run()
        } catch {
            runningCommand = false
            errorMessage = "Unable to launch DreamCleanr CLI: \(error.localizedDescription)"
        }
    }
}

struct ShellDashboardView: View {
    let summary: ReceiptSummary

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                HStack(spacing: 12) {
                    metricCard(title: "Recoverable", value: summary.heroValueText, caption: summary.dryRun ? "Preview mode" : "Last applied run")
                    metricCard(title: "Free Space", value: summary.freeSpaceText, caption: "Current local headroom")
                    metricCard(title: "Projects", value: "\(summary.projectSummary.activeProjectCount)", caption: "Active project guardrails")
                }

                VStack(alignment: .leading, spacing: 12) {
                    Text("Detector Overview")
                        .font(.headline)
                    ForEach(summary.detectorOverview.prefix(6)) { detector in
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(detector.title)
                                    .font(.subheadline.weight(.semibold))
                                Text("\(detector.pathCount) roots · \(detector.safetyState.replacingOccurrences(of: "_", with: " "))")
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }
                            Spacer()
                            Text(ByteCountFormatter.string(fromByteCount: Int64(detector.totalBytes), countStyle: .file))
                                .foregroundStyle(.secondary)
                        }
                        .padding()
                        .background(Color.white.opacity(0.06), in: RoundedRectangle(cornerRadius: 16))
                    }
                }
            }
            .padding(24)
        }
    }

    private func metricCard(title: String, value: String, caption: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title.uppercased())
                .font(.caption.weight(.semibold))
                .foregroundStyle(.secondary)
            Text(value)
                .font(.title2.weight(.bold))
            Text(caption)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color.white.opacity(0.08), in: RoundedRectangle(cornerRadius: 18))
    }
}

struct ShellHistoryView: View {
    let summary: ReceiptSummary

    var body: some View {
        List {
            Section("Project Signals") {
                ForEach(summary.projectSignals.prefix(10)) { signal in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(signal.root)
                            .font(.subheadline.weight(.semibold))
                        Text(signal.toolchains.joined(separator: ", "))
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }
            Section("Top Storage Targets") {
                ForEach(summary.topStorageTargets.prefix(8)) { target in
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text(target.label)
                            Text(target.classification.replacingOccurrences(of: "_", with: " "))
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                        Spacer()
                        Text(ByteCountFormatter.string(fromByteCount: Int64(target.sizeBytes), countStyle: .file))
                            .foregroundStyle(.secondary)
                    }
                }
            }
        }
        .listStyle(.inset)
    }
}

struct ShellSettingsView: View {
    var body: some View {
        Form {
            LabeledContent("Report Directory", value: DreamCleanrArtifactPaths.reportDirectory().path)
            LabeledContent("Latest Summary", value: DreamCleanrArtifactPaths.latestSummaryURL().lastPathComponent)
            Text("This prototype stays local-first and uses the existing Python CLI for real cleanup work.")
        }
        .padding()
    }
}

struct ShellUpgradeView: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Pro Later")
                .font(.largeTitle.weight(.bold))
            Text("The premium shell phase is about calmer history browsing, guided presets, and richer observability. No live checkout is wired into this prototype.")
                .foregroundStyle(.secondary)
            Spacer()
        }
        .padding(24)
    }
}

struct ShellRootView: View {
    @StateObject private var model = ShellSummaryModel()
    @State private var selection = 0

    var body: some View {
        NavigationSplitView {
            List(selection: $selection) {
                Text("Dashboard").tag(0)
                Text("History").tag(1)
                Text("Settings").tag(2)
                Text("Upgrade").tag(3)
            }
            .navigationTitle("DreamCleanr")
        } detail: {
            Group {
                if let summary = model.summary {
                    switch selection {
                    case 1:
                        ShellHistoryView(summary: summary)
                    case 2:
                        ShellSettingsView()
                    case 3:
                        ShellUpgradeView()
                    default:
                        ShellDashboardView(summary: summary)
                    }
                } else {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("No local summary yet")
                            .font(.largeTitle.weight(.bold))
                        Text(model.errorMessage ?? "Run DreamCleanr once to generate latest-summary.json.")
                            .foregroundStyle(.secondary)
                    }
                    .padding(24)
                }
            }
            .toolbar {
                ToolbarItemGroup {
                    Button("Refresh") {
                        model.refresh()
                    }
                    Button(model.runningCommand ? "Running…" : "Run Preview") {
                        model.runPreview()
                    }
                    .disabled(model.runningCommand)
                }
            }
        }
        .onAppear {
            model.refresh()
        }
        .preferredColorScheme(.dark)
        .frame(minWidth: 1100, minHeight: 760)
    }
}

@main
struct DreamCleanrShellPrototypeApp: App {
    var body: some Scene {
        WindowGroup {
            ShellRootView()
        }
    }
}
