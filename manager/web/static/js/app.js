// Global Alpine.js app state
function app() {
    return {
        overallHealth: 'unknown',
        lastUpdate: '',

        init() {
            this.updateStatus();
            setInterval(() => this.updateStatus(), 30000); // Update every 30 seconds
        },

        async updateStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();

                this.overallHealth = data.overall_health;
                this.lastUpdate = new Date().toLocaleTimeString();
            } catch (error) {
                console.error('Failed to update status:', error);
            }
        },

        async logout() {
            try {
                await fetch('/api/logout', { method: 'POST' });
                window.location.href = '/login';
            } catch (error) {
                console.error('Logout failed:', error);
            }
        }
    }
}

// Utility functions
window.formatBytes = function(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

window.formatUptime = function(seconds) {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (days > 0) {
        return `${days}d ${hours}h`;
    } else if (hours > 0) {
        return `${hours}h ${minutes}m`;
    } else {
        return `${minutes}m`;
    }
}

window.formatTime = function(timestamp) {
    return new Date(timestamp).toLocaleString();
}
