// Health Monitoring System Frontend JavaScript

class HealthMonitor {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api/v1';
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupFormValidation();
    }

    bindEvents() {
        // Form submission
        const form = document.getElementById('healthForm');
        form.addEventListener('submit', (e) => this.handleFormSubmit(e));

        // Close results
        const closeBtn = document.getElementById('closeResults');
        closeBtn.addEventListener('click', () => this.hideResults());

        // Real-time validation
        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('input', () => this.validateInput(input));
            input.addEventListener('blur', () => this.validateInput(input));
        });
    }

    setupFormValidation() {
        // Custom validation messages
        const inputs = document.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('invalid', (e) => {
                e.preventDefault();
                this.showInputError(input, input.validationMessage);
            });
        });
    }

    validateInput(input) {
        const value = parseFloat(input.value);
        const min = parseFloat(input.min);
        const max = parseFloat(input.max);

        // Remove existing error styling
        input.classList.remove('error');
        this.removeInputError(input);

        // Check if value is within range
        if (input.value && (value < min || value > max)) {
            input.classList.add('error');
            this.showInputError(input, `Value must be between ${min} and ${max}`);
            return false;
        }

        return true;
    }

    showInputError(input, message) {
        // Remove existing error
        this.removeInputError(input);

        // Create error element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'input-error';
        errorDiv.textContent = message;
        errorDiv.style.color = '#ff6b6b';
        errorDiv.style.fontSize = '0.9rem';
        errorDiv.style.marginTop = '5px';

        // Insert after input
        input.parentNode.insertBefore(errorDiv, input.nextSibling);
    }

    removeInputError(input) {
        const existingError = input.parentNode.querySelector('.input-error');
        if (existingError) {
            existingError.remove();
        }
    }

    async handleFormSubmit(e) {
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);

        // Validate all inputs
        const inputs = form.querySelectorAll('input');
        let isValid = true;
        inputs.forEach(input => {
            if (!this.validateInput(input)) {
                isValid = false;
            }
        });

        if (!isValid) {
            this.showNotification('Please correct the errors in the form.', 'error');
            return;
        }

        // Validate blood pressure relationship
        const systolic = parseFloat(formData.get('bpSystolic'));
        const diastolic = parseFloat(formData.get('bpDiastolic'));
        
        if (systolic && diastolic && systolic <= diastolic) {
            this.showNotification('Systolic pressure must be higher than diastolic pressure', 'error');
            return;
        }

        // Prepare data
        const healthData = {
            heart_rate: parseFloat(formData.get('heartRate')),
            temperature: parseFloat(formData.get('temperature')),
            spo2: parseFloat(formData.get('spo2')),
            age: parseInt(formData.get('age')),
            blood_pressure_systolic: systolic,
            blood_pressure_diastolic: diastolic,
            cholesterol: parseFloat(formData.get('cholesterol'))
        };

        // Show loading
        this.showLoading();

        try {
            const response = await this.predictHealth(healthData);
            this.hideLoading();
            this.displayResults(response);
        } catch (error) {
            this.hideLoading();
            this.showNotification('Error: ' + error.message, 'error');
        }
    }

    async predictHealth(healthData) {
        const response = await fetch(`${this.apiBaseUrl}/predict-health`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(healthData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Failed to get prediction');
        }

        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.message || 'Prediction failed');
        }

        return data.data;
    }

    displayResults(results) {
        const container = document.getElementById('resultsContainer');
        const statusIndicator = document.getElementById('statusIndicator');
        const statusIcon = document.getElementById('statusIcon');
        const statusText = document.getElementById('statusText');
        const confidenceMeter = document.getElementById('confidenceMeter');
        const confidenceText = document.getElementById('confidenceText');
        const suggestedAction = document.getElementById('suggestedAction');
        const modelUsed = document.getElementById('modelUsed');
        const responseTime = document.getElementById('responseTime');

        // Set status
        const status = results.health_status.toLowerCase();
        statusIndicator.className = `status-indicator ${status}`;
        
        // Set status icon and text
        const statusConfig = {
            normal: { icon: 'fas fa-check-circle', text: 'Normal' },
            warning: { icon: 'fas fa-exclamation-triangle', text: 'Warning' },
            critical: { icon: 'fas fa-times-circle', text: 'Critical' }
        };

        const config = statusConfig[status] || statusConfig.normal;
        statusIcon.className = `status-icon ${config.icon}`;
        statusText.textContent = config.text;

        // Set confidence meter
        const confidence = results.confidence_score * 100;
        confidenceMeter.style.width = `${confidence}%`;
        confidenceText.textContent = `${confidence.toFixed(1)}%`;

        // Set suggested action
        suggestedAction.textContent = results.suggested_action;

        // Set prediction details
        modelUsed.textContent = results.prediction_details.model_used.replace('_', ' ').toUpperCase();
        responseTime.textContent = `${results.prediction_details.prediction_time_ms}ms`;

        // Show results
        container.style.display = 'block';
        container.scrollIntoView({ behavior: 'smooth' });

        // Show success notification
        this.showNotification('Health prediction completed successfully!', 'success');
    }

    hideResults() {
        const container = document.getElementById('resultsContainer');
        container.style.display = 'none';
    }

    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = 'flex';
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = 'none';
    }

    showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(notification => notification.remove());

        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="notification-icon ${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${this.getNotificationColor(type)};
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            z-index: 1001;
            max-width: 400px;
            animation: slideIn 0.3s ease;
        `;

        // Add animation styles
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            .notification-content {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .notification-icon {
                font-size: 1.2rem;
            }
            .notification-close {
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                margin-left: auto;
                padding: 5px;
            }
        `;
        document.head.appendChild(style);

        // Add to page
        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-times-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    getNotificationColor(type) {
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        return colors[type] || colors.info;
    }

    // Utility method to test API connection
    async testConnection() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            const data = await response.json();
            return data.success;
        } catch (error) {
            return false;
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const healthMonitor = new HealthMonitor();
    
    // Test API connection on load
    healthMonitor.testConnection().then(isConnected => {
        if (!isConnected) {
            healthMonitor.showNotification(
                'Warning: Cannot connect to the API server. Please ensure the backend is running.',
                'warning'
            );
        }
    });
});

// Add some additional utility functions
window.HealthMonitorUtils = {
    // Format numbers for display
    formatNumber: (num, decimals = 1) => {
        return parseFloat(num).toFixed(decimals);
    },

    // Get status color
    getStatusColor: (status) => {
        const colors = {
            normal: '#28a745',
            warning: '#ffc107',
            critical: '#dc3545'
        };
        return colors[status.toLowerCase()] || colors.normal;
    },

    // Validate health ranges
    validateHealthRanges: (heartRate, temperature, spo2) => {
        const errors = [];
        
        if (heartRate < 30 || heartRate > 200) {
            errors.push('Heart rate must be between 30 and 200 BPM');
        }
        
        if (temperature < 35.0 || temperature > 42.0) {
            errors.push('Temperature must be between 35.0 and 42.0°C');
        }
        
        if (spo2 < 70 || spo2 > 100) {
            errors.push('SpO2 must be between 70 and 100%');
        }
        
        return errors;
    }
};



