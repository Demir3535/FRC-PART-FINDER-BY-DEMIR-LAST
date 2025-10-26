// FRC Parts Finder - UI Integration
// Bu dosya yeni özellikleri mevcut app.js ile entegre eder

// ============================================
// FILTER PANEL TOGGLE
// ============================================

function toggleFilters() {
    const panel = document.getElementById('filterPanel');
    if (panel.style.display === 'none' || panel.style.display === '') {
        panel.style.display = 'block';
    } else {
        panel.style.display = 'none';
    }
}

// ============================================
// FILTER INTERACTIONS
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Category filter tags
    const categoryTags = document.querySelectorAll('#categoryFilters .filter-tag');
    categoryTags.forEach(tag => {
        tag.addEventListener('click', function() {
            const alreadyActive = this.classList.contains('active');
            categoryTags.forEach(t => t.classList.remove('active'));

            if (alreadyActive) {
                searchFilter.setCategory(null);
            } else {
                this.classList.add('active');
                const category = this.getAttribute('data-category');
                searchFilter.setCategory(category);
            }
        });
    });

    // Stock filter tags
    const stockTags = document.querySelectorAll('[data-stock]');
    stockTags.forEach(tag => {
        tag.addEventListener('click', function() {
            const alreadyActive = this.classList.contains('active');
            stockTags.forEach(t => t.classList.remove('active'));

            if (alreadyActive) {
                searchFilter.setStockFilter(null);
            } else {
                this.classList.add('active');
                const stockFilter = this.getAttribute('data-stock');
                if (stockFilter === 'in-stock') {
                    searchFilter.setStockFilter(true);
                } else {
                    searchFilter.setStockFilter(null);
                }
            }
        });
    });
});

// ============================================
// APPLY & RESET FILTERS
// ============================================

function applyFilters() {
    const minPrice = parseFloat(document.getElementById('minPrice').value) || 0;
    const maxPrice = parseFloat(document.getElementById('maxPrice').value) || Infinity;

    searchFilter.setPriceRange(minPrice, maxPrice);

    // Re-display current results with filters applied
    const currentResults = window.lastSearchResults || [];
    const filtered = searchFilter.applyFilters(currentResults);

    displayResults(filtered, 'filtered');

    // Show notification
    showNotification(`Filters applied! Showing ${filtered.length} results.`);
}

function resetFilters() {
    searchFilter.reset();

    // Reset UI
    document.getElementById('minPrice').value = '0';
    document.getElementById('maxPrice').value = '1000';
    document.querySelectorAll('.filter-tag.active').forEach(tag => {
        tag.classList.remove('active');
    });

    // Re-display original results
    const originalResults = window.lastSearchResults || [];
    displayResults(originalResults, 'reset');

    showNotification('Filters reset!');
}

// ============================================
// ENHANCED PART CARD CREATION
// ============================================

// Override the original createPartCard function to add new features
const originalCreatePartCard = window.createPartCard;

window.createPartCard = function(part, isCheapest = false) {
    const card = originalCreatePartCard ? originalCreatePartCard(part, isCheapest) : document.createElement('div');

    // Find the part-info section
    const partInfo = card.querySelector('.part-info');
    if (!partInfo) return card;

    // Add action buttons
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'product-actions';
    actionsDiv.innerHTML = `
        <button class="action-btn btn-compare" onclick='addToCompare(${JSON.stringify(part).replace(/'/g, "&apos;")})'>
            <i class="fas fa-balance-scale"></i> Compare
        </button>
        <button class="action-btn btn-add-bom" onclick='addToBOM(${JSON.stringify(part).replace(/'/g, "&apos;")})'>
            <i class="fas fa-cart-plus"></i> Add to BOM
        </button>
    `;

    // Add CAD link if available
    if (part.cadUrl) {
        actionsDiv.innerHTML += `
            <button class="action-btn btn-cad" onclick="window.open('${part.cadUrl}', '_blank')">
                <i class="fas fa-cube"></i> CAD
            </button>
        `;
    }

    partInfo.appendChild(actionsDiv);

    // Add price history if available
    const productId = part.name.toLowerCase().replace(/\s+/g, '-');
    priceTracker.trackPrice(productId, part.vendor, part.price);

    const priceHistory = priceTracker.getPriceHistory(productId, part.vendor);
    if (priceHistory.length > 1) {
        const lowest = priceTracker.getLowestPrice(productId, part.vendor);
        const dropPercent = priceTracker.getPriceDropPercentage(productId, part.vendor, part.price);

        if (dropPercent > 0) {
            const priceSection = card.querySelector('.price-section');
            if (priceSection) {
                const dropBadge = document.createElement('span');
                dropBadge.className = 'price-drop-badge';
                dropBadge.innerHTML = `<i class="fas fa-arrow-down"></i> ${dropPercent}% from lowest ($${lowest.toFixed(2)})`;
                priceSection.appendChild(dropBadge);
            }
        }
    }

    // Add rating stars if reviews exist
    const rating = communityFeatures.getAverageRating(productId);
    if (rating > 0) {
        const ratingDiv = document.createElement('div');
        ratingDiv.className = 'rating-summary';
        ratingDiv.innerHTML = generateStars(rating) + ` <span>(${rating}/5.0)</span>`;

        const vendorDiv = card.querySelector('.part-vendor');
        if (vendorDiv) {
            vendorDiv.parentNode.insertBefore(ratingDiv, vendorDiv.nextSibling);
        }
    }

    return card;
};

// ============================================
// HELPER FUNCTIONS
// ============================================

