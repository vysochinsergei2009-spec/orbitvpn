import SwiftUI

struct UsersView: View {
    @EnvironmentObject var apiService: APIService
    @State private var userStats: UserStats?
    @State private var isLoading = false
    @State private var searchText = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header
            HStack {
                Text("Users")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                Spacer()

                Button(action: refreshData) {
                    Label("Refresh", systemImage: "arrow.clockwise")
                }
                .disabled(isLoading)
            }
            .padding()

            Divider()

            // Search bar
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(.secondary)

                TextField("Search users...", text: $searchText)
                    .textFieldStyle(.plain)

                if !searchText.isEmpty {
                    Button(action: { searchText = "" }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.secondary)
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(12)
            .background(Color(NSColor.controlBackgroundColor))
            .cornerRadius(8)
            .padding()

            // Statistics Summary
            if let stats = userStats {
                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible()),
                    GridItem(.flexible()),
                    GridItem(.flexible())
                ], spacing: 12) {
                    UserStatCard(title: "Total", value: "\(stats.totalUsers)", color: .blue)
                    UserStatCard(title: "Active", value: "\(stats.activeSubscriptions)", color: .green)
                    UserStatCard(title: "Trial", value: "\(stats.trialUsers)", color: .orange)
                    UserStatCard(title: "New Today", value: "\(stats.newToday)", color: .purple)
                }
                .padding(.horizontal)
                .padding(.bottom)
            }

            Divider()

            // User list placeholder
            VStack(spacing: 16) {
                Image(systemName: "person.3.fill")
                    .font(.system(size: 48))
                    .foregroundColor(.secondary)

                Text("User Management")
                    .font(.title2)
                    .fontWeight(.semibold)

                Text("Full user list and management features will be added soon.\nFor now, you can view user statistics above.")
                    .font(.body)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 40)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .onAppear {
            refreshData()
        }
    }

    private func refreshData() {
        isLoading = true

        Task {
            do {
                let stats = try await apiService.fetchUserStats()

                await MainActor.run {
                    self.userStats = stats
                    self.isLoading = false
                }
            } catch {
                print("Error fetching user stats: \(error)")
                await MainActor.run {
                    self.isLoading = false
                }
            }
        }
    }
}

struct UserStatCard: View {
    let title: String
    let value: String
    let color: Color

    var body: some View {
        VStack(spacing: 8) {
            Text(value)
                .font(.title)
                .fontWeight(.bold)
                .foregroundColor(color)

            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
        .cornerRadius(8)
    }
}

#Preview {
    UsersView()
        .environmentObject(APIService())
}
