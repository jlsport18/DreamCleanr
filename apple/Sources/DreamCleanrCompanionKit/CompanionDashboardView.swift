import SwiftUI
import DreamCleanrAppleShared

public struct CompanionDashboardView: View {
    public let summary: ReceiptSummary

    public init(summary: ReceiptSummary) {
        self.summary = summary
    }

    public var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("DreamCleanr Companion")
                        .font(.largeTitle.weight(.bold))
                    Text("Latest Mac-side receipt summary")
                        .foregroundStyle(.secondary)
                }

                HStack(spacing: 12) {
                    metricCard(title: "Reclaimed", value: summary.heroValueText, caption: summary.mode.capitalized)
                    metricCard(title: "Free Space", value: summary.freeSpaceText, caption: "Current headroom")
                    metricCard(title: "Active Projects", value: "\(summary.projectSummary.activeProjectCount)", caption: "Guardrails")
                }

                VStack(alignment: .leading, spacing: 12) {
                    Text("Detector Surfaces")
                        .font(.headline)
                    ForEach(summary.detectorOverview.prefix(5)) { detector in
                        VStack(alignment: .leading, spacing: 4) {
                            HStack {
                                Text(detector.title)
                                    .font(.subheadline.weight(.semibold))
                                Spacer()
                                Text(ByteCountFormatter.string(fromByteCount: Int64(detector.totalBytes), countStyle: .file))
                                    .foregroundStyle(.secondary)
                            }
                            Text("\(detector.pathCount) roots · \(detector.safetyState.replacingOccurrences(of: "_", with: " "))")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                        .padding()
                        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
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
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 18))
    }
}
