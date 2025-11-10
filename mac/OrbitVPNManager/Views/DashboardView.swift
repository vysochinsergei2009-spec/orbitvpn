import SwiftUI
import Charts

struct DashboardView: View {
    @EnvironmentObject var apiService: APIService
    @State private var systemStatus: SystemStatus?
    @State private var userStats: UserStats?
    @State private var isLoading = false
    @State private var lastUpdate = Date()

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Header
                HStack {
                    VStack(alignment: .leading) {
                        Text("Dashboard")
                            .font(.largeTitle)
                            .fontWeight(.bold)

                        Text("Last updated: \(lastUpdate, style: .time)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    Spacer()

                    Button(action: refreshData) {
                        Label("Refresh", systemImage: "arrow.clockwise")
                    }
                    .disabled(isLoading)
                }
                .padding()

                // System Status Cards
                if let status = systemStatus {
                    HStack(spacing: 16) {
                        StatusCard(
                            title: "System Health",
                            value: status.healthStatus,
                            icon: "heart.fill",
                            color: status.healthStatus == "healthy" ? .green : .orange
                        )

                        StatusCard(
                            title: "Services Running",
                            value: "\(status.servicesRunning)/\(status.servicesTotal)",
                            icon: "server.rack",
                            color: .blue
                        )

                        StatusCard(
                            title: "Uptime",
                            value: formatUptime(status.uptime),
                            icon: "clock.fill",
                            color: .purple
                        )
                    }
                    .padding(.horizontal)
                }

                // User Statistics
                if let stats = userStats {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("User Statistics")
                            .font(.title2)
                            .fontWeight(.semibold)
                            .padding(.horizontal)

                        LazyVGrid(columns: [
                            GridItem(.flexible()),
                            GridItem(.flexible()),
                            GridItem(.flexible())
                        ], spacing: 16) {
                            StatCard(title: "Total Users", value: "\(stats.totalUsers)", icon: "person.3.fill", color: .blue)
                            StatCard(title: "Active Subscriptions", value: "\(stats.activeSubscriptions)", icon: "checkmark.circle.fill", color: .green)
                            StatCard(title: "Trial Users", value: "\(stats.trialUsers)", icon: "star.fill", color: .orange)
                            StatCard(title: "New Today", value: "\(stats.newToday)", icon: "plus.circle.fill", color: .purple)
                            StatCard(title: "Total Configs", value: "\(stats.totalConfigs)", icon: "doc.fill", color: .indigo)
                        }
                        .padding(.horizontal)
                    }
                }

                // Loading state
                if isLoading && systemStatus == nil {
                    ProgressView("Loading dashboard...")
                        .frame(maxWidth: .infinity, alignment: .center)
                        .padding()
                }
            }
            .padding(.vertical)
        }
        .onAppear {
            refreshData()
        }
    }

    private func refreshData() {
        isLoading = true

        Task {
            do {
                async let statusFetch = apiService.fetchSystemStatus()
                async let statsFetch = apiService.fetchUserStats()

                let (status, stats) = try await (statusFetch, statsFetch)

                await MainActor.run {
                    self.systemStatus = status
                    self.userStats = stats
                    self.lastUpdate = Date()
                    self.isLoading = false
                }
            } catch {
                print("Error fetching dashboard data: \(error)")
                await MainActor.run {
                    self.isLoading = false
                }
            }
        }
    }

    private func formatUptime(_ seconds: Double) -> String {
        let days = Int(seconds) / 86400
        let hours = (Int(seconds) % 86400) / 3600
        let minutes = (Int(seconds) % 3600) / 60

        if days > 0 {
            return "\(days)d \(hours)h"
        } else if hours > 0 {
            return "\(hours)h \(minutes)m"
        } else {
            return "\(minutes)m"
        }
    }
}

struct StatusCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)

                Spacer()
            }

            Text(value)
                .font(.title)
                .fontWeight(.bold)

            Text(title)
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
    }
}

struct StatCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color

    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: icon)
                .font(.title)
                .foregroundColor(color)

            Text(value)
                .font(.title2)
                .fontWeight(.bold)

            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(12)
    }
}

#Preview {
    DashboardView()
        .environmentObject(APIService())
}
