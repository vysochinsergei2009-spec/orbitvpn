import Foundation
import Combine

class APIService: ObservableObject {
    @Published var isAuthenticated = false
    @Published var isLoading = false
    @Published var errorMessage: String?

    private var baseURL: String
    private var session: URLSession
    private var cancellables = Set<AnyCancellable>()

    init(baseURL: String = "http://localhost:8080") {
        self.baseURL = baseURL
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.httpCookieStorage = HTTPCookieStorage.shared
        config.httpCookieAcceptPolicy = .always
        config.httpShouldSetCookies = true
        self.session = URLSession(configuration: config)
    }

    // MARK: - Generic Request

    private func request<T: Decodable>(
        _ endpoint: String,
        method: String = "GET",
        body: Data? = nil
    ) async throws -> T {
        guard let url = URL(string: "\(baseURL)\(endpoint)") else {
            throw URLError(.badURL)
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let body = body {
            request.httpBody = body
        }

        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            throw URLError(.init(rawValue: httpResponse.statusCode))
        }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(T.self, from: data)
    }

    // MARK: - Authentication

    func login(username: String, password: String) async throws {
        let loginData = LoginRequest(username: username, password: password)
        let jsonData = try JSONEncoder().encode(loginData)

        let response: LoginResponse = try await request("/api/login", method: "POST", body: jsonData)

        await MainActor.run {
            self.isAuthenticated = response.success
        }
    }

    func logout() async throws {
        let response: LoginResponse = try await request("/api/logout", method: "POST")

        await MainActor.run {
            self.isAuthenticated = !response.success
        }
    }

    // MARK: - System Status

    func fetchSystemStatus() async throws -> SystemStatus {
        return try await request("/api/status")
    }

    // MARK: - Services

    func fetchServices() async throws -> [String: ServiceInfo] {
        let response: ServicesResponse = try await request("/api/services")
        return response.services
    }

    func controlService(_ serviceName: String, action: ServiceAction) async throws -> ServiceActionResponse {
        return try await request("/api/services/\(serviceName)/\(action.rawValue)", method: "POST")
    }

    // MARK: - User Stats

    func fetchUserStats() async throws -> UserStats {
        return try await request("/api/users/stats")
    }

    // MARK: - Marzban

    func fetchMarzbanInstances() async throws -> [MarzbanInstance] {
        let response: MarzbanInstancesResponse = try await request("/api/marzban/instances")
        return response.instances
    }

    func fetchMarzbanInstance(_ id: String) async throws -> MarzbanInstance {
        return try await request("/api/marzban/instances/\(id)")
    }

    // MARK: - Metrics

    func fetchMetricsHistory(service: String? = nil, hours: Int = 1) async throws -> [ServiceMetrics] {
        var endpoint = "/api/metrics/history?hours=\(hours)"
        if let service = service {
            endpoint += "&service=\(service)"
        }

        if let service = service {
            let response: MetricsHistoryResponse = try await request(endpoint)
            return response.metrics
        } else {
            // For all services, return empty for now
            return []
        }
    }

    // MARK: - Health Check

    func checkHealth() async -> Bool {
        do {
            let _: SystemStatus = try await request("/api/status")
            return true
        } catch {
            return false
        }
    }
}
