// Dashboard JavaScript - Advanced Solar Monitoring
class SolarDashboard {
    constructor() {
        this.charts = {};
        this.updateInterval = null;
        this.wsConnection = null;
        this.initializeCharts();
        this.setupEventListeners();
        this.startRealTimeUpdates();
    }

    async initializeCharts() {
        // Initialize Chart.js charts
        await this.createIntensityChart();
        await this.createCorrelationChart();
        await this.createClusterChart();
        await this.createPredictionChart();
        await this.createAlertChart();
    }

    async createIntensityChart() {
        const ctx = document.getElementById('intensityChart').getContext('2d');
        const data = await this.fetchData('/data/events?limit=100');
        
        this.charts.intensity = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.events.map(e => new Date(e.date).toLocaleDateString()),
                datasets: [{
                    label: 'SEP Intensity',
                    data: data.events.map(e => e.sep_intensity),
                    borderColor: '#ff6b35',
                    backgroundColor: 'rgba(255, 107, 53, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: { display: true, text: 'SEP Intensity Over Time', color: '#ffffff' }
                },
                scales: {
                    x: { grid: { color: 'rgba(255, 255, 255, 0.1)' }, ticks: { color: '#a0a0a0' } },
                    y: { grid: { color: 'rgba(255, 255, 255, 0.1)' }, ticks: { color: '#a0a0a0' } }
                }
            }
        });
    }

    async createCorrelationChart() {
        const ctx = document.getElementById('correlationChart').getContext('2d');
        
        this.charts.correlation = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Temperature', 'Ice Extent', 'Ozone Level', 'KP Index'],
                datasets: [{
                    label: 'Correlation with SEP',
                    data: [0.65, -0.45, 0.23, 0.78],
                    borderColor: '#f7931e',
                    backgroundColor: 'rgba(247, 147, 30, 0.2)',
                    pointBackgroundColor: '#f7931e'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 1,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        pointLabels: { color: '#a0a0a0' },
                        ticks: { color: '#a0a0a0' }
                    }
                }
            }
        });
    }

    async createClusterChart() {
        const ctx = document.getElementById('clusterChart').getContext('2d');
        
        this.charts.cluster = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Cluster 1',
                    data: [],
                    backgroundColor: '#ff6b35'
                }, {
                    label: 'Cluster 2',
                    data: [],
                    backgroundColor: '#f7931e'
                }, {
                    label: 'Cluster 3',
                    data: [],
                    backgroundColor: '#ffcd3c'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#ffffff' } }
                },
                scales: {
                    x: { 
                        title: { display: true, text: 'SEP Intensity', color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#a0a0a0' }
                    },
                    y: { 
                        title: { display: true, text: 'Temperature', color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#a0a0a0' }
                    }
                }
            }
        });
    }

    async createPredictionChart() {
        const ctx = document.getElementById('predictionChart').getContext('2d');
        
        this.charts.prediction = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Historical',
                    data: [],
                    borderColor: '#17a2b8',
                    backgroundColor: 'rgba(23, 162, 184, 0.1)'
                }, {
                    label: 'Predicted',
                    data: [],
                    borderColor: '#ffcd3c',
                    backgroundColor: 'rgba(255, 205, 60, 0.1)',
                    borderDash: [5, 5]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#ffffff' } }
                },
                scales: {
                    x: { grid: { color: 'rgba(255, 255, 255, 0.1)' }, ticks: { color: '#a0a0a0' } },
                    y: { grid: { color: 'rgba(255, 255, 255, 0.1)' }, ticks: { color: '#a0a0a0' } }
                }
            }
        });
    }

    async createAlertChart() {
        const ctx = document.getElementById('alertChart').getContext('2d');
        
        this.charts.alerts = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['High', 'Medium', 'Low'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['#dc3545', '#ffc107', '#28a745']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#ffffff' } }
                }
            }
        });
    }

    setupEventListeners() {
        // Navigation tabs
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // Control buttons
        document.getElementById('collectDataBtn').addEventListener('click', () => this.collectData());
        document.getElementById('analyzeBtn').addEventListener('click', () => this.runAnalysis());
        document.getElementById('predictBtn').addEventListener('click', () => this.generatePredictions());
        document.getElementById('refreshBtn').addEventListener('click', () => this.refreshDashboard());

        // Real-time toggle
        document.getElementById('realTimeToggle').addEventListener('change', (e) => {
            if (e.target.checked) {
                this.startRealTimeUpdates();
            } else {
                this.stopRealTimeUpdates();
            }
        });

        // Date range filter
        document.getElementById('applyFilterBtn').addEventListener('click', () => this.applyDateFilter());
    }

    switchTab(tabName) {
        // Hide all tab contents
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });

        // Remove active class from all tabs
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
        });

        // Show selected tab content
        document.getElementById(tabName).classList.add('active');
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Resize charts when tab becomes visible
        setTimeout(() => {
            Object.values(this.charts).forEach(chart => chart.resize());
        }, 100);
    }

    async fetchData(endpoint) {
        try {
            const response = await fetch(endpoint);
            if (!response.ok) throw new Error('Network response was not ok');
            return await response.json();
        } catch (error) {
            console.error('Fetch error:', error);
            this.showNotification('Error fetching data', 'error');
            return null;
        }
    }

    async collectData() {
        this.showLoading('collectDataBtn');
        try {
            const response = await fetch('/data/collect', { method: 'POST' });
            const result = await response.json();
            this.showNotification(`Successfully collected ${result.data_points} data points`, 'success');
            await this.updateStats();
            await this.updateCharts();
        } catch (error) {
            this.showNotification('Error collecting data', 'error');
        } finally {
            this.hideLoading('collectDataBtn');
        }
    }

    async runAnalysis() {
        this.showLoading('analyzeBtn');
        try {
            await Promise.all([
                fetch('/analysis/correlations', { method: 'POST' }),
                fetch('/analysis/clustering', { method: 'POST' })
            ]);
            this.showNotification('Analysis completed successfully', 'success');
            await this.updateCharts();
        } catch (error) {
            this.showNotification('Error running analysis', 'error');
        } finally {
            this.hideLoading('analyzeBtn');
        }
    }

    async generatePredictions() {
        this.showLoading('predictBtn');
        try {
            const response = await fetch('/analysis/prediction', { method: 'POST' });
            const result = await response.json();
            this.showNotification(`Generated ${result.predictions} predictions`, 'success');
            await this.updatePredictionChart();
        } catch (error) {
            this.showNotification('Error generating predictions', 'error');
        } finally {
            this.hideLoading('predictBtn');
        }
    }

    async updateStats() {
        try {
            const [events, alerts, highIntensity] = await Promise.all([
                this.fetchData('/data/events?limit=1000'),
                this.fetchData('/alerts'),
                this.fetchData('/data/high-intensity')
            ]);

            if (events) {
                document.getElementById('totalEvents').textContent = events.count || 0;
                
                const avgIntensity = events.events.length > 0 
                    ? (events.events.reduce((sum, e) => sum + e.sep_intensity, 0) / events.events.length).toFixed(2)
                    : 0;
                document.getElementById('avgIntensity').textContent = avgIntensity;
            }

            if (alerts) {
                document.getElementById('activeAlerts').textContent = alerts.count || 0;
            }

            if (highIntensity) {
                document.getElementById('highIntensityEvents').textContent = highIntensity.count || 0;
            }

            // Update last update time
            document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();

        } catch (error) {
            console.error('Error updating stats:', error);
        }
    }

    async updateCharts() {
        try {
            const data = await this.fetchData('/data/events?limit=100');
            if (!data) return;

            // Update intensity chart
            if (this.charts.intensity) {
                this.charts.intensity.data.labels = data.events.map(e => 
                    new Date(e.date).toLocaleDateString()
                );
                this.charts.intensity.data.datasets[0].data = data.events.map(e => e.sep_intensity);
                this.charts.intensity.update();
            }

            // Update cluster chart with scatter plot data
            if (this.charts.cluster) {
                const clusters = {};
                data.events.forEach(event => {
                    const clusterId = event.cluster_id || 0;
                    if (!clusters[clusterId]) clusters[clusterId] = [];
                    clusters[clusterId].push({
                        x: event.sep_intensity,
                        y: event.temperature
                    });
                });

                Object.keys(clusters).forEach((clusterId, index) => {
                    if (this.charts.cluster.data.datasets[index]) {
                        this.charts.cluster.data.datasets[index].data = clusters[clusterId];
                    }
                });
                this.charts.cluster.update();
            }

        } catch (error) {
            console.error('Error updating charts:', error);
        }
    }

    async updatePredictionChart() {
        // Implementation for prediction chart updates
        console.log('Updating prediction chart...');
    }

    async updateAlerts() {
        try {
            const alerts = await this.fetchData('/alerts');
            if (!alerts) return;

            const alertsContainer = document.getElementById('alertsList');
            alertsContainer.innerHTML = '';

            alerts.alerts.forEach(alert => {
                const alertElement = document.createElement('div');
                alertElement.className = `alert-item alert-${alert.severity.toLowerCase()}`;
                alertElement.innerHTML = `
                    <div class="alert-icon">⚠️</div>
                    <div class="alert-content">
                        <div class="alert-message">${alert.message}</div>
                        <div class="alert-time">${new Date(alert.created_at).toLocaleString()}</div>
                    </div>
                    <div class="alert-value">${alert.actual_value?.toFixed(2) || 'N/A'}</div>
                `;
                alertsContainer.appendChild(alertElement);
            });

            // Update alert chart
            if (this.charts.alerts) {
                const severityCounts = { high: 0, medium: 0, low: 0 };
                alerts.alerts.forEach(alert => {
                    severityCounts[alert.severity.toLowerCase()]++;
                });

                this.charts.alerts.data.datasets[0].data = [
                    severityCounts.high,
                    severityCounts.medium,
                    severityCounts.low
                ];
                this.charts.alerts.update();
            }

        } catch (error) {
            console.error('Error updating alerts:', error);
        }
    }

    async refreshDashboard() {
        this.showLoading('refreshBtn');
        try {
            await Promise.all([
                this.updateStats(),
                this.updateCharts(),
                this.updateAlerts()
            ]);
            this.showNotification('Dashboard refreshed successfully', 'success');
        } catch (error) {
            this.showNotification('Error refreshing dashboard', 'error');
        } finally {
            this.hideLoading('refreshBtn');
        }
    }

    startRealTimeUpdates() {
        if (this.updateInterval) return;
        
        this.updateInterval = setInterval(async () => {
            await this.updateStats();
            await this.updateAlerts();
        }, 30000); // Update every 30 seconds

        document.querySelector('.real-time-indicator').classList.remove('hidden');
    }

    stopRealTimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        document.querySelector('.real-time-indicator').classList.add('hidden');
    }

    showLoading(buttonId) {
        const button = document.getElementById(buttonId);
        button.disabled = true;
        button.innerHTML = '<span class="loading"></span> Loading...';
    }

    hideLoading(buttonId) {
        const button = document.getElementById(buttonId);
        button.disabled = false;
        // Restore original text based on button ID
        const originalTexts = {
            'collectDataBtn': 'Collect Data',
            'analyzeBtn': 'Run Analysis',
            'predictBtn': 'Generate Predictions',
            'refreshBtn': 'Refresh'
        };
        button.innerHTML = originalTexts[buttonId] || 'Action';
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
                <span class="notification-message">${message}</span>
            </div>
        `;
        
        // Add notification styles if not exists
        if (!document.getElementById('notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 1rem;
                    border-radius: 5px;
                    color: white;
                    z-index: 1000;
                    animation: slideIn 0.3s ease;
                }
                .notification-success { background: #28a745; }
                .notification-error { background: #dc3545; }
                .notification-info { background: #17a2b8; }
                .notification-content { display: flex; align-items: center; gap: 0.5rem; }
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    applyDateFilter() {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        
        if (startDate && endDate) {
            this.fetchData(`/data/events?start_date=${startDate}&end_date=${endDate}`)
                .then(data => {
                    if (data) {
                        this.updateChartsWithData(data);
                        this.showNotification('Date filter applied', 'success');
                    }
                });
        }
    }

    updateChartsWithData(data) {
        // Update charts with filtered data
        if (this.charts.intensity && data.events) {
            this.charts.intensity.data.labels = data.events.map(e => 
                new Date(e.date).toLocaleDateString()
            );
            this.charts.intensity.data.datasets[0].data = data.events.map(e => e.sep_intensity);
            this.charts.intensity.update();
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new SolarDashboard();
});
