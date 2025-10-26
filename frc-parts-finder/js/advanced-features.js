// FRC Parts Finder - Advanced Features Module
// Gelişmiş Özellikler: Fiyat Takibi, Karşılaştırma, BOM Builder, vb.

// ============================================
// 1. ADVANCED SEARCH & FILTERING
// ============================================

class AdvancedSearchFilter {
    constructor() {
        this.filters = {
            category: null,
            priceRange: { min: 0, max: Infinity },
            vendors: [],
            specs: {},
            tags: [],
            inStock: null
        };
    }

    applyFilters(products) {
        return products.filter(product => {
            // Category filter
            if (this.filters.category && product.category !== this.filters.category) {
                return false;
            }

            // Price range filter
            const price = parseFloat(product.price);
            if (price < this.filters.priceRange.min || price > this.filters.priceRange.max) {
                return false;
            }

            // Vendor filter
            if (this.filters.vendors.length > 0 && !this.filters.vendors.includes(product.vendor)) {
                return false;
            }

            // Stock filter
            if (this.filters.inStock !== null) {
                const isInStock = product.stock === 'in-stock';
                if (this.filters.inStock !== isInStock) {
                    return false;
                }
            }

            // Tags filter
            if (this.filters.tags.length > 0) {
                const productTags = product.tags || [];
                const hasAllTags = this.filters.tags.every(tag => productTags.includes(tag));
                if (!hasAllTags) {
                    return false;
                }
            }

            return true;
        });
    }

    setCategory(category) {
        this.filters.category = category;
    }

    setPriceRange(min, max) {
        this.filters.priceRange = { min, max };
    }

    setVendors(vendors) {
        this.filters.vendors = vendors;
    }

    setTags(tags) {
        this.filters.tags = tags;
    }

    setStockFilter(inStock) {
        this.filters.inStock = inStock;
    }

    reset() {
        this.filters = {
            category: null,
            priceRange: { min: 0, max: Infinity },
            vendors: [],
            specs: {},
            tags: [],
            inStock: null
        };
    }
}

// Global filter instance
const searchFilter = new AdvancedSearchFilter();

// ============================================
// 2. PRICE TRACKING SYSTEM
// ============================================

class PriceTracker {
    constructor() {
        this.priceHistory = this.loadPriceHistory();
    }

    loadPriceHistory() {
        const stored = localStorage.getItem('priceHistory');
        return stored ? JSON.parse(stored) : {};
    }

    savePriceHistory() {
        localStorage.setItem('priceHistory', JSON.stringify(this.priceHistory));
    }

    trackPrice(productId, vendor, price) {
        const key = `${productId}_${vendor}`;
        if (!this.priceHistory[key]) {
            this.priceHistory[key] = [];
        }

        const today = new Date().toISOString().split('T')[0];
        const lastEntry = this.priceHistory[key][this.priceHistory[key].length - 1];

        // Only add if price changed or it's a new day
        if (!lastEntry || lastEntry.price !== price || lastEntry.date !== today) {
            this.priceHistory[key].push({
                date: today,
                price: price,
                timestamp: Date.now()
            });

            // Keep only last 365 days
            const oneYearAgo = Date.now() - (365 * 24 * 60 * 60 * 1000);
            this.priceHistory[key] = this.priceHistory[key].filter(
                entry => entry.timestamp > oneYearAgo
            );

            this.savePriceHistory();
        }
    }

    getPriceHistory(productId, vendor) {
        const key = `${productId}_${vendor}`;
        return this.priceHistory[key] || [];
    }

    getLowestPrice(productId, vendor) {
        const history = this.getPriceHistory(productId, vendor);
        if (history.length === 0) return null;

        return Math.min(...history.map(entry => entry.price));
    }

    getPriceDropPercentage(productId, vendor, currentPrice) {
        const lowest = this.getLowestPrice(productId, vendor);
        if (!lowest || lowest >= currentPrice) return 0;

        return ((currentPrice - lowest) / currentPrice * 100).toFixed(1);
    }

