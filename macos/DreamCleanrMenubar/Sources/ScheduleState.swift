// ScheduleState — observes the macOS LaunchAgent state for daily
// background cleanup. Reads `launchctl list` to determine if
// `com.jlfg.dreamcleanr` is currently registered.

import Foundation
import SwiftUI

@MainActor
final class ScheduleState: ObservableObject {
    @Published var installed: Bool = false {
        didSet {
            // Avoid CLI invocation when refreshed from observed state
            // — the App.swift layer triggers `dreamcleanr schedule install/uninstall`
            // on user toggle.
        }
    }

    init() {
        Task { await refresh() }
    }

    func refresh() async {
        let result = await runLaunchctl(["list", "com.jlfg.dreamcleanr"])
        // launchctl exits 0 if the agent IS loaded, non-zero otherwise
        installed = result.contains("\"PID\"") || result.contains("PID")
    }

    private func runLaunchctl(_ args: [String]) async -> String {
        await withCheckedContinuation { (cont: CheckedContinuation<String, Never>) in
            let task = Process()
            task.launchPath = "/bin/launchctl"
            task.arguments = args
            let pipe = Pipe()
            task.standardOutput = pipe
            task.standardError = pipe
            task.terminationHandler = { _ in
                let data = pipe.fileHandleForReading.readDataToEndOfFile()
                cont.resume(returning: String(data: data, encoding: .utf8) ?? "")
            }
            do { try task.run() }
            catch { cont.resume(returning: "") }
        }
    }
}
