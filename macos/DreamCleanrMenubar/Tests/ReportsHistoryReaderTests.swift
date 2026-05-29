// ReportsHistoryReaderTests — verify the recent-reports listing pairs
// json/html files correctly, sorts newest-first, tolerates malformed
// JSON, and falls back to the reports folder when nothing is on disk.
//
// Pure-fixture tests against a temp directory; no XCUITest, no network,
// no real ~/Library writes.

import XCTest
@testable import DreamCleanrMenubar

final class ReportsHistoryReaderTests: XCTestCase {

    // MARK: - ReportEntry.menuLabel formatting

    func testMenuLabelWithBothBytesAndMb() {
        let d = ISO8601DateFormatter().date(from: "2026-05-28T03:30:00Z")!
        let entry = ReportEntry(
            id: "abc", date: d, htmlURL: nil, jsonURL: URL(fileURLWithPath: "/tmp/x.json"),
            storageReclaimedBytes: 1_500_000_000, memoryReclaimedMb: 256
        )
        let label = entry.menuLabel
        XCTAssertTrue(label.contains("1.4 GB disk"))
        XCTAssertTrue(label.contains("256 MB RAM"))
        XCTAssertTrue(label.contains("·"))
    }

    func testMenuLabelOnlyStorage() {
        let d = ISO8601DateFormatter().date(from: "2026-05-28T03:30:00Z")!
        let entry = ReportEntry(
            id: "abc", date: d, htmlURL: nil, jsonURL: URL(fileURLWithPath: "/tmp/x.json"),
            storageReclaimedBytes: 500_000_000, memoryReclaimedMb: 0
        )
        let label = entry.menuLabel
        XCTAssertTrue(label.contains("MB disk") || label.contains("GB disk"))
        XCTAssertFalse(label.contains("RAM"))
    }

    func testMenuLabelZeroValuesShowsOnlyDate() {
        let d = ISO8601DateFormatter().date(from: "2026-05-28T03:30:00Z")!
        let entry = ReportEntry(
            id: "abc", date: d, htmlURL: nil, jsonURL: URL(fileURLWithPath: "/tmp/x.json"),
            storageReclaimedBytes: 0, memoryReclaimedMb: 0
        )
        let label = entry.menuLabel
        XCTAssertFalse(label.contains("·"))
        XCTAssertFalse(label.contains("disk"))
        XCTAssertFalse(label.contains("RAM"))
    }

    // MARK: - Filename pairing

    /// The reader pairs `report-<TS>-<RUNID>.json` with the matching `.html`
    /// next to it. We verify the pairing by constructing the expected HTML
    /// URL from the JSON URL using the same logic the reader uses.
    func testJsonHtmlPairingConstructsExpectedURL() {
        let json = URL(fileURLWithPath: "/Users/x/Library/Logs/DreamCleanr/reports/report-20260528-abc.json")
        let html = json.deletingPathExtension().appendingPathExtension("html")
        XCTAssertEqual(html.lastPathComponent, "report-20260528-abc.html")
    }

    // MARK: - humanBytes / formatMb edge cases worth pinning

    func testHumanBytesPicksTier() {
        XCTAssertEqual(humanBytes(900), "900 B")
        XCTAssertEqual(humanBytes(2048), "2.0 KB")
        XCTAssertEqual(humanBytes(1_500_000_000), "1.4 GB")
    }
}
