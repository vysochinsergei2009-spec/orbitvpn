import Foundation

// MARK: - Service Status Models

struct SystemStatus: Codable {
    let uptime: Double
    let servicesRunning: Int
    let servicesTotal: Int
    let healthStatus: String

    enum CodingKeys: String, CodingKey {
        case uptime
        case servicesRunning = "services_running"
        case servicesTotal = "services_total"
        case healthStatus = "health_status"
    }
}

struct ServiceInfo: Codable, Identifiable {
    let id = UUID()
    let name: String
    let status: String
    let uptime: Double?
    let restartCount: Int
    let lastError: String?
    let pid: Int?
    let memory: Double?
    let cpu: Double?

    enum CodingKeys: String, CodingKey {
        case name, status, uptime, pid, memory, cpu
        case restartCount = "restart_count"
        case lastError = "last_error"
    }

    var statusColor: String {
        switch status.lowercased() {
        case "running": return "green"
        case "stopped": return "gray"
        case "error": return "red"
        default: return "yellow"
        }
    }
}

struct ServicesResponse: Codable {
    let services: [String: ServiceInfo]
}

// MARK: - User Statistics

struct UserStats: Codable {
    let totalUsers: Int
    let activeSubscriptions: Int
    let trialUsers: Int
    let newToday: Int
    let totalConfigs: Int

    enum CodingKeys: String, CodingKey {
        case totalUsers = "total_users"
        case activeSubscriptions = "active_subscriptions"
        case trialUsers = "trial_users"
        case newToday = "new_today"
        case totalConfigs = "total_configs"
    }
}

// MARK: - Marzban Models

struct MarzbanInstance: Codable, Identifiable {
    let id: String
    let name: String
    let baseUrl: String
    let isActive: Bool
    let priority: Int
    let health: String?
    let nodesCount: Int?
    let usersCount: Int?
    let traffic: TrafficInfo?

    enum CodingKeys: String, CodingKey {
        case id, name, priority, health
        case baseUrl = "base_url"
        case isActive = "is_active"
        case nodesCount = "nodes_count"
        case usersCount = "users_count"
        case traffic
    }

    var healthColor: String {
        guard let health = health else { return "gray" }
        switch health.lowercased() {
        case "healthy": return "green"
        case "degraded": return "yellow"
        case "unhealthy": return "red"
        default: return "gray"
        }
    }
}

struct TrafficInfo: Codable {
    let upload: Int64
    let download: Int64

    var totalGB: Double {
        let total = upload + download
        return Double(total) / 1_073_741_824 // Convert to GB
    }
}

struct MarzbanInstancesResponse: Codable {
    let instances: [MarzbanInstance]
}

// MARK: - Metrics

struct ServiceMetrics: Codable {
    let timestamp: Date
    let cpu: Double?
    let memory: Double?
    let requests: Int?
    let errors: Int?

    enum CodingKeys: String, CodingKey {
        case timestamp, cpu, memory, requests, errors
    }
}

struct MetricsHistoryResponse: Codable {
    let service: String
    let metrics: [ServiceMetrics]
}

// MARK: - Authentication

struct LoginRequest: Codable {
    let username: String
    let password: String
}

struct LoginResponse: Codable {
    let success: Bool
}

// MARK: - API Response

struct APIResponse<T: Codable>: Codable {
    let success: Bool
    let data: T?
    let error: String?
}

// MARK: - Service Action

enum ServiceAction: String {
    case start
    case stop
    case restart
}

struct ServiceActionResponse: Codable {
    let success: Bool
    let service: String
    let action: String
}