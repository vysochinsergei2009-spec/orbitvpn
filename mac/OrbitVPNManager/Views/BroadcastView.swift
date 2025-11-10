import SwiftUI

struct BroadcastView: View {
    @State private var broadcastMessage = ""
    @State private var targetAudience = "all"
    @State private var showingConfirmation = false
    @State private var isSending = false

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header
            HStack {
                Text("Broadcast")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                Spacer()
            }
            .padding()

            Divider()

            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    // Message Input
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Message")
                            .font(.headline)

                        TextEditor(text: $broadcastMessage)
                            .font(.body)
                            .frame(minHeight: 200)
                            .padding(8)
                            .background(Color(NSColor.textBackgroundColor))
                            .cornerRadius(8)
                            .overlay(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(Color.secondary.opacity(0.2), lineWidth: 1)
                            )

                        Text("\(broadcastMessage.count) characters")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    // Target Audience
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Target Audience")
                            .font(.headline)

                        Picker("", selection: $targetAudience) {
                            Text("All Users").tag("all")
                            Text("Users with Notifications Enabled").tag("subscribed")
                        }
                        .pickerStyle(.radioGroup)
                    }

                    Divider()

                    // Preview
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Preview")
                            .font(.headline)

                        HStack {
                            VStack(alignment: .leading, spacing: 8) {
                                Text("To:")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)

                                Text(targetAudience == "all" ? "All Users" : "Users with Notifications")
                                    .font(.subheadline)
                            }

                            Spacer()
                        }
                        .padding()
                        .background(Color(NSColor.controlBackgroundColor))
                        .cornerRadius(8)

                        if !broadcastMessage.isEmpty {
                            VStack(alignment: .leading, spacing: 8) {
                                Text("Message:")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)

                                Text(broadcastMessage)
                                    .font(.body)
                            }
                            .padding()
                            .background(Color(NSColor.controlBackgroundColor))
                            .cornerRadius(8)
                        }
                    }

                    // Send Button
                    HStack {
                        Spacer()

                        Button("Send Broadcast") {
                            showingConfirmation = true
                        }
                        .disabled(broadcastMessage.isEmpty || isSending)
                        .buttonStyle(.borderedProminent)
                        .controlSize(.large)

                        Spacer()
                    }
                    .padding(.top, 20)
                }
                .padding()
            }
        }
        .alert("Confirm Broadcast", isPresented: $showingConfirmation) {
            Button("Cancel", role: .cancel) {}
            Button("Send") {
                sendBroadcast()
            }
        } message: {
            Text("Are you sure you want to send this message to \(targetAudience == "all" ? "all users" : "users with notifications enabled")?")
        }
    }

    private func sendBroadcast() {
        isSending = true

        // TODO: Implement actual broadcast API call
        // For now, just simulate
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            isSending = false
            broadcastMessage = ""
        }
    }
}

#Preview {
    BroadcastView()
}
