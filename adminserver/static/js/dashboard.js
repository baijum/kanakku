/**
 * Kanakku Monitoring Dashboard JavaScript
 *
 * Handles real-time updates, chart visualization, and user interactions
 * for the monitoring dashboard.
 */

class Dashboard {
    constructor() {
        this.updateInterval = 30000; // 30 seconds
        this.charts = {};
        this.currentLogKey = '';
        this.isConnected = false;
        this.updateTimer = null;

        // Bind methods
        this.updateServices = this.updateServices.bind(this);
        this.updateMetrics = this.updateMetrics.bind(this);
        this.loadLogs = this.loadLogs.bind(this);
        this.searchLogs = this.searchLogs.bind(this);
        this.showError = this.showError.bind(this);
        this.hideError = this.hideError.bind(this);
    }

    /**
     * Initialize the dashboard
     */
    init() {
        console.log('Initializing Kanakku Monitoring Dashboard...');

        this.setupEventListeners();
        this.initializeCharts();
        this.startAutoUpdate();

        // Initial data load
        this.updateServices();
        this.updateMetrics();
        this.updateConnectionStatus(true);

        console.log('Dashboard initialized successfully');
    }

    /**
     * Set up event listeners for user interactions
     */
    setupEventListeners() {
        // Service refresh (auto-handled by timer)

        // Metrics refresh button
        const refreshMetricsBtn = document.getElementById('refresh-metrics');
        if (refreshMetricsBtn) {
            refreshMetricsBtn.addEventListener('click', this.updateMetrics);
        }

        // Log controls
        const loadLogsBtn = document.getElementById('load-logs');
        const refreshLogsBtn = document.getElementById('refresh-logs');
        const searchLogsBtn = document.getElementById('search-logs');
        const clearSearchBtn = document.getElementById('clear-search');
        const logSelector = document.getElementById('log-selector');

        if (loadLogsBtn) {
            loadLogsBtn.addEventListener('click', this.loadLogs);
        }

        if (refreshLogsBtn) {
            refreshLogsBtn.addEventListener('click', () => {
                if (this.currentLogKey) {
                    this.loadLogs();
                }
            });
        }

        if (searchLogsBtn) {
            searchLogsBtn.addEventListener('click', this.searchLogs);
        }

        if (clearSearchBtn) {
            clearSearchBtn.addEventListener('click', () => {
                document.getElementById('log-search-input').value = '';
                if (this.currentLogKey) {
                    this.loadLogs();
                }
            });
        }

        if (logSelector) {
            logSelector.addEventListener('change', (e) => {
                this.currentLogKey = e.target.value;
                if (this.currentLogKey) {
                    this.loadLogs();
                }
            });
        }

        // Search on Enter key
        const searchInput = document.getElementById('log-search-input');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.searchLogs();
                }
            });
        }

        // Error banner close
        const errorClose = document.getElementById('error-close');
        if (errorClose) {
            errorClose.addEventListener('click', this.hideError);
        }
    }

    /**
     * Initialize Chart.js charts for metrics visualization
     */
    initializeCharts() {
        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                x: {
                    display: false
                }
            }
        };

        // CPU Chart
        const cpuCanvas = document.getElementById('cpu-chart');
        if (cpuCanvas) {
            this.charts.cpu = new Chart(cpuCanvas, {
                type: 'line',
                data: {
                    labels: Array(10).fill(''),
                    datasets: [{
                        data: Array(10).fill(0),
                        borderColor: '#2563eb',
                        backgroundColor: 'rgba(37, 99, 235, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: chartOptions
            });
        }

        // Memory Chart
        const memoryCanvas = document.getElementById('memory-chart');
        if (memoryCanvas) {
            this.charts.memory = new Chart(memoryCanvas, {
                type: 'line',
                data: {
                    labels: Array(10).fill(''),
                    datasets: [{
                        data: Array(10).fill(0),
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: chartOptions
            });
        }

        // Disk Chart
        const diskCanvas = document.getElementById('disk-chart');
        if (diskCanvas) {
            this.charts.disk = new Chart(diskCanvas, {
                type: 'doughnut',
                data: {
                    labels: ['Used', 'Free'],
                    datasets: [{
                        data: [0, 100],
                        backgroundColor: ['#f59e0b', '#e5e7eb'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }
    }

    /**
     * Start automatic updates
     */
    startAutoUpdate() {
        this.updateTimer = setInterval(() => {
            this.updateServices();
            this.updateMetrics();
        }, this.updateInterval);
    }

    /**
     * Stop automatic updates
     */
    stopAutoUpdate() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
    }

    /**
     * Update services status
     */
    async updateServices() {
        try {
            const response = await fetch('/api/services/status');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.renderServices(data);
            this.updateConnectionStatus(true);

        } catch (error) {
            console.error('Error updating services:', error);
            this.showError(`Failed to update services: ${error.message}`);
            this.updateConnectionStatus(false);
        }
    }

    /**
     * Update system metrics
     */
    async updateMetrics() {
        try {
            const response = await fetch('/api/system/metrics');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.renderMetrics(data);
            this.updateConnectionStatus(true);

        } catch (error) {
            console.error('Error updating metrics:', error);
            this.showError(`Failed to update metrics: ${error.message}`);
            this.updateConnectionStatus(false);
        }
    }

    /**
     * Load logs for the selected log file
     */
    async loadLogs() {
        if (!this.currentLogKey) {
            this.showError('Please select a log file first');
            return;
        }

        const lines = document.getElementById('log-lines').value || 100;

        try {
            const response = await fetch(`/api/logs/${this.currentLogKey}?lines=${lines}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.renderLogs(data.content);

        } catch (error) {
            console.error('Error loading logs:', error);
            this.showError(`Failed to load logs: ${error.message}`);
        }
    }

    /**
     * Search logs
     */
    async searchLogs() {
        if (!this.currentLogKey) {
            this.showError('Please select a log file first');
            return;
        }

        const query = document.getElementById('log-search-input').value.trim();
        if (!query) {
            this.showError('Please enter a search query');
            return;
        }

        try {
            const response = await fetch(`/api/logs/${this.currentLogKey}/search?q=${encodeURIComponent(query)}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.renderLogs(data.results);

        } catch (error) {
            console.error('Error searching logs:', error);
            this.showError(`Failed to search logs: ${error.message}`);
        }
    }

    /**
     * Render services status
     */
    renderServices(data) {
        const servicesGrid = document.getElementById('services-grid');
        const totalServices = document.getElementById('total-services');
        const activeServices = document.getElementById('active-services');

        if (!servicesGrid) return;

        // Update summary
        if (totalServices) totalServices.textContent = data.total_services || 0;
        if (activeServices) activeServices.textContent = data.active_services || 0;

        // Clear existing content
        servicesGrid.innerHTML = '';

        // Render service cards
        Object.entries(data.services || {}).forEach(([serviceName, serviceInfo]) => {
            const card = document.createElement('div');
            card.className = `service-card ${serviceInfo.active ? 'active' : 'inactive'}`;

            card.innerHTML = `
                <div class="service-header">
                    <div class="service-name">${serviceName}</div>
                    <div class="service-status ${serviceInfo.active ? 'active' : 'inactive'}">
                        ${serviceInfo.status}
                    </div>
                </div>
                <div class="service-details">
                    <div class="service-detail">
                        <span class="service-detail-label">Load State:</span>
                        <span class="service-detail-value">${serviceInfo.loadstate || 'Unknown'}</span>
                    </div>
                    <div class="service-detail">
                        <span class="service-detail-label">Sub State:</span>
                        <span class="service-detail-value">${serviceInfo.substate || 'Unknown'}</span>
                    </div>
                    <div class="service-detail">
                        <span class="service-detail-label">PID:</span>
                        <span class="service-detail-value">${serviceInfo.mainpid || 'N/A'}</span>
                    </div>
                    <div class="service-detail">
                        <span class="service-detail-label">Last Checked:</span>
                        <span class="service-detail-value">${this.formatTime(serviceInfo.last_checked)}</span>
                    </div>
                </div>
            `;

            servicesGrid.appendChild(card);
        });

        this.updateLastUpdated();
    }

    /**
     * Render system metrics
     */
    renderMetrics(data) {
        // Update metric values
        const cpuValue = document.getElementById('cpu-value');
        const memoryValue = document.getElementById('memory-value');
        const diskValue = document.getElementById('disk-value');
        const uptimeValue = document.getElementById('uptime-value');
        const loadAverage = document.getElementById('load-average');
        const memoryUsed = document.getElementById('memory-used');
        const memoryTotal = document.getElementById('memory-total');
        const processCount = document.getElementById('process-count');

        if (cpuValue) cpuValue.textContent = `${(data.cpu_usage || 0).toFixed(1)}%`;
        if (memoryValue) memoryValue.textContent = `${(data.memory?.usage_percent || 0).toFixed(1)}%`;
        if (diskValue) diskValue.textContent = `${(data.disk_usage || 0).toFixed(1)}%`;
        if (uptimeValue) uptimeValue.textContent = data.uptime || 'Unknown';
        if (loadAverage) loadAverage.textContent = (data.load_average || 0).toFixed(2);
        if (memoryUsed) memoryUsed.textContent = `${(data.memory?.used_mb || 0).toFixed(0)} MB`;
        if (memoryTotal) memoryTotal.textContent = `${(data.memory?.total_mb || 0).toFixed(0)} MB`;
        if (processCount) processCount.textContent = data.process_count || 0;

        // Update charts
        this.updateChart('cpu', data.cpu_usage || 0);
        this.updateChart('memory', data.memory?.usage_percent || 0);
        this.updateDiskChart(data.disk_usage || 0);

        this.updateLastUpdated();
    }

    /**
     * Update a line chart with new data
     */
    updateChart(chartName, value) {
        const chart = this.charts[chartName];
        if (!chart) return;

        const data = chart.data.datasets[0].data;
        data.shift(); // Remove first element
        data.push(value); // Add new value

        chart.update('none'); // Update without animation for performance
    }

    /**
     * Update the disk usage doughnut chart
     */
    updateDiskChart(usagePercent) {
        const chart = this.charts.disk;
        if (!chart) return;

        chart.data.datasets[0].data = [usagePercent, 100 - usagePercent];
        chart.update('none');
    }

    /**
     * Render logs content
     */
    renderLogs(content) {
        const logContent = document.getElementById('log-content');
        if (!logContent) return;

        if (!content || content.trim() === '') {
            logContent.innerHTML = '<div class="log-placeholder">No log content available</div>';
            return;
        }

        // Escape HTML and preserve formatting
        const escapedContent = this.escapeHtml(content);
        logContent.textContent = escapedContent;

        // Scroll to bottom
        logContent.scrollTop = logContent.scrollHeight;
    }

    /**
     * Update connection status indicator
     */
    updateConnectionStatus(connected) {
        this.isConnected = connected;

        const statusDot = document.querySelector('.status-dot');
        const statusText = document.querySelector('.status-text');

        if (statusDot) {
            statusDot.className = `status-dot ${connected ? 'connected' : 'error'}`;
        }

        if (statusText) {
            statusText.textContent = connected ? 'Connected' : 'Connection Error';
        }
    }

    /**
     * Update last updated timestamp
     */
    updateLastUpdated() {
        const lastUpdatedTime = document.getElementById('last-updated-time');
        if (lastUpdatedTime) {
            lastUpdatedTime.textContent = this.formatTime(new Date().toISOString());
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        const errorBanner = document.getElementById('error-banner');
        const errorMessage = document.getElementById('error-message');

        if (errorBanner && errorMessage) {
            errorMessage.textContent = message;
            errorBanner.style.display = 'block';

            // Auto-hide after 5 seconds
            setTimeout(() => {
                this.hideError();
            }, 5000);
        }

        console.error('Dashboard Error:', message);
    }

    /**
     * Hide error message
     */
    hideError() {
        const errorBanner = document.getElementById('error-banner');
        if (errorBanner) {
            errorBanner.style.display = 'none';
        }
    }

    /**
     * Format timestamp for display
     */
    formatTime(isoString) {
        if (!isoString) return '--';

        try {
            const date = new Date(isoString);
            return date.toLocaleTimeString();
        } catch (error) {
            return '--';
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Cleanup when dashboard is destroyed
     */
    destroy() {
        this.stopAutoUpdate();

        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });

        this.charts = {};
    }
}

// Global dashboard instance
let dashboardInstance = null;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    dashboardInstance = new Dashboard();
    dashboardInstance.init();
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (dashboardInstance) {
        dashboardInstance.destroy();
    }
});

// Export for global access
window.Dashboard = Dashboard;
