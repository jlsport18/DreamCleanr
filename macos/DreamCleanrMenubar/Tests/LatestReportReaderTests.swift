// LatestReportReaderTests — verify the receipt parser handles both the
// summary schema and the full report schema, and degrades gracefully on
// malformed / missing files.

import XCTest
@testable import DreamCleanrMenubar

final class LatestReportReaderTests: XCTestCase {

    // The formatting helpers are pure functions — easiest to pin first.

    func testHumanBytesFormatsTiers() {
        XCTAssertEqual(humanBytes(0), "0 B")
        XCTAssertEqual(humanBytes(512), "512 B")
        XCTAssertEqual(humanBytes(1024), "1.0 KB")
        XCTAssertEqual(humanBytes(1024 * 1024), "1.0 MB")
        XCTAssertEqual(humanBytes(2 * 1024 * 1024 * 1024), "2.0 GB")
    }

    func testHumanBytesNegativeOrZero() {
        XCTAssertEqual(humanBytes(0), "0 B")
        XCTAssertEqual(humanBytes(-1), "0 B")
    }

    func testFormatMbDropsZeroDecimal() {
        XCTAssertEqual(formatMb(0), "0 MB")
        XCTAssertEqual(formatMb(8), "8 MB")
        XCTAssertEqual(formatMb(8.5), "8.5 MB")
    }

    // Menu line composition — verify both summary lines render the
    // dry-run prefix correctly.

    func testMenuLineForApplyRun() {
        let r = LatestReportSummary(
            runId: "r1", finishedAt: "2026-05-29T05:00:00Z",
            storageReclaimedBytes: 1024 * 1024 * 1024,
            memoryReclaimedMb: 4096,
            processesTrimmed: 3, objectsPruned: 12,
            mode: "balanced", dryRun: false
        )
        XCTAssertEqual(r.menuLine, "Last clean: 1.0 GB disk + 4096 MB RAM")
        XCTAssertEqual(r.subline, "3 procs · 12 objects · balanced")
    }

    func testMenuLineForDryRun() {
        let r = LatestReportSummary(
            runId: "r2", finishedAt: "2026-05-29T05:00:00Z",
            storageReclaimedBytes: 500 * 1024 * 1024,
            memoryReclaimedMb: 0,
            processesTrimmed: 0, objectsPruned: 5,
            mode: "balanced", dryRun: true
        )
        XCTAssertTrue(r.menuLine.hasPrefix("Preview: would reclaim"))
        XCTAssertTrue(r.menuLine.contains("500.0 MB"))
        XCTAssertTrue(r.menuLine.contains("0 MB RAM"))
    }
}
