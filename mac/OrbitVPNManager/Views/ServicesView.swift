import SwiftUI

struct ServicesView: View {
    @EnvironmentObject var apiService: APIService
    @State private var services: [String: ServiceInfo] = [:]
    @State private var isLoading = false
    @State private var selectedService: String?
    @State private var showingActionSheet = false

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header
            HStack {
                Text("Services")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                Spacer()

                Button(action: refreshServices) {
                    Label("Refresh", systemImage: "arrow.clockwise")
                }
                .disabled(isLoading)
            }
            .padding()

            Divider()

            // Services List
            if isLoading && services.isEmpty {
                ProgressView("Loading services...")
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                List {
                    ForEach(Array(services.keys).sorted(), id: \.self) { key in
                        if let service = services[key] {
                            ServiceRow(service: service) {
                                selectedService = key
                                showingActionSheet = true
                            }
                        }
                    }
                }
                .listStyle(.inset)
            }
        }
        .confirmationDialog(
            "Service Actions",
            isPresented: $showingActionSheet,
            titleVisibility: .visible
        ) {
            if let serviceName = selectedService,
               let service = services[serviceName] {
                if service.status.lowercased() == "running" {
                    Button("Stop") {
                        controlService(serviceName, action: .stop)
                    }
                    Button("Restart") {
                        controlService(serviceName, action: .restart)
                    }
                } else {
                    Button("Start") {
                        controlService(serviceName, action: .start)
                    }
                }

                Button("Cancel", role: .cancel) {}
            }
        }
        .onAppear {
            refreshServices()
        }
    }

    private func refreshServices() {
        isLoading = true

        Task {
            do {
                let fetchedServices = try await apiService.fetchServices()

                await MainActor.run {
                    self.services = fetchedServices
                    self.isLoading = false
                }
            } catch {
                print("Error fetching services: \(error)")
                await MainActor.run {
                    self.isLoading = false
                }
            }
        }
    }

    private func controlService(_ name: String, action: ServiceAction) {
        Task {
            do {
                _ = try await apiService.controlService(name, action: action)

                // Refresh after action
                try await Task.sleep(nanoseconds: 1_000_000_000) // 1 second
                refreshServices()
            } catch {
                print("Error controlling service: \(error)")
            }
        }
    }
}

struct ServiceRow: View {
    let service: ServiceInfo
    let onAction: () -> Void

    var body: some View {
        HStack(spacing: 16) {
            // Status indicator
            Circle()
                .fill(statusColor)
                .frame(width: 12, height: 12)

            // Service info
            VStack(alignment: .leading, spacing: 4) {
                Text(service.name.capitalized)
                    .font(.headline)

                HStack(spacing: 12) {
                    Label(service.status.capitalized, systemImage: "circle.fill")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    if let uptime = service.uptime {
                        Label(formatUptime(uptime), systemImage: "clock")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    if service.restartCount > 0 {
                        Label("\(service.restartCount) restarts", systemImage: "arrow.clockwise")
                            .font(.caption)
                            .foregroundColor(.orange)
                    }
                }
            }

            Spacer()

            // Metrics
            if let cpu = service.cpu, let memory = service.memory {
                VStack(alignment: .trailing, spacing: 4) {
                    Text("CPU: \(String(format: "%.1f%%", cpu))")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    Text("RAM: \(String(format: "%.1f MB", memory))")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            // Action button
            Button(action: onAction) {
                Image(systemName: "ellipsis.circle")
                    .font(.title3)
            }
            .buttonStyle(.plain)
        }
        .padding(.vertical, 8)
    }

    private var statusColor: Color {
        switch service.status.lowercased() {
        case "running": return .green
        case "stopped": return .gray
        case "error": return .red
        default: return .orange
        }
    }

    private func formatUptime(_ seconds: Double) -> String {
        let hours = Int(seconds) / 3600
        let minutes = (Int(seconds) % 3600) / 60

        if hours > 0 {
            return "\(hours)h \(minutes)m"
        } else {
            return "\(minutes)m"
        }
    }
}

#Preview {
    ServicesView()
        .environmentObject(APIService())
}
