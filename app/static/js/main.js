/**
 * Main JavaScript file for Stock Analysis Tool
 * Contains common utilities and global functionality
 */

// Global app configuration
window.StockApp = {
    config: {
        apiBaseUrl: '',
        refreshInterval: 30000, // 30 seconds
        animationDuration: 300
    },
    
    // Current data cache
    cache: {
        stocks: new Map(),
        lastUpdate: null
    },
    
    // State management
    state: {
        isLoading: false,
        currentPage: location.pathname,
        watchlist: []
    }
};

// Common utility functions
window.StockApp.utils = {
    
    /**
     * Format currency value
     * @param {number} amount - Amount to format
     * @param {string} currency - Currency code (default: USD)
     * @returns {string} Formatted currency string
     */
    formatCurrency: function(amount, currency = 'USD') {
        if (amount === null || amount === undefined || isNaN(amount)) {
            return 'N/A';
        }
        
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    },

    /**
     * Format percentage value
     * @param {number} value - Percentage value
     * @param {number} decimals - Number of decimal places
     * @returns {string} Formatted percentage string
     */
    formatPercentage: function(value, decimals = 2) {
        if (value === null || value === undefined || isNaN(value)) {
            return 'N/A';
        }
        
        return value.toFixed(decimals) + '%';
    },

    /**
     * Format large numbers with K, M, B suffixes
     * @param {number} number - Number to format
     * @returns {string} Formatted number string
     */
    formatLargeNumber: function(number) {
        if (number === null || number === undefined || isNaN(number)) {
            return 'N/A';
        }
        
        const abs = Math.abs(number);
        const sign = number < 0 ? '-' : '';
        
        if (abs >= 1e12) {
            return sign + (abs / 1e12).toFixed(2) + 'T';
        } else if (abs >= 1e9) {
            return sign + (abs / 1e9).toFixed(2) + 'B';
        } else if (abs >= 1e6) {
            return sign + (abs / 1e6).toFixed(2) + 'M';
        } else if (abs >= 1e3) {
            return sign + (abs / 1e3).toFixed(2) + 'K';
        } else {
            return sign + abs.toLocaleString();
        }
    },

    /**
     * Get CSS class for price change
     * @param {number} change - Price change value
     * @returns {string} CSS class name
     */
    getChangeClass: function(change) {
        if (change === null || change === undefined || isNaN(change)) {
            return 'text-muted';
        }
        
        if (change > 0) {
            return 'text-success';
        } else if (change < 0) {
            return 'text-danger';
        } else {
            return 'text-muted';
        }
    },

    /**
     * Get change arrow icon
     * @param {number} change - Price change value
     * @returns {string} Arrow icon
     */
    getChangeArrow: function(change) {
        if (change > 0) {
            return '▲';
        } else if (change < 0) {
            return '▼';
        } else {
            return '▬';
        }
    },

    /**
     * Debounce function
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function} Debounced function
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Show loading spinner
     * @param {string} containerId - Container element ID
     */
    showLoading: function(containerId = 'main') {
        const container = document.getElementById(containerId);
        if (container) {
            const loading = document.createElement('div');
            loading.id = 'globalLoading';
            loading.className = 'loading-overlay';
            loading.innerHTML = `
                <div class="loading-content">
                    <div class="loading-spinner mx-auto mb-3"></div>
                    <p>Loading...</p>
                </div>
            `;
            container.appendChild(loading);
        }
        StockApp.state.isLoading = true;
    },

    /**
     * Hide loading spinner
     */
    hideLoading: function() {
        const loading = document.getElementById('globalLoading');
        if (loading) {
            loading.remove();
        }
        StockApp.state.isLoading = false;
    },

    /**
     * Show toast notification
     * @param {string} message - Message to show
     * @param {string} type - Toast type (success, error, warning, info)
     * @param {number} duration - Duration in milliseconds
     */
    showToast: function(message, type = 'info', duration = 3000) {
        // Remove existing toasts
        const existingToasts = document.querySelectorAll('.custom-toast');
        existingToasts.forEach(toast => toast.remove());

        // Create toast element
        const toast = document.createElement('div');
        toast.className = `custom-toast alert alert-${type} alert-dismissible fade show`;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            max-width: 500px;
            animation: slideInRight 0.3s ease;
        `;
        
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(toast);

        // Auto-remove after duration
        setTimeout(() => {
            toast.classList.add('fade');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, 300);
        }, duration);
    },

    /**
     * Validate stock symbol
     * @param {string} symbol - Stock symbol to validate
     * @returns {boolean} True if valid
     */
    isValidSymbol: function(symbol) {
        if (!symbol || typeof symbol !== 'string') {
            return false;
        }
        
        const cleanSymbol = symbol.trim().toUpperCase();
        return /^[A-Z0-9]{1,6}$/.test(cleanSymbol) && /^[A-Z]/.test(cleanSymbol);
    },

    /**
     * Format date for display
     * @param {Date|string} date - Date to format
     * @returns {string} Formatted date string
     */
    formatDate: function(date) {
        if (!date) return 'N/A';
        
        const d = new Date(date);
        if (isNaN(d.getTime())) return 'Invalid Date';
        
        return d.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    /**
     * Check if market is open (simplified)
     * @returns {boolean} True if market appears to be open
     */
    isMarketOpen: function() {
        const now = new Date();
        const day = now.getDay(); // 0 = Sunday, 6 = Saturday
        const hour = now.getHours();
        
        // Weekend check
        if (day === 0 || day === 6) {
            return false;
        }
        
        // Rough market hours (9:30 AM to 4:00 PM EST)
        if (hour >= 9 && hour < 16) {
            return true;
        }
        
        return false;
    }
};

// API helper functions
window.StockApp.api = {
    
    /**
     * Make API request with error handling
     * @param {string} url - API endpoint
     * @param {Object} options - Fetch options
     * @returns {Promise} API response
     */
    request: async function(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    /**
     * Get stock quote
     * @param {string} symbol - Stock symbol
     * @returns {Promise} Stock data
     */
    getStock: async function(symbol) {
        return this.request(`/search/api/quote/${symbol}`);
    },

    /**
     * Refresh stock data
     * @param {string} symbol - Stock symbol
     * @returns {Promise} Updated stock data
     */
    refreshStock: async function(symbol) {
        return this.request(`/stock/api/${symbol}/refresh`);
    },

    /**
     * Search stocks
     * @param {string} query - Search query
     * @returns {Promise} Search results
     */
    searchStocks: async function(query) {
        return this.request(`/search/api/suggestions?q=${encodeURIComponent(query)}`);
    }
};

// Watchlist functionality
window.StockApp.watchlist = {
    
    /**
     * Add stock to watchlist
     * @param {string} symbol - Stock symbol
     * @returns {Promise} Result
     */
    add: async function(symbol) {
        try {
            const result = await StockApp.api.request('/watchlist/api/add', {
                method: 'POST',
                body: JSON.stringify({ symbol: symbol })
            });
            
            StockApp.utils.showToast(`${symbol} added to watchlist!`, 'success');
            return result;
        } catch (error) {
            StockApp.utils.showToast(`Failed to add ${symbol} to watchlist`, 'error');
            throw error;
        }
    },

    /**
     * Remove stock from watchlist
     * @param {string} symbol - Stock symbol
     * @returns {Promise} Result
     */
    remove: async function(symbol) {
        try {
            const result = await StockApp.api.request('/watchlist/api/remove', {
                method: 'POST',
                body: JSON.stringify({ symbol: symbol })
            });
            
            StockApp.utils.showToast(`${symbol} removed from watchlist!`, 'success');
            return result;
        } catch (error) {
            StockApp.utils.showToast(`Failed to remove ${symbol} from watchlist`, 'error');
            throw error;
        }
    },

    /**
     * Get user's watchlist
     * @returns {Promise} Watchlist data
     */
    get: async function() {
        return StockApp.api.request('/watchlist/api/list');
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Stock Analysis Tool initialized');
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Auto-refresh functionality (if enabled)
    if (StockApp.config.refreshInterval > 0) {
        setInterval(() => {
            if (StockApp.utils.isMarketOpen() && !StockApp.state.isLoading) {
                // Auto-refresh current page data
                const refreshBtn = document.querySelector('[data-auto-refresh]');
                if (refreshBtn) {
                    refreshBtn.click();
                }
            }
        }, StockApp.config.refreshInterval);
    }

    // Handle network status
    window.addEventListener('online', () => {
        StockApp.utils.showToast('Connection restored', 'success');
    });

    window.addEventListener('offline', () => {
        StockApp.utils.showToast('Connection lost', 'warning');
    });
});

// Add custom CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 9998;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .loading-content {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }

    .loading-spinner {
        border: 3px solid #f3f3f3;
        border-top: 3px solid #007bff;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .custom-toast {
        animation: slideInRight 0.3s ease;
    }

    .fade-in {
        animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
`;
document.head.appendChild(style);

// Export for global access
window.StockUtils = StockApp.utils;
window.StockAPI = StockApp.api;