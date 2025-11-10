import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var backendManager: BackendManager
    @EnvironmentObject var apiService: APIService
    @State private var backendURL = "http://localhost:8080"
    @State private var autoStartBackend = true
    @State private var showingRestartConfirmation = false

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header
            HStack {
                Text("Settings")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                Spacer()
            }
            .padding()

            Divider()

            Form {
                Section {
                    // Backend settings
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Backend Configuration")
                            .font(.title2)
                            .fontWeight(.semibold)

                        VStack(alignment: .leading, spacing: 8) {
                            Text("Backend URL")
                                .font(.subheadline)
                                .foregroundColor(.secondary)

                            TextField("Backend URL", text: $backendURL)
                                .textFieldStyle(.roundedBorder)

                            Text("The URL where the Python backend API is running")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }

                        Toggle("Auto-start backend on launch", isOn: $autoStartBackend)

                        HStack(spacing: 12) {
                            Button(backendManager.isRunning ? "Stop Backend" : "Start Backend") {
                                if backendManager.isRunning {
                                    backendManager.stopBackend()
                                } else {
                                    backendManager.startBackend()
                                }
                            }

                            if backendManager.isRunning {
                                Button("Restart Backend") {
                                    showingRestartConfirmation = true
                                }
                            }
                        }
                    }
                    .padding()
                }

                Divider()

                Section {
                    // App settings
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Application")
                            .font(.title2)
                            .fontWeight(.semibold)

                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Version")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)

                                Text("1.0.0")
                                    .font(.body)
                            }

                            Spacer()

                            VStack(alignment: .leading, spacing: 4) {
                                Text("Build")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)

                                Text("1")
                                    .font(.body)
                            }
                        }

                        Divider()

                        VStack(alignment: .leading, spacing: 8) {
                            Text("About")
                                .font(.subheadline)
                                .foregroundColor(.secondary)

                            Text("OrbitVPN Manager is a macOS application for managing the OrbitVPN Telegram bot and its services.")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding()
                }

                Divider()

                Section {
                    // Danger zone
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Danger Zone")
                            .font(.title2)
                            .fontWeight(.semibold)
                            .foregroundColor(.red)

                        VStack(alignment: .leading, spacing: 12) {
                            Text("Reset Application")
                                .font(.subheadline)
                                .foregroundColor(.secondary)

                            Text("This will reset all settings to default. Your bot data will not be affected.")
                                .font(.caption)
                                .foregroundColor(.secondary)

                            Button("Reset to Defaults") {
                                resetToDefaults()
                            }
                            .tint(.red)
                        }
                    }
                    .padding()
                }
            }
            .formStyle(.grouped)
        }
        .alert("Restart Backend", isPresented: $showingRestartConfirmation) {
            Button("Cancel", role: .cancel) {}
            Button("Restart") {
                backendManager.restartBackend()
            }
        } message: {
            Text("This will restart the Python backend server. Are you sure?")
        }
    }

    private func resetToDefaults() {
        backendURL = "http://localhost:8080"
        autoStartBackend = true
    }
}

#Preview {
    SettingsView()
        .environmentObject(BackendManager())
        .environmentObject(APIService())
}
