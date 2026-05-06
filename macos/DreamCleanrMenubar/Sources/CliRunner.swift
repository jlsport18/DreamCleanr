// CliRunner — invokes the dreamcleanr CLI as a subprocess with strict
// argument allowlisting.
//
// Security: the GUI never executes arbitrary args; only commands from
// ALLOWED_COMMANDS pass through. This prevents a future-rogue UI bug
// from invoking unintended subcommands.

import Foundation

actor CliRunner {
    static let shared = CliRunner()

    /// Allowlisted subcommand prefixes. The first arg MUST start one of these.
    private static let allowedCommands: Set<String> = [
        "scan", "clean", "schedule", "report", "export", "--version",
    ]

    /// Allowlisted flag patterns. Each non-positional arg is checked.
    private static let allowedFlagPrefixes: [String] = [
        "--mode=", "--scope=", "--apply", "--dry-run", "install", "uninstall",
    ]

    private static func cliPath() -> String {
        // 1. PATH lookup
        if let p = which("dreamcleanr") { return p }
        // 2. Fallback: ~/.local/bin/dreamcleanr (curl installer default)
        let local = NSString(string: "~/.local/bin/dreamcleanr").expandingTildeInPath
        if FileManager.default.isExecutableFile(atPath: local) { return local }
        return "dreamcleanr"  // best-effort; will surface error
    }

    private static func which(_ binary: String) -> String? {
        let task = Process()
        task.launchPath = "/usr/bin/which"
        task.arguments = [binary]
        let pipe = Pipe()
        task.standardOutput = pipe
        task.standardError = Pipe()
        do {
            try task.run()
            task.waitUntilExit()
            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            let s = String(data: data, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines)
            return s?.isEmpty == false ? s : nil
        } catch {
            return nil
        }
    }

    private static func validate(_ args: [String]) -> Bool {
        guard let first = args.first, allowedCommands.contains(first) else { return false }
        for arg in args.dropFirst() {
            if arg.hasPrefix("-") {
                if !allowedFlagPrefixes.contains(where: { arg.hasPrefix($0) }) { return false }
            } else {
                // Positional arg like 'install' / 'uninstall' for `schedule`
                if !allowedFlagPrefixes.contains(arg) { return false }
            }
        }
        return true
    }

    /// Run the dreamcleanr CLI with `args`. Returns combined stdout/stderr.
    func run(_ args: [String]) async -> String {
        guard Self.validate(args) else {
            return "✗ Refused to run — args not on allowlist: \(args.joined(separator: " "))"
        }
        return await withCheckedContinuation { continuation in
            let task = Process()
            task.launchPath = Self.cliPath()
            task.arguments = args
            let pipe = Pipe()
            task.standardOutput = pipe
            task.standardError = pipe
            task.terminationHandler = { _ in
                let data = pipe.fileHandleForReading.readDataToEndOfFile()
                let s = String(data: data, encoding: .utf8) ?? "(no output)"
                continuation.resume(returning: s.trimmingCharacters(in: .whitespacesAndNewlines))
            }
            do {
                try task.run()
            } catch {
                continuation.resume(returning: "✗ Failed to start dreamcleanr: \(error)")
            }
        }
    }
}
