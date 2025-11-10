import SwiftUI

struct LogsView: View {
    @EnvironmentObject var backendManager: BackendManager
    @State private var selectedLogType = "output"
    @State private var searchText = ""
    @State private var autoScroll = true

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header
            HStack {
                Text("Logs")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                Spacer()

                // Auto-scroll toggle
                Toggle("Auto-scroll", isOn: $autoScroll)
                    .toggleStyle(.switch)

                // Clear logs
                Button(action: clearLogs) {
                    Label("Clear", systemImage: "trash")
                }
            }
            .padding()

            Divider()

            // Log type picker
            Picker("Log Type", selection: $selectedLogType) {
                Text("Standard Output").tag("output")
                Text("Error Output").tag("error")
            }
            .pickerStyle(.segmented)
            .padding(.horizontal)
            .padding(.vertical, 8)

            // Search
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(.secondary)

                TextField("Filter logs...", text: $searchText)
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
            .padding(.horizontal)
            .padding(.bottom, 8)

            Divider()

            // Logs display
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 0) {
                        ForEach(filteredLogs.indices, id: \.self) { index in
                            Text(filteredLogs[index])
                                .font(.system(.caption, design: .monospaced))
                                .textSelection(.enabled)
                                .padding(.horizontal)
                                .padding(.vertical, 2)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .id(index)
                        }
                    }
                    .onChange(of: filteredLogs.count) { _ in
                        if autoScroll && !filteredLogs.isEmpty {
                            proxy.scrollTo(filteredLogs.count - 1, anchor: .bottom)
                        }
                    }
                }
                .background(Color(NSColor.textBackgroundColor))
            }
        }
    }

    private var filteredLogs: [String] {
        let logs = selectedLogType == "output" ? backendManager.backendOutput : backendManager.errorOutput

        if searchText.isEmpty {
            return logs
        } else {
            return logs.filter { $0.localizedCaseInsensitiveContains(searchText) }
        }
    }

    private func clearLogs() {
        if selectedLogType == "output" {
            backendManager.backendOutput = []
        } else {
            backendManager.errorOutput = []
        }
    }
}

#Preview {
    LogsView()
        .environmentObject(BackendManager())
}