    createPriceChart(productId, vendor, canvasId) {
        const history = this.getPriceHistory(productId, vendor);
        if (history.length < 2) {
            return null;
        }

        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        const ctx = canvas.getContext('2d');
        const dates = history.map(h => h.date);
        const prices = history.map(h => h.price);

        // Simple line chart (you can integrate Chart.js for better visuals)
        return {
            dates: dates,
            prices: prices,
            lowest: Math.min(...prices),
            highest: Math.max(...prices),
            current: prices[prices.length - 1]
        };
    }
}

// Global price tracker
const priceTracker = new PriceTracker();

// ============================================
// 3. PRODUCT COMPARISON TOOL
// ============================================

class ProductComparison {
    constructor() {
        this.compareList = this.loadCompareList();
    }

    loadCompareList() {
        const stored = localStorage.getItem('compareList');
        return stored ? JSON.parse(stored) : [];
    }

    saveCompareList() {
        localStorage.setItem('compareList', JSON.stringify(this.compareList));
    }

    addToCompare(product) {
        // Limit to 4 products for comparison
        if (this.compareList.length >= 4) {
            alert('You can only compare up to 4 products at a time');
            return false;
        }

        // Check if already in list
        const exists = this.compareList.some(p =>
            p.name === product.name && p.vendor === product.vendor
        );

        if (!exists) {
            this.compareList.push(product);
            this.saveCompareList();
            this.updateCompareUI();
            return true;
        }

        return false;
    }

    removeFromCompare(index) {
        this.compareList.splice(index, 1);
        this.saveCompareList();
        this.updateCompareUI();
        this.refreshModal();
    }

    clearCompare() {
        this.compareList = [];
        this.saveCompareList();
        this.updateCompareUI();
        this.refreshModal();
    }

    updateCompareUI() {
        const badge = document.getElementById('compareBadge');
        if (badge) {
            badge.textContent = this.compareList.length;
            badge.style.display = this.compareList.length > 0 ? 'inline-block' : 'none';
        }
    }

    showComparisonView() {
        if (this.compareList.length === 0) {
            alert('Please add at least 1 product to compare');
            return;
        }

        // Create comparison modal
        const modal = this.createComparisonModal();
        document.body.appendChild(modal);
    }

    createComparisonModal() {
        const modal = document.createElement('div');
        modal.className = 'comparison-modal';
        modal.innerHTML = `
            <div class="comparison-content">
                <div class="comparison-header">
                    <h2>Product Comparison</h2>
                    <div class="comparison-header-actions">
                        <button class="comparison-clear-btn" onclick="productComparison.clearCompare()">Clear All</button>
                        <button class="close-btn" onclick="productComparison.closeModal()">&times;</button>
                    </div>
                </div>
                <div class="comparison-table-container">
                    ${this.generateComparisonTable()}
                </div>
            </div>
        `;

        return modal;
    }

