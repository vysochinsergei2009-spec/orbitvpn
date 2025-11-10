import SwiftUI

struct MarzbanView: View {
    @EnvironmentObject var apiService: APIService
    @State private var instances: [MarzbanInstance] = []
    @State private var isLoading = false
    @State private var selectedInstance: MarzbanInstance?

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header
            HStack {
                Text("Marzban Servers")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                Spacer()

                Button(action: refreshInstances) {
                    Label("Refresh", systemImage: "arrow.clockwise")
                }
                .disabled(isLoading)
            }
            .padding()

            Divider()

            if isLoading && instances.isEmpty {
                ProgressView("Loading servers...")
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if instances.isEmpty {
                VStack(spacing: 16) {
                    Image(systemName: "externaldrive.fill.badge.wifi")
                        .font(.system(size: 48))
                        .foregroundColor(.secondary)

                    Text("No Marzban Servers")
                        .font(.title2)
                        .fontWeight(.semibold)

                    Text("No Marzban instances found in the system.")
                        .font(.body)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                ScrollView {
                    LazyVStack(spacing: 16) {
                        ForEach(instances) { instance in
                            MarzbanInstanceCard(instance: instance) {
                                selectedInstance = instance
                            }
                        }
                    }
                    .padding()
                }
            }
        }
        .sheet(item: $selectedInstance) { instance in
            MarzbanInstanceDetailView(instance: instance)
        }
        .onAppear {
            refreshInstances()
        }
    }

    private func refreshInstances() {
        isLoading = true

        Task {
            do {
                let fetchedInstances = try await apiService.fetchMarzbanInstances()

                await MainActor.run {
                    self.instances = fetchedInstances
                    self.isLoading = false
                }
            } catch {
                print("Error fetching Marzban instances: \(error)")
                await MainActor.run {
                    self.isLoading = false
                }
            }
        }
    }
}

struct MarzbanInstanceCard: View {
    let instance: MarzbanInstance
    let onTap: () -> Void

    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 16) {
                // Status indicator
                VStack(spacing: 8) {
                    Circle()
                        .fill(healthColor)
                        .frame(width: 16, height: 16)

                    if !instance.isActive {
                        Image(systemName: "pause.circle.fill")
                            .foregroundColor(.orange)
                    }
                }

                // Instance info
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Text(instance.name)
                            .font(.headline)

                        Spacer()

                        if let health = instance.health {
                            Text(health.capitalized)
                                .font(.caption)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(healthColor.opacity(0.2))
                                .foregroundColor(healthColor)
                                .cornerRadius(4)
                        }
                    }

                    Text(instance.baseUrl)
                        .font(.caption)
                        .foregroundColor(.secondary)

                    HStack(spacing: 20) {
                        if let nodesCount = instance.nodesCount {
                            Label("\(nodesCount) nodes", systemImage: "square.grid.3x3.fill")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }

                        if let usersCount = instance.usersCount {
                            Label("\(usersCount) users", systemImage: "person.3.fill")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }

                        if let traffic = instance.traffic {
                            Label(String(format: "%.2f GB", traffic.totalGB), systemImage: "arrow.up.arrow.down")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                }

                Spacer()

                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color(NSColor.controlBackgroundColor))
            .cornerRadius(12)
        }
        .buttonStyle(.plain)
    }

    private var healthColor: Color {
        guard let health = instance.health else { return .gray }
        switch health.lowercased() {
        case "healthy": return .green
        case "degraded": return .yellow
        case "unhealthy": return .red
        default: return .gray
        }
    }
}

struct MarzbanInstanceDetailView: View {
    let instance: MarzbanInstance
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Instance Info
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Instance Information")
                            .font(.title2)
                            .fontWeight(.semibold)

                        DetailRow(label: "Name", value: instance.name)
                        DetailRow(label: "ID", value: instance.id)
                        DetailRow(label: "URL", value: instance.baseUrl)
                        DetailRow(label: "Priority", value: "\(instance.priority)")
                        DetailRow(label: "Status", value: instance.isActive ? "Active" : "Inactive")

                        if let health = instance.health {
                            DetailRow(label: "Health", value: health.capitalized)
                        }
                    }

                    Divider()

                    // Statistics
                    if instance.nodesCount != nil || instance.usersCount != nil {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Statistics")
                                .font(.title2)
                                .fontWeight(.semibold)

                            if let nodesCount = instance.nodesCount {
                                DetailRow(label: "Nodes", value: "\(nodesCount)")
                            }

                            if let usersCount = instance.usersCount {
                                DetailRow(label: "Users", value: "\(usersCount)")
                            }

                            if let traffic = instance.traffic {
                                DetailRow(label: "Total Traffic", value: String(format: "%.2f GB", traffic.totalGB))
                                DetailRow(label: "Upload", value: String(format: "%.2f GB", Double(traffic.upload) / 1_073_741_824))
                                DetailRow(label: "Download", value: String(format: "%.2f GB", Double(traffic.download) / 1_073_741_824))
                            }
                        }
                    }
                }
                .padding()
            }
            .navigationTitle("Server Details")
            .toolbar {
                ToolbarItem(placement: .automatic) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
        .frame(width: 500, height: 600)
    }
}

struct DetailRow: View {
    let label: String
    let value: String

    var body: some View {
        HStack {
            Text(label)
                .foregroundColor(.secondary)

            Spacer()

            Text(value)
                .fontWeight(.medium)
        }
        .padding(.vertical, 4)
    }
}

#Preview {
    MarzbanView()
        .environmentObject(APIService())
}