function addToCompare(product) {
    const success = productComparison.addToCompare(product);
    if (success) {
        showNotification(`${product.name} added to comparison!`);
    } else {
        showNotification('Product already in comparison or limit reached!', 'warning');
    }
}

function addToBOM(product) {
    bomBuilder.addToBOM(product, 1);
    showNotification(`${product.name} added to BOM!`);
}

function generateStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    let html = '<span class="rating-stars">';

    for (let i = 0; i < fullStars; i++) {
        html += '<i class="fas fa-star"></i>';
    }

    if (hasHalfStar) {
        html += '<i class="fas fa-star-half-alt"></i>';
    }

    for (let i = 0; i < emptyStars; i++) {
        html += '<i class="far fa-star"></i>';
    }

    html += '</span>';
    return html;
}

function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
    `;

    // Add to body
    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Add notification styles dynamically
const notificationStyles = `
<style>
.notification {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: white;
    padding: 15px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    display: flex;
    align-items: center;
    gap: 10px;
    transform: translateY(100px);
    opacity: 0;
    transition: all 0.3s ease;
    z-index: 10001;
    max-width: 400px;
}

.notification.show {
    transform: translateY(0);
    opacity: 1;
}

.notification-success {
    border-left: 4px solid #10b981;
    color: #10b981;
}

.notification-warning {
    border-left: 4px solid #f59e0b;
    color: #f59e0b;
}

.notification i {
    font-size: 20px;
}

.notification span {
    color: var(--text-color);
    font-weight: 500;
}

.dark-mode .notification {
    background: #1e293b;
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', notificationStyles);

// ============================================
// STORE LAST SEARCH RESULTS
// ============================================

// Override displayResults to store results
const originalDisplayResults = window.displayResults;
if (originalDisplayResults) {
    window.displayResults = function(results, source) {
        window.lastSearchResults = results;
        originalDisplayResults(results, source);
    };
}

// ============================================
// NEW VENDOR INTEGRATION
// ============================================

// Load enhanced schema and add new vendors
async function loadEnhancedVendors() {
    try {
        const response = await fetch('./data/enhanced-schema.json');
        if (!response.ok) return;

        const schema = await response.json();
        const newVendors = schema.newVendors;

        // Merge with existing VENDORS object
        if (window.VENDORS && newVendors) {
            Object.assign(window.VENDORS, newVendors);
            console.log('✅ New vendors loaded:', Object.keys(newVendors));
        }
    } catch (error) {
        console.log('Enhanced vendors not loaded:', error);
    }
}

// Call on page load
document.addEventListener('DOMContentLoaded', function() {
    loadEnhancedVendors();

    console.log('✅ UI Integration loaded!');
    console.log('✅ Advanced filters ready');
    console.log('✅ Comparison tool ready');
    console.log('✅ BOM Builder ready');
    console.log('✅ Calculators ready');
});

// ============================================
// AUTOCOMPLETE SUGGESTIONS
// ============================================

const searchInput = document.getElementById('searchInput');
let autocompleteTimeout;

if (searchInput) {
    searchInput.addEventListener('input', function() {
        clearTimeout(autocompleteTimeout);
        const query = this.value.trim();

        if (query.length < 2) {
            hideAutocomplete();
            return;
        }

        autocompleteTimeout = setTimeout(() => {
            showAutocompleteSuggestions(query);
        }, 300);
    });
}

async function showAutocompleteSuggestions(query) {
    const database = await loadProductsDatabase();
    if (!database) return;

    const matches = [];
    const queryLower = query.toLowerCase();

    // Find matching product keys
    for (const key of Object.keys(database)) {
        if (key.includes(queryLower)) {
            matches.push(key);
        }
        if (matches.length >= 5) break;
    }

    if (matches.length > 0) {
        displayAutocomplete(matches);
    } else {
        hideAutocomplete();
    }
}

function displayAutocomplete(suggestions) {
    let container = document.getElementById('autocomplete-container');

    if (!container) {
        container = document.createElement('div');
        container.id = 'autocomplete-container';
        container.className = 'autocomplete-dropdown';
        searchInput.parentNode.appendChild(container);
    }

    container.innerHTML = suggestions.map(suggestion => `
        <div class="autocomplete-item" onclick="selectSuggestion('${suggestion}')">
            <i class="fas fa-search"></i> ${suggestion}
        </div>
    `).join('');

    container.style.display = 'block';
}

function hideAutocomplete() {
    const container = document.getElementById('autocomplete-container');
    if (container) {
        container.style.display = 'none';
    }
}

function selectSuggestion(suggestion) {
    searchInput.value = suggestion;
    hideAutocomplete();
    searchParts();
}

// Add autocomplete styles
const autocompleteStyles = `
<style>
.autocomplete-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 0 0 8px 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    max-height: 300px;
    overflow-y: auto;
    margin-top: -1px;
}

.autocomplete-item {
    padding: 12px 16px;
    cursor: pointer;
    border-bottom: 1px solid var(--border-color);
    transition: background 0.2s;
    display: flex;
    align-items: center;
    gap: 10px;
}

.autocomplete-item:hover {
    background: var(--bg-light);
}

.autocomplete-item i {
    color: var(--primary-color);
}

.autocomplete-item:last-child {
    border-bottom: none;
}

.search-box {
    position: relative;
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', autocompleteStyles);

// Close autocomplete when clicking outside
document.addEventListener('click', function(e) {
    if (!searchInput.contains(e.target) && !document.getElementById('autocomplete-container')?.contains(e.target)) {
        hideAutocomplete();
    }
});

console.log('✅ Autocomplete suggestions ready!');
