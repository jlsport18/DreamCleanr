import Foundation

public struct ReceiptSummary: Codable, Sendable {
    public let summaryVersion: Int
    public let runID: String
    public let finishedAt: String
    public let mode: String
    public let dryRun: Bool
    public let storageReclaimedBytes: Int
    public let freeSpaceBytes: Int
    public let processesTrimmed: Int
    public let objectsPruned: Int
    public let familyOverview: [String: FamilyOverview]
    public let detectorOverview: [DetectorOverview]
    public let projectSummary: ProjectSummary
    public let projectSignals: [ProjectSignal]
    public let topStorageTargets: [StorageTarget]

    enum CodingKeys: String, CodingKey {
        case summaryVersion = "summary_version"
        case runID = "run_id"
        case finishedAt = "finished_at"
        case mode
        case dryRun = "dry_run"
        case storageReclaimedBytes = "storage_reclaimed_bytes"
        case freeSpaceBytes = "free_space_bytes"
        case processesTrimmed = "processes_trimmed"
        case objectsPruned = "objects_pruned"
        case familyOverview = "family_overview"
        case detectorOverview = "detector_overview"
        case projectSummary = "project_summary"
        case projectSignals = "project_signals"
        case topStorageTargets = "top_storage_targets"
    }

    public var heroValueText: String {
        ByteCountFormatter.string(fromByteCount: Int64(storageReclaimedBytes), countStyle: .file)
    }

    public var freeSpaceText: String {
        ByteCountFormatter.string(fromByteCount: Int64(freeSpaceBytes), countStyle: .file)
    }
}

public struct FamilyOverview: Codable, Sendable {
    public let state: String
    public let recommendedAction: String
    public let stale: Int
    public let bytesReclaimed: Int

    enum CodingKeys: String, CodingKey {
        case state
        case recommendedAction = "recommended_action"
        case stale
        case bytesReclaimed = "bytes_reclaimed"
    }
}

public struct DetectorOverview: Codable, Sendable, Identifiable {
    public let key: String
    public let title: String
    public let totalBytes: Int
    public let pathCount: Int
    public let safetyState: String
    public let activeProjectCount: Int

    public var id: String { key }

    enum CodingKeys: String, CodingKey {
        case key
        case title
        case totalBytes = "total_bytes"
        case pathCount = "path_count"
        case safetyState = "safety_state"
        case activeProjectCount = "active_project_count"
    }
}

public struct ProjectSummary: Codable, Sendable {
    public let activeProjectCount: Int
    public let toolchainCounts: [String: Int]

    enum CodingKeys: String, CodingKey {
        case activeProjectCount = "active_project_count"
        case toolchainCounts = "toolchain_counts"
    }
}

public struct ProjectSignal: Codable, Sendable, Identifiable {
    public let root: String
    public let toolchains: [String]
    public let markers: [String]
    public let sourceProcessCount: Int
    public let families: [String]

    public var id: String { root }

    enum CodingKeys: String, CodingKey {
        case root
        case toolchains
        case markers
        case sourceProcessCount = "source_process_count"
        case families
    }
}

public struct StorageTarget: Codable, Sendable, Identifiable {
    public let label: String
    public let family: String
    public let classification: String
    public let sizeBytes: Int

    public var id: String { label }

    enum CodingKeys: String, CodingKey {
        case label
        case family
        case classification
        case sizeBytes = "size_bytes"
    }
}

public enum ReceiptSummaryLoader {
    public static func load(from url: URL) throws -> ReceiptSummary {
        let data = try Data(contentsOf: url)
        return try JSONDecoder().decode(ReceiptSummary.self, from: data)
    }
}

public enum DreamCleanrArtifactPaths {
    public static func reportDirectory(homeDirectory: URL = FileManager.default.homeDirectoryForCurrentUser) -> URL {
        homeDirectory
            .appendingPathComponent("Library", isDirectory: true)
            .appendingPathComponent("Logs", isDirectory: true)
            .appendingPathComponent("DreamCleanr", isDirectory: true)
            .appendingPathComponent("reports", isDirectory: true)
    }

    public static func latestSummaryURL(homeDirectory: URL = FileManager.default.homeDirectoryForCurrentUser) -> URL {
        reportDirectory(homeDirectory: homeDirectory).appendingPathComponent("latest-summary.json")
    }

    public static func latestReportURL(homeDirectory: URL = FileManager.default.homeDirectoryForCurrentUser) -> URL {
        reportDirectory(homeDirectory: homeDirectory).appendingPathComponent("latest.json")
    }

    public static func latestHTMLURL(homeDirectory: URL = FileManager.default.homeDirectoryForCurrentUser) -> URL {
        reportDirectory(homeDirectory: homeDirectory).appendingPathComponent("latest.html")
    }
}
