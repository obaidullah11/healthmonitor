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
        // Form submission (unified assessment)
        const form = document.getElementById('healthForm');
        form.addEventListener('submit', (e) => this.handleUnifiedAssessment(e));

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

    async handleUnifiedAssessment(e) {
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
            const response = await this.predictCompleteHealth(healthData);
            this.hideLoading();
            this.displayUnifiedResults(response);
            
            // Log the complete response for debugging
            console.log('Unified Health Assessment Response:', response);
        } catch (error) {
            this.hideLoading();
            this.showNotification('Error: ' + error.message, 'error');
        }
    }

    async predictCompleteHealth(healthData) {
        const response = await fetch(`${this.apiBaseUrl}/predict-complete-health`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(healthData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Failed to get complete health assessment');
        }

        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.message || 'Complete health assessment failed');
        }

        return data.data;
    }

    // Keep old methods for backward compatibility (if needed)
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

    async handleHeartDiseaseAssessment(e) {
        e.preventDefault();

        // Get form data
        const form = document.getElementById('healthForm');
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
            const response = await this.predictHeartDiseaseRisk(healthData);
            this.hideLoading();
            this.displayHeartDiseaseResults(response);
        } catch (error) {
            this.hideLoading();
            this.showNotification('Error: ' + error.message, 'error');
        }
    }

    async predictHeartDiseaseRisk(healthData) {
        const response = await fetch(`${this.apiBaseUrl}/predict-heart-disease`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(healthData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Failed to assess heart disease risk');
        }

        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.message || 'Risk assessment failed');
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

        // Add heart disease assessment if available
        if (results.heart_disease_assessment) {
            // Check if heart disease summary already exists, if so remove it
            const existingSummary = document.getElementById('heartDiseaseSummary');
            if (existingSummary) {
                existingSummary.remove();
            }
            
            // Create heart disease summary element
            const heartDiseaseDiv = document.createElement('div');
            heartDiseaseDiv.id = 'heartDiseaseSummary';
            heartDiseaseDiv.className = 'heart-disease-summary';
            heartDiseaseDiv.innerHTML = `
                <h4 style="margin-top: 20px; color: #e74c3c;">
                    <i class="fas fa-heart"></i> Cardiovascular Risk Assessment
                </h4>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 10px;">
                    <p style="font-size: 1.2rem; margin: 0;">
                        <strong>Risk Level:</strong> 
                        <span style="color: ${this.getRiskColor(results.heart_disease_assessment.risk_level)}">
                            ${results.heart_disease_assessment.risk_level}
                        </span>
                        (${results.heart_disease_assessment.risk_percentage}% 10-year risk)
                    </p>
                    ${results.heart_disease_assessment.major_risk_factors.length > 0 ? `
                        <p style="margin: 10px 0 0 0;"><strong>Major Risk Factors:</strong> 
                            ${results.heart_disease_assessment.major_risk_factors.join(', ')}
                        </p>` : ''}
                    ${results.heart_disease_assessment.primary_recommendation ? `
                        <p style="margin: 10px 0 0 0; color: #666;">
                            <strong>Recommendation:</strong> ${results.heart_disease_assessment.primary_recommendation}
                        </p>` : ''}
                </div>
            `;
            
            // Append to prediction card
            const predictionCard = document.getElementById('predictionCard');
            predictionCard.appendChild(heartDiseaseDiv);
        }

        // Show results
        container.style.display = 'block';
        container.scrollIntoView({ behavior: 'smooth' });

        // Show success notification
        this.showNotification('Health prediction completed successfully!', 'success');
    }

    getRiskColor(riskLevel) {
        const colors = {
            'Low': '#28a745',
            'Moderate': '#ffc107',
            'High': '#fd7e14',
            'Very High': '#dc3545'
        };
        return colors[riskLevel] || '#666';
    }

    displayHeartDiseaseResults(results) {
        const container = document.getElementById('resultsContainer');
        
        // Clear existing content and add heart disease specific display
        const predictionCard = document.getElementById('predictionCard');
        
        // Create heart disease specific HTML
        const heartDiseaseHTML = `
            <div class="heart-disease-results">
                <div class="risk-level-container ${results.risk_level.toLowerCase().replace(' ', '-')}">
                    <i class="fas fa-heart risk-icon"></i>
                    <h3 class="risk-level">${results.risk_level} Risk</h3>
                    <p class="risk-percentage">${results.risk_percentage}% 10-year cardiovascular risk</p>
                    <div class="confidence-badge">Confidence: ${(results.confidence_score * 100).toFixed(1)}%</div>
                </div>
                
                <div class="risk-factors-section">
                    <h4><i class="fas fa-list-check"></i> Identified Risk Factors</h4>
                    <div class="risk-factors-grid">
                        ${results.risk_factors.map(factor => `
                            <div class="risk-factor-item ${factor.severity.toLowerCase()}">
                                <div class="factor-header">
                                    <span class="factor-name">${factor.factor}</span>
                                    <span class="factor-severity severity-${factor.severity.toLowerCase()}">${factor.severity}</span>
                                </div>
                                <div class="factor-details">
                                    <span class="current-value">Current: ${factor.value}</span>
                                    <span class="target-value">Target: ${factor.target}</span>
                                    ${factor.modifiable ? '<span class="modifiable-badge">Modifiable</span>' : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="recommendations-section">
                    <h4><i class="fas fa-clipboard-list"></i> Personalized Recommendations</h4>
                    <ul class="recommendations-list">
                        ${results.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
                
                <div class="risk-scores-detail">
                    <h4><i class="fas fa-chart-line"></i> Risk Assessment Details</h4>
                    <div class="scores-grid">
                        <div class="score-item">
                            <span class="score-label">Traditional Risk Score:</span>
                            <span class="score-value">${results.risk_scores.traditional.level} (${results.risk_scores.traditional.factors.length} factors)</span>
                        </div>
                        <div class="score-item">
                            <span class="score-label">Framingham Score:</span>
                            <span class="score-value">${results.risk_scores.framingham.percentage}%</span>
                        </div>
                        <div class="score-item">
                            <span class="score-label">AI Assessment:</span>
                            <span class="score-value">${results.risk_scores.ai_based.percentage}% (${results.risk_scores.ai_based.ml_based ? 'ML-based' : 'Pattern-based'})</span>
                        </div>
                    </div>
                </div>
                
                <div class="processing-info">
                    <small>Assessment completed in ${results.processing_time_ms}ms</small>
                </div>
            </div>
        `;
        
        // Replace the prediction card content
        predictionCard.innerHTML = heartDiseaseHTML;
        
        // Show results
        container.style.display = 'block';
        container.scrollIntoView({ behavior: 'smooth' });
        
        // Show appropriate notification based on risk level
        const notificationMessages = {
            'Low': 'Good news! Your cardiovascular risk is low. Keep up the healthy lifestyle!',
            'Moderate': 'Your cardiovascular risk is moderate. Consider the recommendations provided.',
            'High': 'Your cardiovascular risk is high. Please consult with a healthcare provider soon.',
            'Very High': 'Your cardiovascular risk is very high. Seek medical attention promptly.'
        };
        
        const notificationType = results.risk_level === 'Low' ? 'success' : 
                               results.risk_level === 'Moderate' ? 'warning' : 'error';
        
        this.showNotification(notificationMessages[results.risk_level] || 'Assessment completed', notificationType);
    }

    displayUnifiedResults(results) {
        const container = document.getElementById('resultsContainer');
        const predictionCard = document.getElementById('predictionCard');
        
        // Extract data from unified response
        const generalHealth = results.general_health_assessment;
        const cvdAssessment = results.comprehensive_cvd_assessment;
        const meta = results.combined_meta;
        
        // Create unified results HTML
        const unifiedHTML = `
            <div class="unified-results">
                <!-- General Health Status Section -->
                <div class="general-health-section">
                    <div class="section-header">
                        <h3><i class="fas fa-stethoscope"></i> General Health Status</h3>
                    </div>
                    <div class="status-indicator ${generalHealth.health_status.toLowerCase()}">
                        <i class="status-icon ${this.getStatusIcon(generalHealth.health_status)}"></i>
                        <span class="status-text">${generalHealth.health_status}</span>
                    </div>
                    <div class="confidence-meter">
                        <label>Confidence Score</label>
                        <div class="meter-container">
                            <div class="meter-fill" style="width: ${generalHealth.confidence_score * 100}%"></div>
                            <span class="confidence-text">${(generalHealth.confidence_score * 100).toFixed(1)}%</span>
                        </div>
                    </div>
                    <div class="suggested-action">
                        <h4>Immediate Action</h4>
                        <p>${generalHealth.suggested_action}</p>
                    </div>
                    <div class="risk-summary">
                        <h4>CVD Risk Summary</h4>
                        <p><strong>Risk Level:</strong> <span style="color: ${this.getRiskColor(generalHealth.risk_summary.risk_level)}">${generalHealth.risk_summary.risk_level}</span> (${generalHealth.risk_summary.risk_percentage}%)</p>
                        ${generalHealth.risk_summary.major_risk_factors.length > 0 ? `
                            <p><strong>Major Risk Factors:</strong> ${generalHealth.risk_summary.major_risk_factors.join(', ')}</p>
                        ` : ''}
                    </div>
                </div>
                
                <!-- Comprehensive CVD Assessment Section -->
                <div class="cvd-assessment-section">
                    <div class="section-header">
                        <h3><i class="fas fa-heart"></i> Comprehensive Cardiovascular Risk Analysis</h3>
                    </div>
                    <div class="risk-level-container ${cvdAssessment.risk_level.toLowerCase().replace(' ', '-')}">
                        <i class="fas fa-heart risk-icon"></i>
                        <h4 class="risk-level">${cvdAssessment.risk_level} Risk</h4>
                        <p class="risk-percentage">${cvdAssessment.risk_percentage}% 10-year cardiovascular risk</p>
                        <div class="confidence-badge">Confidence: ${(cvdAssessment.confidence_score * 100).toFixed(1)}%</div>
                    </div>
                    
                    <div class="risk-factors-section">
                        <h4><i class="fas fa-list-check"></i> Identified Risk Factors</h4>
                        <div class="risk-factors-grid">
                            ${cvdAssessment.risk_factors.map(factor => `
                                <div class="risk-factor-item ${factor.severity.toLowerCase()}">
                                    <div class="factor-header">
                                        <span class="factor-name">${factor.factor}</span>
                                        <span class="factor-severity severity-${factor.severity.toLowerCase()}">${factor.severity}</span>
                                    </div>
                                    <div class="factor-details">
                                        <span class="current-value">Current: ${factor.value}</span>
                                        <span class="target-value">Target: ${factor.target}</span>
                                        ${factor.modifiable ? '<span class="modifiable-badge">Modifiable</span>' : ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="recommendations-section">
                        <h4><i class="fas fa-clipboard-list"></i> Personalized Recommendations</h4>
                        <ul class="recommendations-list">
                            ${cvdAssessment.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <div class="risk-scores-detail">
                        <h4><i class="fas fa-chart-line"></i> Risk Assessment Methods</h4>
                        <div class="scores-grid">
                            <div class="score-item">
                                <span class="score-label">Traditional Risk:</span>
                                <span class="score-value">${cvdAssessment.risk_scores.traditional.level} (${cvdAssessment.risk_scores.traditional.factors.length} factors)</span>
                            </div>
                            <div class="score-item">
                                <span class="score-label">Framingham Score:</span>
                                <span class="score-value">${cvdAssessment.risk_scores.framingham.percentage}%</span>
                            </div>
                            <div class="score-item">
                                <span class="score-label">AI Assessment:</span>
                                <span class="score-value">${cvdAssessment.risk_scores.ai_based.percentage}% (${cvdAssessment.risk_scores.ai_based.ml_based ? 'ML-based' : 'Pattern-based'})</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Metadata Section -->
                <div class="metadata-section">
                    <h4><i class="fas fa-info-circle"></i> Assessment Details</h4>
                    <div class="metadata-grid">
                        <div class="meta-item">
                            <span class="meta-label">Total Processing Time:</span>
                            <span class="meta-value">${meta.total_processing_time_ms}ms</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">General Health Model:</span>
                            <span class="meta-value">${meta.models_used.general_health.replace('_', ' ').toUpperCase()}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">CVD Assessment:</span>
                            <span class="meta-value">${meta.models_used.cvd_assessment}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">API Version:</span>
                            <span class="meta-value">${meta.api_version}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Replace the prediction card content
        predictionCard.innerHTML = unifiedHTML;
        
        // Show results
        container.style.display = 'block';
        container.scrollIntoView({ behavior: 'smooth' });
        
        // Show appropriate notification based on overall risk
        const overallRisk = cvdAssessment.risk_level;
        const healthStatus = generalHealth.health_status;
        
        let notificationMessage = 'Complete health assessment completed successfully!';
        let notificationType = 'success';
        
        if (healthStatus === 'Critical' || overallRisk === 'Very High') {
            notificationMessage = 'Critical health indicators detected. Seek immediate medical attention!';
            notificationType = 'error';
        } else if (healthStatus === 'Warning' || overallRisk === 'High') {
            notificationMessage = 'Health concerns identified. Please consult with a healthcare provider.';
            notificationType = 'warning';
        } else if (overallRisk === 'Moderate') {
            notificationMessage = 'Moderate cardiovascular risk detected. Review recommendations.';
            notificationType = 'warning';
        }
        
        this.showNotification(notificationMessage, notificationType);
    }
    
    getStatusIcon(status) {
        const icons = {
            'Normal': 'fas fa-check-circle',
            'Warning': 'fas fa-exclamation-triangle',
            'Critical': 'fas fa-times-circle'
        };
        return icons[status] || icons['Normal'];
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



