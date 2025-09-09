class StockSearch {
    constructor() {
        this.searchInput = document.getElementById('searchInput');
        this.searchForm = document.getElementById('searchForm');
        this.searchSuggestions = document.getElementById('searchSuggestions');
        this.searchLoading = document.getElementById('searchLoading');
        this.quoteModal = new bootstrap.Modal(document.getElementById('quoteModal'));
        
        this.debounceTimer = null;
        this.currentQuery = '';
        this.isSearching = false;
        
        this.init();
    }

    init() {
        // Setup event listeners
        this.setupSearchInput();
        this.setupFormSubmission();
        this.setupPopularStocks();
        this.setupQuoteButtons();
        this.setupClickOutside();
        
        console.log('Stock Search initialized');
    }

    setupSearchInput() {
        // Real-time search suggestions
        this.searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            
            if (query !== this.currentQuery) {
                this.currentQuery = query;
                this.debouncedSearch(query);
            }
        });

        // Handle keyboard navigation
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.navigateSuggestions('down');
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateSuggestions('up');
            } else if (e.key === 'Enter') {
                const selected = this.searchSuggestions.querySelector('.suggestion-item.selected');
                if (selected) {
                    e.preventDefault();
                    this.selectSuggestion(selected);
                }
            } else if (e.key === 'Escape') {
                this.hideSuggestions();
            }
        });

        // Show suggestions on focus if there's a query
        this.searchInput.addEventListener('focus', () => {
            if (this.currentQuery && this.searchSuggestions.children.length > 0) {
                this.showSuggestions();
            }
        });
    }

    setupFormSubmission() {
        this.searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const query = this.searchInput.value.trim();
            
            if (query) {
                this.performSearch(query);
            }
        });
    }

    setupPopularStocks() {
        const popularCards = document.querySelectorAll('.popular-stock-card');
        
        popularCards.forEach(card => {
            card.addEventListener('click', () => {
                const symbol = card.dataset.symbol;
                if (symbol) {
                    this.goToStockDetail(symbol);
                }
            });
        });
    }

    setupQuoteButtons() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('get-quote-btn')) {
                e.preventDefault();
                const symbol = e.target.dataset.symbol;
                if (symbol) {
                    this.showQuickQuote(symbol);
                }
            }
        });
    }

    setupClickOutside() {
        document.addEventListener('click', (e) => {
            if (!this.searchInput.contains(e.target) && !this.searchSuggestions.contains(e.target)) {
                this.hideSuggestions();
            }
        });
    }

    debouncedSearch(query) {
        // Clear previous timer
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }

        // Set new timer
        this.debounceTimer = setTimeout(() => {
            if (query.length >= 1) {
                this.fetchSuggestions(query);
            } else {
                this.hideSuggestions();
            }
        }, 300); // 300ms delay
    }

    async fetchSuggestions(query) {
        if (this.isSearching) return;

        this.isSearching = true;
        this.showLoading();

        try {
            const response = await fetch(`/search/api/suggestions?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.error) {
                this.showError(data.error);
                return;
            }

            this.displaySuggestions(data.results || []);
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Search failed. Please try again.');
        } finally {
            this.hideLoading();
            this.isSearching = false;
        }
    }

    displaySuggestions(suggestions) {
        this.searchSuggestions.innerHTML = '';

        if (suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }

        suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.innerHTML = `
                <div class="suggestion-symbol">${suggestion.symbol}</div>
                <div class="suggestion-name">${suggestion.name}</div>
            `;

            item.addEventListener('click', () => {
                this.selectSuggestion(item);
            });

            // Store suggestion data
            item.dataset.symbol = suggestion.symbol;
            item.dataset.name = suggestion.name;

            this.searchSuggestions.appendChild(item);
        });

        this.showSuggestions();
    }

    selectSuggestion(item) {
        const symbol = item.dataset.symbol;
        const name = item.dataset.name;

        // Update search input
        this.searchInput.value = symbol;
        this.currentQuery = symbol;

        // Hide suggestions
        this.hideSuggestions();

        // Navigate to stock detail
        this.goToStockDetail(symbol);
    }

    navigateSuggestions(direction) {
        const items = this.searchSuggestions.querySelectorAll('.suggestion-item');
        const selected = this.searchSuggestions.querySelector('.suggestion-item.selected');
        
        if (items.length === 0) return;

        let newIndex = 0;

        if (selected) {
            const currentIndex = Array.from(items).indexOf(selected);
            selected.classList.remove('selected');

            if (direction === 'down') {
                newIndex = (currentIndex + 1) % items.length;
            } else {
                newIndex = currentIndex === 0 ? items.length - 1 : currentIndex - 1;
            }
        }

        items[newIndex].classList.add('selected');
    }

    async showQuickQuote(symbol) {
        // Update modal title
        document.getElementById('quoteModalTitle').textContent = `${symbol} Quote`;
        
        // Show loading state
        document.getElementById('quoteModalBody').innerHTML = `
            <div class="text-center">
                <div class="loading-spinner mx-auto mb-3"></div>
                <p>Loading quote for ${symbol}...</p>
            </div>
        `;

        // Update detail button
        const detailBtn = document.getElementById('quoteModalDetailBtn');
        detailBtn.href = `/stock/${symbol}`;

        // Show modal
        this.quoteModal.show();

        try {
            const response = await fetch(`/search/api/quote/${symbol}`);
            const data = await response.json();

            if (data.error) {
                this.displayQuoteError(data.error);
                return;
            }

            this.displayQuote(data.stock);
        } catch (error) {
            console.error('Quote error:', error);
            this.displayQuoteError('Failed to load quote. Please try again.');
        }
    }

    displayQuote(stock) {
        const changeClass = stock.day_change >= 0 ? 'text-success' : 'text-danger';
        const changeIcon = stock.day_change >= 0 ? '▲' : '▼';

        document.getElementById('quoteModalBody').innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h5>${stock.company_name}</h5>
                    <p class="text-muted mb-1">${stock.symbol} • ${stock.exchange || 'N/A'}</p>
                    <p class="text-muted">${stock.sector || 'N/A'}</p>
                </div>
                <div class="col-md-6 text-end">
                    <h3 class="mb-1">$${stock.current_price ? stock.current_price.toFixed(2) : 'N/A'}</h3>
                    ${stock.day_change ? `
                        <p class="${changeClass} mb-0">
                            ${changeIcon} $${Math.abs(stock.day_change).toFixed(2)} 
                            (${stock.day_change_percent ? stock.day_change_percent.toFixed(2) : 'N/A'}%)
                        </p>
                    ` : ''}
                    <small class="text-muted">
                        ${stock.last_updated ? new Date(stock.last_updated).toLocaleString() : 'Unknown time'}
                    </small>
                </div>
            </div>
            
            <hr>
            
            <div class="row">
                <div class="col-6">
                    <small class="text-muted">Previous Close</small>
                    <div>$${stock.previous_close ? stock.previous_close.toFixed(2) : 'N/A'}</div>
                </div>
                <div class="col-6">
                    <small class="text-muted">Market Cap</small>
                    <div>${stock.formatted_market_cap || 'N/A'}</div>
                </div>
                <div class="col-6 mt-2">
                    <small class="text-muted">Day Range</small>
                    <div>$${stock.day_low || 'N/A'} - $${stock.day_high || 'N/A'}</div>
                </div>
                <div class="col-6 mt-2">
                    <small class="text-muted">Volume</small>
                    <div>${stock.volume ? stock.volume.toLocaleString() : 'N/A'}</div>
                </div>
            </div>
        `;
    }

    displayQuoteError(error) {
        document.getElementById('quoteModalBody').innerHTML = `
            <div class="alert alert-danger" role="alert">
                <h6 class="alert-heading">Error Loading Quote</h6>
                <p class="mb-0">${error}</p>
            </div>
        `;
    }

    performSearch(query) {
        // Redirect to search results page
        window.location.href = `/search/results?q=${encodeURIComponent(query)}`;
    }

    goToStockDetail(symbol) {
        window.location.href = `/stock/${symbol}`;
    }

    showSuggestions() {
        this.searchSuggestions.style.display = 'block';
    }

    hideSuggestions() {
        this.searchSuggestions.style.display = 'none';
        // Remove all selected classes
        this.searchSuggestions.querySelectorAll('.selected').forEach(item => {
            item.classList.remove('selected');
        });
    }

    showLoading() {
        this.searchLoading.style.display = 'block';
    }

    hideLoading() {
        this.searchLoading.style.display = 'none';
    }

    showError(message) {
        // Create temporary error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-warning alert-dismissible fade show mt-2';
        errorDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert after search form
        this.searchForm.parentNode.insertBefore(errorDiv, this.searchForm.nextSibling);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new StockSearch();
});

// Utility functions for other pages
window.StockSearchUtils = {
    formatCurrency: (amount) => {
        if (amount === null || amount === undefined) return 'N/A';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },

    formatPercentage: (value) => {
        if (value === null || value === undefined) return 'N/A';
        return `${value.toFixed(2)}%`;
    },

    formatLargeNumber: (number) => {
        if (number === null || number === undefined) return 'N/A';
        
        if (number >= 1e12) return `${(number / 1e12).toFixed(2)}T`;
        if (number >= 1e9) return `${(number / 1e9).toFixed(2)}B`;
        if (number >= 1e6) return `${(number / 1e6).toFixed(2)}M`;
        if (number >= 1e3) return `${(number / 1e3).toFixed(2)}K`;
        
        return number.toLocaleString();
    }
};