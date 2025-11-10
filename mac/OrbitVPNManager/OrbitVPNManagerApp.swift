import SwiftUI

@main
struct OrbitVPNManagerApp: App {
    @StateObject private var backendManager = BackendManager()
    @StateObject private var apiService = APIService()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(backendManager)
                .environmentObject(apiService)
                .frame(minWidth: 1200, minHeight: 800)
        }
        .windowStyle(.hiddenTitleBar)
        .windowToolbarStyle(.unified)
    }
}
