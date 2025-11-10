import Foundation
import Combine

class BackendManager: ObservableObject {
    @Published var isRunning = false
    @Published var backendOutput: [String] = []
    @Published var errorOutput: [String] = []

    private var process: Process?
    private var outputPipe: Pipe?
    private var errorPipe: Pipe?

    private let backendPath: String

    init() {
        // Get the path to the backend directory in the app bundle
        if let bundlePath = Bundle.main.resourcePath {
            self.backendPath = bundlePath + "/backend"
        } else {
            // Fallback to local path for development
            let currentFile = #file
            let projectPath = (currentFile as NSString).deletingLastPathComponent
            let managerPath = (projectPath as NSString).deletingLastPathComponent
            self.backendPath = managerPath + "/backend"
        }
    }

    func startBackend() {
        guard !isRunning else { return }

        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        process.arguments = [
            "python3",
            "-m",
            "uvicorn",
            "manager.web.app:create_app",
            "--factory",
            "--host", "127.0.0.1",
            "--port", "8080",
            "--reload"
        ]

        // Set working directory to backend path
        process.currentDirectoryURL = URL(fileURLWithPath: backendPath)

        // Setup pipes for output
        let outputPipe = Pipe()
        let errorPipe = Pipe()
        process.standardOutput = outputPipe
        process.standardError = errorPipe

        self.outputPipe = outputPipe
        self.errorPipe = errorPipe

        // Read output asynchronously
        outputPipe.fileHandleForReading.readabilityHandler = { [weak self] handle in
            let data = handle.availableData
            if let output = String(data: data, encoding: .utf8), !output.isEmpty {
                DispatchQueue.main.async {
                    self?.backendOutput.append(output)
                    // Keep only last 100 lines
                    if let self = self, self.backendOutput.count > 100 {
                        self.backendOutput.removeFirst()
                    }
                }
            }
        }

        errorPipe.fileHandleForReading.readabilityHandler = { [weak self] handle in
            let data = handle.availableData
            if let output = String(data: data, encoding: .utf8), !output.isEmpty {
                DispatchQueue.main.async {
                    self?.errorOutput.append(output)
                    if let self = self, self.errorOutput.count > 100 {
                        self.errorOutput.removeFirst()
                    }
                }
            }
        }

        do {
            try process.run()
            self.process = process
            DispatchQueue.main.async {
                self.isRunning = true
            }

            // Monitor process termination
            process.terminationHandler = { [weak self] _ in
                DispatchQueue.main.async {
                    self?.isRunning = false
                }
            }
        } catch {
            print("Failed to start backend: \(error)")
        }
    }

    func stopBackend() {
        guard isRunning, let process = process else { return }

        process.terminate()
        process.waitUntilExit()

        outputPipe?.fileHandleForReading.readabilityHandler = nil
        errorPipe?.fileHandleForReading.readabilityHandler = nil

        DispatchQueue.main.async {
            self.isRunning = false
            self.process = nil
        }
    }

    func restartBackend() {
        stopBackend()
        // Wait a bit before restarting
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            self.startBackend()
        }
    }

    deinit {
        stopBackend()
    }
}
