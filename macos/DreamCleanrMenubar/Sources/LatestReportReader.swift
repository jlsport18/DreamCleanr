// LatestReportReader — surfaces the most-recent DreamCleanr cleanup
// receipt in the menu bar without re-running the CLI.
//
// Reads ~/Library/Logs/DreamCleanr/reports/latest-summary.json (written
// by the Python CLI on every clean / scan with --apply) and parses the
// headline numbers: storage reclaimed, RAM reclaimed, finished_at.
//
// Per AGENTS.md: the macOS shell wraps the CLI and never duplicates
// cleanup logic. This file is read-only — it consumes receipts the
// CLI produced.
//
// Per issue #2 — first shipping slice (read receipts; render in menu).

import Foundation

/// Snapshot of the most recent DreamCleanr cleanup, parsed from disk.
struct LatestReportSummary {
    let runId: String
    let finishedAt: String          // ISO 8601 from the CLI
    let storageReclaimedBytes: Int  // disk-only — does NOT include trashed bytes
    let memoryReclaimedMb: Double   // RAM (process termination + model unload)
    let processesTrimmed: Int
    let objectsPruned: Int
    let mode: String                // safe | balanced | max
    let dryRun: Bool

    /// One-line human summary suitable for the menu.
    var menuLine: String {
        if dryRun {
            return "Preview: would reclaim \(humanBytes(storageReclaimedBytes)) disk, \(formatMb(memoryReclaimedMb)) RAM"
        }
        return "Last clean: \(humanBytes(storageReclaimedBytes)) disk + \(formatMb(memoryReclaimedMb)) RAM"
    }

    /// Detailed second line.
    var subline: String {
        "\(processesTrimmed) procs · \(objectsPruned) objects · \(mode)"
    }
}

actor LatestReportReader {
    static let shared = LatestReportReader()

    private static func summaryPath() -> URL {
        let home = FileManager.default.homeDirectoryForCurrentUser
        return home
            .appendingPathComponent("Library", isDirectory: true)
            .appendingPathComponent("Logs", isDirectory: true)
            .appendingPathComponent("DreamCleanr", isDirectory: true)
            .appendingPathComponent("reports", isDirectory: true)
            .appendingPathComponent("latest-summary.json")
    }

    /// Read the latest cleanup summary. Returns nil if no report exists yet
    /// or the file is malformed (CLI may have written a partial file mid-run).
    func read() -> LatestReportSummary? {
        let path = Self.summaryPath()
        guard FileManager.default.fileExists(atPath: path.path),
              let data = try? Data(contentsOf: path),
              let raw = try? JSONSerialization.jsonObject(with: data) as? [String: Any]
        else { return nil }

        // The CLI writes both the report and a summary; the summary has
        // pre-rolled-up numbers. Tolerate either shape — fall back to
        // the report fields if the summary keys aren't present.
        let storage = (raw["storage_reclaimed_bytes"] as? Int)
            ?? (raw["report"] as? [String: Any]).flatMap { $0["storage_reclaimed_bytes"] as? Int }
            ?? 0
        let memMb = (raw["memory_reclaimed_estimate_mb"] as? Double)
            ?? (raw["report"] as? [String: Any]).flatMap { $0["memory_reclaimed_estimate_mb"] as? Double }
            ?? 0.0
        let trimmed = (raw["processes_trimmed"] as? Int) ?? 0
        let pruned = (raw["objects_pruned"] as? Int) ?? 0
        let mode = (raw["mode"] as? String) ?? "balanced"
        let dryRun = (raw["dry_run"] as? Bool) ?? false
        let runId = (raw["run_id"] as? String) ?? "unknown"
        let finishedAt = (raw["finished_at"] as? String) ?? ""

        return LatestReportSummary(
            runId: runId,
            finishedAt: finishedAt,
            storageReclaimedBytes: storage,
            memoryReclaimedMb: memMb,
            processesTrimmed: trimmed,
            objectsPruned: pruned,
            mode: mode,
            dryRun: dryRun
        )
    }
}

// MARK: - Formatting helpers (kept local so the file is self-contained)

/// Human-readable bytes (1.4 GB, 512 MB, 128 KB).
func humanBytes(_ n: Int) -> String {
    guard n > 0 else { return "0 B" }
    let units = ["B", "KB", "MB", "GB", "TB"]
    var v = Double(n)
    var i = 0
    while v >= 1024 && i < units.count - 1 {
        v /= 1024
        i += 1
    }
    if i == 0 {
        return "\(Int(v)) \(units[i])"
    }
    return String(format: "%.1f %@", v, units[i])
}

/// MB formatter that drops the decimal when it's a clean integer.
func formatMb(_ mb: Double) -> String {
    if mb == 0 { return "0 MB" }
    if mb.truncatingRemainder(dividingBy: 1) == 0 {
        return "\(Int(mb)) MB"
    }
    return String(format: "%.1f MB", mb)
}
