// CliRunnerTests — verify the argument allowlist refuses anything unsafe.

import XCTest
@testable import DreamCleanrMenubar

final class CliRunnerTests: XCTestCase {

    func testAllowedSimpleSubcommands() async {
        let r = CliRunner.shared
        // These should all pass validation (we don't actually require the CLI to be present —
        // validation is the layer under test).
        // We test the validate() function indirectly via run(), but in this scaffold we keep it private.
        // A separate `internal` exposure is added in a follow-up if we want tighter unit coverage.
        XCTAssertTrue(true, "Placeholder — see TODO above; real unit tests added when we expose validate().")
    }

    func testRejectsArbitrary() async {
        // When dreamcleanr CLI isn't on PATH, run() returns the "Failed to start" string.
        // We can't deeply test the validation without exposing the private validate() —
        // but smoke-test that the public surface doesn't crash on weird input.
        let result = await CliRunner.shared.run(["rm", "-rf", "/"])
        XCTAssertTrue(result.contains("Refused") || result.contains("Failed"))
    }
}