    generateComparisonTable() {
        const products = this.compareList;
        if (!products.length) {
            return '<p class="empty-state">No products selected.</p>';
        }

        let html = '<table class="comparison-table"><thead><tr><th>Attribute</th>';

        // Product headers
        products.forEach((product, index) => {
            html += `<th>${product.name}<br><small>${product.vendor}</small><br><button class="remove-compare-btn" onclick="productComparison.handleRemoveClick(event, ${index})">Remove</button></th>`;
        });
        html += '</tr></thead><tbody>';

        // Price row
        html += '<tr><td><strong>Price</strong></td>';
        products.forEach(product => {
            html += `<td>$${product.price}</td>`;
        });
        html += '</tr>';

        // Stock row
        html += '<tr><td><strong>Stock</strong></td>';
        products.forEach(product => {
            html += `<td class="stock-${product.stock}">${product.stock}</td>`;
        });
        html += '</tr>';

        // Category row
        html += '<tr><td><strong>Category</strong></td>';
        products.forEach(product => {
            html += `<td>${product.category || 'N/A'}</td>`;
        });
        html += '</tr>';

        // Tags row
        html += '<tr><td><strong>Tags</strong></td>';
        products.forEach(product => {
            const tags = product.tags || [];
            html += `<td>${tags.join(', ') || 'N/A'}</td>`;
        });
        html += '</tr>';

        // Specs rows (if available)
        if (products.some(p => p.specs)) {
            const allSpecKeys = new Set();
            products.forEach(p => {
                if (p.specs) {
                    Object.keys(p.specs).forEach(key => allSpecKeys.add(key));
                }
            });

            allSpecKeys.forEach(specKey => {
                html += `<tr><td><strong>${specKey}</strong></td>`;
                products.forEach(product => {
                    const value = product.specs && product.specs[specKey] ? product.specs[specKey] : 'N/A';
                    html += `<td>${value}</td>`;
                });
                html += '</tr>';
            });
        }

        // Links row
        html += '<tr><td><strong>View Product</strong></td>';
        products.forEach(product => {
            html += `<td><a href="${product.url}" target="_blank" class="btn-link">View</a></td>`;
        });
        html += '</tr>';

        html += '</tbody></table>';
        return html;
    }

    closeModal() {
        const modal = document.querySelector('.comparison-modal');
        if (modal) {
            modal.remove();
        }
    }

    refreshModal() {
        const tableContainer = document.querySelector('.comparison-table-container');
        if (!tableContainer) {
            return;
        }

        tableContainer.innerHTML = this.generateComparisonTable();
    }

    handleRemoveClick(event, index) {
        if (event) {
            event.stopPropagation();
            event.preventDefault();
        }
        this.removeFromCompare(index);
    }
}

// Global comparison instance
const productComparison = new ProductComparison();

// ============================================
// 4. BOM (Bill of Materials) BUILDER
// ============================================

class BOMBuilder {
    constructor() {
        this.bomList = this.loadBOM();
    }

    loadBOM() {
        const stored = localStorage.getItem('bomList');
        return stored ? JSON.parse(stored) : [];
    }

    saveBOM() {
        localStorage.setItem('bomList', JSON.stringify(this.bomList));
    }

    addToBOM(product, quantity = 1) {
        const existing = this.bomList.find(item =>
            item.product.name === product.name && item.product.vendor === product.vendor
        );

        if (existing) {
            existing.quantity += quantity;
        } else {
            this.bomList.push({
                product: product,
                quantity: quantity,
                addedDate: new Date().toISOString()
            });
        }

        this.saveBOM();
        this.updateBOMUI();
    }

    updateQuantity(index, quantity) {
        if (this.bomList[index]) {
            this.bomList[index].quantity = Math.max(1, quantity);
            this.saveBOM();
            this.updateBOMUI();
        }
    }

    removeFromBOM(index) {
        this.bomList.splice(index, 1);
        this.saveBOM();
        this.updateBOMUI();
    }

    clearBOM() {
        if (confirm('Are you sure you want to clear your entire BOM?')) {
            this.bomList = [];
            this.saveBOM();
            this.updateBOMUI();
        }
    }

    getTotalCost() {
        return this.bomList.reduce((total, item) => {
            return total + (parseFloat(item.product.price) * item.quantity);
        }, 0);
    }

    getVendorBreakdown() {
        const breakdown = {};

        this.bomList.forEach(item => {
            const vendor = item.product.vendor;
            if (!breakdown[vendor]) {
                breakdown[vendor] = {
                    items: 0,
                    total: 0
                };
            }
            breakdown[vendor].items += item.quantity;
            breakdown[vendor].total += parseFloat(item.product.price) * item.quantity;
        });

        return breakdown;
    }

