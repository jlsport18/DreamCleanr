// ReportsHistoryReader — lists recent DreamCleanr cleanup receipts so the
// menu bar can show a "Recent reports" submenu and open any of them in
// the browser at file://.
//
// Per AGENTS.md the macOS shell wraps the CLI; this file is read-only
// over the CLI's receipt directory. Pairs with LatestReportReader.swift
// (single most-recent) for the menu's headline row.

import Foundation

/// A single past cleanup report — enough to identify + open it.
struct ReportEntry: Identifiable {
    let id: String          // run_id portion of the filename (unique per run)
    let date: Date          // parsed from the file's mtime
    let htmlURL: URL?       // file://… to the .html receipt; nil if missing
    let jsonURL: URL        // file://… to the .json receipt
    let storageReclaimedBytes: Int   // parsed lazily from the json header
    let memoryReclaimedMb: Double

    /// One-line label for a menu item — `2026-05-28 · 1.4 GB disk`.
    var menuLabel: String {
        let f = DateFormatter()
        f.dateFormat = "yyyy-MM-dd HH:mm"
        let when = f.string(from: date)
        if storageReclaimedBytes == 0 && memoryReclaimedMb == 0 {
            return when
        }
        let parts: [String] = [
            storageReclaimedBytes > 0 ? "\(humanBytes(storageReclaimedBytes)) disk" : "",
            memoryReclaimedMb > 0 ? "\(formatMb(memoryReclaimedMb)) RAM" : "",
        ].filter { !$0.isEmpty }
        return parts.isEmpty ? when : "\(when) · \(parts.joined(separator: " + "))"
    }
}

actor ReportsHistoryReader {
    static let shared = ReportsHistoryReader()

    /// Where the CLI writes receipts.
    private static func reportsDir() -> URL {
        let home = FileManager.default.homeDirectoryForCurrentUser
        return home
            .appendingPathComponent("Library", isDirectory: true)
            .appendingPathComponent("Logs", isDirectory: true)
            .appendingPathComponent("DreamCleanr", isDirectory: true)
            .appendingPathComponent("reports", isDirectory: true)
    }

    /// The CLI writes `report-<TS>-<RUNID>.json` next to `report-<TS>-<RUNID>.html`.
    /// Pair them up; return the latest `limit` entries newest-first.
    func recent(limit: Int = 5) -> [ReportEntry] {
        let dir = Self.reportsDir()
        guard let urls = try? FileManager.default.contentsOfDirectory(
            at: dir,
            includingPropertiesForKeys: [.contentModificationDateKey],
            options: [.skipsHiddenFiles]
        ) else { return [] }

        let jsons = urls
            .filter { $0.lastPathComponent.hasPrefix("report-") && $0.pathExtension == "json" }
            // newest first
            .sorted { a, b in (mtime(a) ?? .distantPast) > (mtime(b) ?? .distantPast) }

        return jsons.prefix(limit).compactMap { jsonURL -> ReportEntry? in
            let stem = jsonURL.deletingPathExtension().lastPathComponent      // report-20260528-abc
            let runId = stem.replacingOccurrences(of: "report-", with: "")    // 20260528-abc
            let htmlURL = jsonURL.deletingPathExtension().appendingPathExtension("html")
            let html: URL? = FileManager.default.fileExists(atPath: htmlURL.path) ? htmlURL : nil
            let when = mtime(jsonURL) ?? Date()

            // Parse headline numbers cheaply — tolerate missing keys.
            var storage = 0
            var memMb = 0.0
            if let data = try? Data(contentsOf: jsonURL),
               let raw = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
                storage = (raw["storage_reclaimed_bytes"] as? Int) ?? 0
                memMb = (raw["memory_reclaimed_estimate_mb"] as? Double) ?? 0
            }

            return ReportEntry(
                id: runId,
                date: when,
                htmlURL: html,
                jsonURL: jsonURL,
                storageReclaimedBytes: storage,
                memoryReclaimedMb: memMb
            )
        }
    }

    /// The single most-recent HTML receipt — used by the "Open last report"
    /// button. Falls back to the reports folder when no HTML exists yet.
    func latestHTMLOrFolder() -> URL {
        let dir = Self.reportsDir()
        if let first = recent(limit: 1).first, let html = first.htmlURL {
            return html
        }
        return dir
    }

    private func mtime(_ url: URL) -> Date? {
        (try? url.resourceValues(forKeys: [.contentModificationDateKey])
              .contentModificationDate)
    }
}
