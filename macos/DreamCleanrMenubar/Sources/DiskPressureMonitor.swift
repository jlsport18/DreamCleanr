// DiskPressureMonitor — observes free-disk-space on the boot volume,
// publishes a "pressure level" + matching SF Symbol + tint color.
//
// Refreshes every 60 seconds in the background. Also re-checked
// after every CLI run so the indicator reflects post-cleanup state
// immediately.

import Foundation
import SwiftUI

@MainActor
final class DiskPressureMonitor: ObservableObject {
    enum Pressure {
        case healthy   // > 25% free
        case warning   // 10-25% free
        case critical  // < 10% free
    }

    @Published private(set) var freeBytes: Int64 = 0
    @Published private(set) var totalBytes: Int64 = 0
    @Published private(set) var pressure: Pressure = .healthy

    private var timer: Timer?

    init() {
        refresh()
        startTimer()
    }

    deinit {
        timer?.invalidate()
    }

    private func startTimer() {
        timer = Timer.scheduledTimer(withTimeInterval: 60, repeats: true) { [weak self] _ in
            Task { @MainActor in self?.refresh() }
        }
    }

    func refresh() {
        let url = URL(fileURLWithPath: "/")
        do {
            let values = try url.resourceValues(forKeys: [.volumeAvailableCapacityForImportantUsageKey, .volumeTotalCapacityKey])
            freeBytes = Int64(values.volumeAvailableCapacityForImportantUsage ?? 0)
            totalBytes = Int64(values.volumeTotalCapacity ?? 0)
            pressure = computePressure()
        } catch {
            // Keep last-known values on failure
        }
    }

    private func computePressure() -> Pressure {
        guard totalBytes > 0 else { return .healthy }
        let pct = Double(freeBytes) / Double(totalBytes)
        if pct < 0.10 { return .critical }
        if pct < 0.25 { return .warning }
        return .healthy
    }

    var symbolName: String {
        switch pressure {
        case .healthy:  return "internaldrive"
        case .warning:  return "internaldrive.fill"
        case .critical: return "exclamationmark.triangle.fill"
        }
    }

    var tint: Color {
        switch pressure {
        case .healthy:  return .green
        case .warning:  return .orange
        case .critical: return .red
        }
    }

    var statusText: String {
        let freeGB = Double(freeBytes) / 1_073_741_824
        let totalGB = Double(totalBytes) / 1_073_741_824
        let pct = totalBytes > 0 ? Int((Double(freeBytes) / Double(totalBytes)) * 100) : 0
        return String(format: "%.1f GB free of %.0f GB (%d%%)", freeGB, totalGB, pct)
    }
}