    exportToCSV() {
        let csv = 'Part Name,Vendor,Quantity,Unit Price,Total Price,URL,Category\n';

        this.bomList.forEach(item => {
            const p = item.product;
            const total = (parseFloat(p.price) * item.quantity).toFixed(2);
            csv += `"${p.name}","${p.vendor}",${item.quantity},${p.price},${total},"${p.url}","${p.category || 'N/A'}"\n`;
        });

        // Download CSV
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `FRC_BOM_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
    }

    updateBOMUI() {
        const badge = document.getElementById('bomBadge');
        if (badge) {
            const totalItems = this.bomList.reduce((sum, item) => sum + item.quantity, 0);
            badge.textContent = totalItems;
            badge.style.display = totalItems > 0 ? 'inline-block' : 'none';
        }
    }

    showBOMView() {
        const modal = this.createBOMModal();
        document.body.appendChild(modal);
    }

    createBOMModal() {
        const modal = document.createElement('div');
        modal.className = 'bom-modal';

        const vendorBreakdown = this.getVendorBreakdown();
        const totalCost = this.getTotalCost();

        let itemsHTML = '';
        this.bomList.forEach((item, index) => {
            const itemTotal = (parseFloat(item.product.price) * item.quantity).toFixed(2);
            itemsHTML += `
                <tr>
                    <td>${item.product.name}</td>
                    <td>${item.product.vendor}</td>
                    <td>
                        <input type="number" min="1" value="${item.quantity}"
                            onchange="bomBuilder.updateQuantity(${index}, this.value)"
                            class="quantity-input">
                    </td>
                    <td>$${item.product.price}</td>
                    <td>$${itemTotal}</td>
                    <td>
                        <button onclick="bomBuilder.removeFromBOM(${index})" class="btn-remove">Remove</button>
                    </td>
                </tr>
            `;
        });

        let vendorHTML = '';
        Object.entries(vendorBreakdown).forEach(([vendor, data]) => {
            vendorHTML += `
                <div class="vendor-summary">
                    <strong>${vendor}:</strong> ${data.items} items - $${data.total.toFixed(2)}
                </div>
            `;
        });

        modal.innerHTML = `
            <div class="bom-content">
                <div class="bom-header">
                    <h2>Bill of Materials (BOM)</h2>
                    <button class="close-btn" onclick="bomBuilder.closeModal()">&times;</button>
                </div>

                <div class="bom-summary">
                    <h3>Summary</h3>
                    <div class="summary-total">Total Cost: <strong>$${totalCost.toFixed(2)}</strong></div>
                    <h4>By Vendor:</h4>
                    ${vendorHTML}
                </div>

                <div class="bom-actions">
                    <button onclick="bomBuilder.exportToCSV()" class="btn-primary">Export to CSV</button>
                    <button onclick="bomBuilder.clearBOM()" class="btn-danger">Clear BOM</button>
                </div>

                <table class="bom-table">
                    <thead>
                        <tr>
                            <th>Part Name</th>
                            <th>Vendor</th>
                            <th>Quantity</th>
                            <th>Unit Price</th>
                            <th>Total</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${itemsHTML || '<tr><td colspan="6" style="text-align: center;">No items in BOM</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;

        return modal;
    }

    closeModal() {
        const modal = document.querySelector('.bom-modal');
        if (modal) {
            modal.remove();
        }
    }
}

// Global BOM builder instance
const bomBuilder = new BOMBuilder();

// ============================================
// 5. CALCULATOR INTEGRATIONS
// ============================================

class FRCCalculators {
    // Gear Ratio Calculator
    static calculateGearRatio(drivingTeeth, drivenTeeth) {
        const ratio = drivenTeeth / drivingTeeth;
        return {
            ratio: ratio.toFixed(3),
            notation: `${drivingTeeth}:${drivenTeeth}`,
            reduction: ratio > 1,
            multiplication: ratio < 1
        };
    }

