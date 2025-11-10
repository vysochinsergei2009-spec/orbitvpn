import SwiftUI

struct ContentView: View {
    @EnvironmentObject var backendManager: BackendManager
    @EnvironmentObject var apiService: APIService
    @State private var selectedTab = 0

    var body: some View {
        NavigationView {
            // Sidebar
            List(selection: $selectedTab) {
                Section("Overview") {
                    NavigationLink(tag: 0, selection: $selectedTab) {
                        DashboardView()
                    } label: {
                        Label("Dashboard", systemImage: "chart.bar.fill")
                    }

                    NavigationLink(tag: 1, selection: $selectedTab) {
                        ServicesView()
                    } label: {
                        Label("Services", systemImage: "server.rack")
                    }
                }

                Section("Management") {
                    NavigationLink(tag: 2, selection: $selectedTab) {
                        UsersView()
                    } label: {
                        Label("Users", systemImage: "person.3.fill")
                    }

                    NavigationLink(tag: 3, selection: $selectedTab) {
                        MarzbanView()
                    } label: {
                        Label("Servers", systemImage: "externaldrive.fill.badge.wifi")
                    }
                }

                Section("Tools") {
                    NavigationLink(tag: 4, selection: $selectedTab) {
                        BroadcastView()
                    } label: {
                        Label("Broadcast", systemImage: "megaphone.fill")
                    }

                    NavigationLink(tag: 5, selection: $selectedTab) {
                        LogsView()
                    } label: {
                        Label("Logs", systemImage: "doc.text.fill")
                    }
                }

                Section("Settings") {
                    NavigationLink(tag: 6, selection: $selectedTab) {
                        SettingsView()
                    } label: {
                        Label("Settings", systemImage: "gearshape.fill")
                    }
                }
            }
            .listStyle(.sidebar)
            .frame(minWidth: 200)

            // Default view
            DashboardView()
        }
        .toolbar {
            ToolbarItem(placement: .navigation) {
                HStack {
                    Circle()
                        .fill(backendManager.isRunning ? Color.green : Color.red)
                        .frame(width: 8, height: 8)

                    Text(backendManager.isRunning ? "Backend Running" : "Backend Stopped")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            ToolbarItem(placement: .automatic) {
                Button(action: {
                    if backendManager.isRunning {
                        backendManager.stopBackend()
                    } else {
                        backendManager.startBackend()
                    }
                }) {
                    Image(systemName: backendManager.isRunning ? "stop.fill" : "play.fill")
                }
                .help(backendManager.isRunning ? "Stop Backend" : "Start Backend")
            }
        }
        .onAppear {
            // Auto-start backend if not running
            if !backendManager.isRunning {
                backendManager.startBackend()
            }
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(BackendManager())
        .environmentObject(APIService())
}