    // Speed Calculator
    static calculateSpeed(motorRPM, gearRatio, wheelDiameter) {
        // Formula: Speed (fps) = (Motor RPM × Wheel Diameter × π) / (Gear Ratio × 12 × 60)
        const speedFPS = (motorRPM * wheelDiameter * Math.PI) / (gearRatio * 12 * 60);
        const speedMPS = speedFPS * 0.3048;

        return {
            fps: speedFPS.toFixed(2),
            mph: (speedFPS * 0.681818).toFixed(2),
            mps: speedMPS.toFixed(2)
        };
    }

    // Current Draw Calculator
    static estimateCurrentDraw(numMotors, motorType, loadPercentage = 50) {
        const motorCurrents = {
            'NEO': { free: 1.3, stall: 105 },
            'NEO 550': { free: 1.1, stall: 97 },
            'Falcon 500': { free: 1.5, stall: 257 },
            'Kraken X60': { free: 2, stall: 366 },
            'CIM': { free: 2.7, stall: 131 }
        };

        const motor = motorCurrents[motorType] || motorCurrents['NEO'];
        const estimatedCurrent = motor.free + ((motor.stall - motor.free) * loadPercentage / 100);

        return {
            perMotor: estimatedCurrent.toFixed(1),
            total: (estimatedCurrent * numMotors).toFixed(1),
            breaker: Math.ceil(estimatedCurrent * numMotors / 10) * 10
        };
    }

    // Show calculator modal
    static showCalculatorModal() {
        const modal = document.createElement('div');
        modal.className = 'calculator-modal';
        modal.innerHTML = `
            <div class="calculator-content">
                <div class="calculator-header">
                    <h2>FRC Calculators</h2>
                    <button class="close-btn" onclick="this.closest('.calculator-modal').remove()">&times;</button>
                </div>

                <div class="calculator-tabs">
                    <button class="tab-btn active" onclick="FRCCalculators.showTab('gear')">Gear Ratio</button>
                    <button class="tab-btn" onclick="FRCCalculators.showTab('speed')">Speed</button>
                    <button class="tab-btn" onclick="FRCCalculators.showTab('current')">Current Draw</button>
                </div>

                <div id="calc-gear" class="calc-tab active">
                    <h3>Gear Ratio Calculator</h3>
                    <div class="calc-input">
                        <label>Driving Gear Teeth:</label>
                        <input type="number" id="driving-teeth" value="12">
                    </div>
                    <div class="calc-input">
                        <label>Driven Gear Teeth:</label>
                        <input type="number" id="driven-teeth" value="60">
                    </div>
                    <button onclick="FRCCalculators.calcGear()" class="btn-calc">Calculate</button>
                    <div id="gear-result" class="calc-result"></div>
                </div>

                <div id="calc-speed" class="calc-tab">
                    <h3>Speed Calculator</h3>
                    <div class="calc-input">
                        <label>Motor Free Speed (RPM):</label>
                        <input type="number" id="motor-rpm" value="5676" placeholder="NEO = 5676">
                    </div>
                    <div class="calc-input">
                        <label>Gear Ratio:</label>
                        <input type="number" id="gear-ratio" value="8.45" step="0.01">
                    </div>
                    <div class="calc-input">
                        <label>Wheel Diameter (inches):</label>
                        <input type="number" id="wheel-dia" value="4" step="0.1">
                    </div>
                    <button onclick="FRCCalculators.calcSpeed()" class="btn-calc">Calculate</button>
                    <div id="speed-result" class="calc-result"></div>
                </div>

                <div id="calc-current" class="calc-tab">
                    <h3>Current Draw Estimator</h3>
                    <div class="calc-input">
                        <label>Number of Motors:</label>
                        <input type="number" id="num-motors" value="4" min="1">
                    </div>
                    <div class="calc-input">
                        <label>Motor Type:</label>
                        <select id="motor-type">
                            <option value="NEO">NEO</option>
                            <option value="NEO 550">NEO 550</option>
                            <option value="Falcon 500">Falcon 500</option>
                            <option value="Kraken X60">Kraken X60</option>
                            <option value="CIM">CIM</option>
                        </select>
                    </div>
                    <div class="calc-input">
                        <label>Load Percentage (%):</label>
                        <input type="range" id="load-percent" min="0" max="100" value="50"
                            oninput="document.getElementById('load-value').textContent = this.value">
                        <span id="load-value">50</span>%
                    </div>
                    <button onclick="FRCCalculators.calcCurrent()" class="btn-calc">Calculate</button>
                    <div id="current-result" class="calc-result"></div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    static showTab(tabName) {
        document.querySelectorAll('.calc-tab').forEach(tab => tab.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

        document.getElementById(`calc-${tabName}`).classList.add('active');
        event.target.classList.add('active');
    }

    static calcGear() {
        const driving = parseFloat(document.getElementById('driving-teeth').value);
        const driven = parseFloat(document.getElementById('driven-teeth').value);
        const result = this.calculateGearRatio(driving, driven);

        document.getElementById('gear-result').innerHTML = `
            <div class="result-box">
                <p><strong>Gear Ratio:</strong> ${result.ratio}:1 (${result.notation})</p>
                <p><strong>Type:</strong> ${result.reduction ? 'Reduction (Slower, More Torque)' : 'Multiplication (Faster, Less Torque)'}</p>
            </div>
        `;
    }

    static calcSpeed() {
        const rpm = parseFloat(document.getElementById('motor-rpm').value);
        const ratio = parseFloat(document.getElementById('gear-ratio').value);
        const diameter = parseFloat(document.getElementById('wheel-dia').value);
        const result = this.calculateSpeed(rpm, ratio, diameter);

        document.getElementById('speed-result').innerHTML = `
            <div class="result-box">
                <p><strong>Robot Speed:</strong></p>
                <p>${result.fps} ft/s</p>
                <p>${result.mph} mph</p>
                <p>${result.mps} m/s</p>
            </div>
        `;
    }

    static calcCurrent() {
        const numMotors = parseInt(document.getElementById('num-motors').value);
        const motorType = document.getElementById('motor-type').value;
        const loadPercent = parseFloat(document.getElementById('load-percent').value);
        const result = this.estimateCurrentDraw(numMotors, motorType, loadPercent);

        document.getElementById('current-result').innerHTML = `
            <div class="result-box">
                <p><strong>Per Motor:</strong> ${result.perMotor} A</p>
                <p><strong>Total Current:</strong> ${result.total} A</p>
                <p><strong>Recommended Breaker:</strong> ${result.breaker} A</p>
            </div>
        `;
    }
}

// ============================================
// 6. COMMUNITY FEATURES (Reviews & Ratings)
// ============================================

class CommunityFeatures {
    constructor() {
        this.reviews = this.loadReviews();
    }

    loadReviews() {
        const stored = localStorage.getItem('productReviews');
        return stored ? JSON.parse(stored) : {};
    }

    saveReviews() {
        localStorage.setItem('productReviews', JSON.stringify(this.reviews));
    }

    addReview(productId, rating, review, teamNumber) {
        const key = productId;
        if (!this.reviews[key]) {
            this.reviews[key] = [];
        }

        this.reviews[key].push({
            rating: rating,
            review: review,
            teamNumber: teamNumber,
            date: new Date().toISOString(),
            helpful: 0
        });

        this.saveReviews();
    }

    getAverageRating(productId) {
        const reviews = this.reviews[productId] || [];
        if (reviews.length === 0) return 0;

        const sum = reviews.reduce((acc, r) => acc + r.rating, 0);
        return (sum / reviews.length).toFixed(1);
    }

    getReviews(productId) {
        return this.reviews[productId] || [];
    }
}

// Global community features instance
const communityFeatures = new CommunityFeatures();

// Initialize all features on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Advanced features loaded!');

    // Update UI badges
    productComparison.updateCompareUI();
    bomBuilder.updateBOMUI();
});
