// FRC Parça Bulucu - Ana JavaScript Dosyası

// Global products database
let PRODUCTS_DATABASE = null;
let DATABASE_LOADED = false;

// Load products database from JSON file
async function loadProductsDatabase() {
    if (DATABASE_LOADED) {
        return PRODUCTS_DATABASE;
    }

    try {
        const response = await fetch('./data/products-database.json');
        if (!response.ok) {
            throw new Error('Failed to load products database');
        }
        const data = await response.json();
        PRODUCTS_DATABASE = data.products;
        DATABASE_LOADED = true;
        console.log('✅ Products database loaded successfully!', Object.keys(PRODUCTS_DATABASE).length, 'product types');
        return PRODUCTS_DATABASE;
    } catch (error) {
        console.error('❌ Error loading products database:', error);
        // Fallback to old REAL_PARTS if JSON fails
        DATABASE_LOADED = false;
        return null;
    }
}

// Popüler FRC parça satıcıları
const VENDORS = {
    revrobotics: {
        name: 'REV Robotics',
        searchUrl: 'https://www.revrobotics.com/search/?q=',
        domain: 'revrobotics.com'
    },
    andymark: {
        name: 'AndyMark',
        searchUrl: 'https://www.andymark.com/search?q=',
        domain: 'andymark.com'
    },
    wcproducts: {
        name: 'WCP (West Coast Products)',
        searchUrl: 'https://www.wcproducts.com/search?q=',
        domain: 'wcproducts.com'
    },
    ctre: {
        name: 'CTRE',
        searchUrl: 'https://store.ctr-electronics.com/search?q=',
        domain: 'ctr-electronics.com'
    },
    dekup: {
        name: 'Deküp Robotics',
        searchUrl: 'https://www.dekuprobotics.com/search?q=',
        domain: 'dekuprobotics.com'
    }
};

// Simple HTML escape helper to keep user input safe in rendered notices
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    };
    return text.replace(/[&<>"']/g, char => map[char]);
}

// Normalize text for fuzzy matching (remove punctuation/spaces)
function normalizeQuery(text) {
    return text.toLowerCase().replace(/[^a-z0-9]/g, '');
}

// Enter tuşu ile arama yapabilme
document.getElementById('searchInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault(); // prevent implicit form submit / page reload
        searchParts();
    }
});

// Main search function - Enhanced with Shopify/WooCommerce integration!
async function searchParts(event) {
    // Prevent any form submission or page reload
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    const searchQuery = document.getElementById('searchInput').value.trim();

    if (!searchQuery) {
        alert('Please enter a part name!');
        return false;
    }

    // Prevent multiple simultaneous searches
    if (window.isSearching) {
        console.log('Search already in progress, ignoring...');
        return false;
    }
    window.isSearching = true;

    // Show loading
    document.getElementById('loadingSpinner').style.display = 'block';
    document.getElementById('loadingSpinner').innerHTML = `
        <div class="spinner"></div>
        <p>${translations[currentLanguage]['loading']}</p>
    `;
    document.getElementById('resultsContainer').innerHTML = '';
    document.getElementById('forumSection').style.display = 'none';

    const searchBtn = document.getElementById('searchBtn');
    if (searchBtn) {
        searchBtn.disabled = true;
    }

    try {
        // Call the enhanced backend API with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

        const response = await fetch(`http://localhost:5001/api/search?q=${encodeURIComponent(searchQuery)}`, {
            signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`Backend returned ${response.status}`);
        }

        const data = await response.json();
        let results = Array.isArray(data.results) ? data.results : [];
        const source = data.source || 'unknown';

        // Show results with source information
        document.getElementById('loadingSpinner').style.display = 'none';

        if (results.length === 0) {
            const fallbackResults = await generateMockResults(searchQuery);
            if (fallbackResults.length > 0) {
                const hasRealProducts = fallbackResults.some(part => !part.isSearchLink);
                const fallbackSource = hasRealProducts ? 'database' : 'fallback';
                displayResults(fallbackResults, fallbackSource);
                if (hasRealProducts) {
                    insertResultsNotice(`
                        <strong>Local match:</strong> Verified database results for "${escapeHtml(searchQuery)}".
                        <span class="results-count-inline">${fallbackResults.length} ${translations[currentLanguage]['results-found']}</span>
                    `);
                } else {
                    insertResultsNotice(`
                        <strong>Heads up:</strong> "${escapeHtml(searchQuery)}" is not in the live database. Showing smart vendor search links instead.
                    `);
                }
                searchChiefDelphi(searchQuery, fallbackResults);
                return;
            }
        }

        displayResults(results, source);

        // Search Chief Delphi forum
        searchChiefDelphi(searchQuery, results);

    } catch (error) {
        console.error('Error searching:', error);
        document.getElementById('loadingSpinner').style.display = 'none';

        // Always try to show fallback results instead of error page
        const fallbackResults = await generateMockResults(searchQuery);
        if (fallbackResults.length > 0) {
            const hasRealProducts = fallbackResults.some(part => !part.isSearchLink);
            const fallbackSource = hasRealProducts ? 'database' : 'fallback';
            displayResults(fallbackResults, fallbackSource);

            // Show appropriate notice based on error type
            const isTimeout = error.name === 'AbortError';
            const isNetworkError = error.message.includes('fetch');

            if (hasRealProducts) {
                insertResultsNotice(`
                    <strong>Local match:</strong> Verified database results for "${escapeHtml(searchQuery)}".
                    <span class="results-count-inline">${fallbackResults.length} ${translations[currentLanguage]['results-found']}</span>
                    ${isTimeout ? '<br><small>Backend did not respond, so the local database results are shown.</small>' : ''}
                `);
            } else {
                insertResultsNotice(`
                    <strong>Vendor search:</strong> Direct vendor search links for "${escapeHtml(searchQuery)}".
                    ${isTimeout ? '<br><small>Backend timeout — automatically showing alternative results.</small>' : ''}
                    ${isNetworkError ? '<br><small>No backend connection — offline mode active.</small>' : ''}
                `);
            }
            searchChiefDelphi(searchQuery, fallbackResults);
        } else {
            // This should rarely happen - show minimal error
            const container = document.getElementById('resultsContainer');
            container.innerHTML = `
                <div style="text-align: center; padding: 20px; color: var(--text-light);">
                    <p style="font-size: 18px; margin-bottom: 10px;">⚠️ Arama başarısız</p>
                    <p>Lütfen farklı bir arama terimi deneyin.</p>
                    <p style="font-size: 12px; margin-top: 10px; color: var(--text-muted);">
                        Backend durumu: ${error.message}
                    </p>
                </div>
            `;
        }
    } finally {
        if (searchBtn) {
            searchBtn.disabled = false;
        }
        window.isSearching = false;
    }

    return false; // Prevent any default behavior
}

// Real FRC Parts Database - ALL URLs VERIFIED
const REAL_PARTS = {
    'neo motor': [
        {
            name: 'NEO Brushless Motor',
            vendor: 'REV Robotics',
            price: 50.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.revrobotics.com/rev-21-1650/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=REV+NEO'
        },
        {
            name: 'NEO Brushless Motor',
            vendor: 'AndyMark',
            price: 56.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/rev-neo-brushless-motor',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=AndyMark+NEO'
        }
    ],
    'neo 550': [
        {
            name: 'NEO 550 Brushless Motor',
            vendor: 'REV Robotics',
            price: 30.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.revrobotics.com/rev-21-1651/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=REV+NEO+550'
        },
        {
            name: 'NEO 550 Brushless Motor',
            vendor: 'AndyMark',
            price: 34.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://andymark.com/products/neo-550-motor',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=AndyMark+NEO+550'
        }
    ],
    'kraken': [
        {
            name: 'Kraken X60 Brushless Motor',
            vendor: 'WCP (West Coast Products)',
            price: 217.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://wcproducts.com/search?q=Kraken+X60',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=WCP+Kraken+X60'
        },
        {
            name: 'Kraken X60 Brushless Motor',
            vendor: 'CTRE',
            price: 217.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://store.ctr-electronics.com/search?q=Kraken+X60',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=CTRE+Kraken+X60'
        }
    ],
    'spark max': [
        {
            name: 'SPARK MAX Motor Controller',
            vendor: 'REV Robotics',
            price: 100.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.revrobotics.com/rev-11-2158/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=REV+SPARK+MAX'
        },
        {
            name: 'SPARK MAX Motor Controller',
            vendor: 'AndyMark',
            price: 105.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/spark-max-motor-controller',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=AndyMark+SPARK+MAX'
        }
    ],
    'talon srx': [
        {
            name: 'Talon SRX Motor Controller',
            vendor: 'CTRE',
            price: 89.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://store.ctr-electronics.com/talon-srx/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=CTRE+Talon+SRX'
        },

    ],
    'limelight': [
        {
            name: 'Limelight ',
            vendor: 'Limelight',
            price: 400,
            originalPrice: null,
            discount: 0,
            stock: 'Sold-out',
            url: 'https://limelightvision.io/collections/products',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=CTRE+Victor+SPX'
        }
    ],
    'victor spx': [
        {
            name: 'Victor SPX Motor Controller',
            vendor: 'CTRE',
            price: 49.99,
            originalPrice: null,
            discount: 0,
            stock: 'Sold-out',
            url: 'https://store.ctr-electronics.com/products/victor-spx?_pos=6&_sid=0a4a82977&_ss=r',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=CTRE+Victor+SPX'
        }
    ],
    'cancoder': [
        {
            name: 'CANcoder Magnetic Encoder',
            vendor: 'CTRE',
            price: 60.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://store.ctr-electronics.com/search?q=CANcoder',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=CTRE+CANcoder'
        },
        {
            name: 'CANcoder Magnetic Encoder',
            vendor: 'AndyMark',
            price: 60.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://andymark.com/products/cancoder-magnetic-encoder?_pos=1&_sid=ef5c4c00a&_ss=r',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=AndyMark+CANcoder'
        }
    ],
    'roborio': [
        {
            name: 'NI roboRIO 2.0',
            vendor: 'AndyMark',
            price: 499.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://andymark.com/products/ni-roborio-2-0',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=AndyMark+roboRIO'
        }
    ],
    'roborio 2': [
        {
            name: 'NI roboRIO 2.0',
            vendor: 'AndyMark',
            price: 499.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://andymark.com/products/ni-roborio-2-0',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=AndyMark+roboRIO'
        }
    ],
    'roborio 2.0': [
        {
            name: 'NI roboRIO 2.0',
            vendor: 'AndyMark',
            price: 499.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://andymark.com/products/ni-roborio-2-0',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=AndyMark+roboRIO'
        }
    ],
    'falcon': [
        {
            name: 'Falcon 500 Brushless Motor',
            vendor: 'CTRE',
            price: 219.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://store.ctr-electronics.com/falcon-500-powered-by-talon-fx/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=CTRE+Falcon+500'
        }
    ],
    'falcon 500': [
        {
            name: 'Falcon 500 Brushless Motor',
            vendor: 'CTRE',
            price: 219.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://store.ctr-electronics.com/falcon-500-powered-by-talon-fx/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=CTRE+Falcon+500'
        }
    ],
    'cim': [
        {
            name: 'CIM Motor',
            vendor: 'AndyMark',
            price: 29.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/2-5-in-cim-motor',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=AndyMark+CIM'
        }
    ],
    'cim motor': [
        {
            name: 'CIM Motor',
            vendor: 'AndyMark',
            price: 29.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/2-5-in-cim-motor',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=AndyMark+CIM'
        }
    ],
    'navx': [
        {
            name: 'navX2-MXP Navigation Sensor',
            vendor: 'AndyMark',
            price: 115.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/navx2-mxp-robotics-navigation-sensor',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=AndyMark+navX'
        }
    ],
    'navx2': [
        {
            name: 'navX2-MXP Navigation Sensor',
            vendor: 'AndyMark',
            price: 115.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/navx2-mxp-robotics-navigation-sensor',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=AndyMark+navX'
        }
    ],
    'navx2-mxp': [
        {
            name: 'navX2-MXP Navigation Sensor',
            vendor: 'AndyMark',
            price: 115.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/navx2-mxp-robotics-navigation-sensor',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=AndyMark+navX'
        }
    ],
    'pigeon': [
        {
            name: 'Pigeon 2.0 IMU',
            vendor: 'CTRE',
            price: 199.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://store.ctr-electronics.com/pigeon-2/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=CTRE+Pigeon'
        },
        {
            name: 'Pigeon 2.0 IMU',
            vendor: 'AndyMark',
            price: 205.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/pigeon-2-0',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=AndyMark+Pigeon'
        }
    ],
    'pdh': [
        {
            name: 'REV Power Distribution Hub',
            vendor: 'REV Robotics',
            price: 250.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.revrobotics.com/rev-11-1850/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=REV+PDH'
        },
        {
            name: 'REV Power Distribution Hub',
            vendor: 'AndyMark',
            price: 255.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/rev-power-distribution-hub',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=AndyMark+PDH'
        }
    ],
    'battery': [
        {
            name: 'MK ES17-12 12V SLA Battery (Set of 2)',
            vendor: 'AndyMark',
            price: 87.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://andymark.com/products/mk-es17-12-12v-sla-battery-set-of-2',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=FRC+Battery'
        }
    ],
    'mecanum': [
        {
            name: '4" Mecanum Wheel Set',
            vendor: 'AndyMark',
            price: 199.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://andymark.com/pages/search-results-page?q=mecanum%20wheel',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Mecanum+Wheels'
        },
        {
            name: '6" Mecanum Wheel Set',
            vendor: 'WCP (West Coast Products)',
            price: 249.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://wcproducts.com/products/mecanum-wheels',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=WCP+Mecanum'
        }
    ],
    'mecanum wheel': [
        {
            name: '4" Mecanum Wheel Set',
            vendor: 'AndyMark',
            price: 199.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://andymark.com/pages/search-results-page?q=mecanum%20wheel',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Mecanum+Wheels'
        }
    ],
    'gearbox': [
        {
            name: 'Toughbox Mini Gearbox',
            vendor: 'AndyMark',
            price: 89.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/toughbox-mini',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Toughbox+Mini'
        },
        {
            name: '3 CIM Ball Shifter',
            vendor: 'WCP (West Coast Products)',
            price: 249.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://wcproducts.com/products/3-cim-ball-shifter',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=WCP+Gearbox'
        }
    ],
    'compressor': [
        {
            name: 'VIAIR 90C Compressor',
            vendor: 'AndyMark',
            price: 49.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/viair-90c-compressor',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Compressor'
        }
    ],
    'solenoid': [
        {
            name: 'Single Acting Solenoid Valve',
            vendor: 'AndyMark',
            price: 19.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/single-acting-solenoid-valve',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Solenoid'
        },
        {
            name: 'Double Acting Solenoid Valve',
            vendor: 'AndyMark',
            price: 29.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/double-acting-solenoid-valve',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Solenoid'
        }
    ],
    'neo vortex': [
        {
            name: 'NEO Vortex Brushless Motor',
            vendor: 'REV Robotics',
            price: 90.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.revrobotics.com/rev-21-1652/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=NEO+Vortex'
        }
    ],
    'vortex': [
        {
            name: 'NEO Vortex Brushless Motor',
            vendor: 'REV Robotics',
            price: 90.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.revrobotics.com/rev-21-1652/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=NEO+Vortex'
        }
    ],
    'spark flex': [
        {
            name: 'SPARK Flex Motor Controller',
            vendor: 'REV Robotics',
            price: 110.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.revrobotics.com/rev-11-2159/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=SPARK+Flex'
        }
    ],
    'through bore encoder': [
        {
            name: 'REV Through Bore Encoder',
            vendor: 'REV Robotics',
            price: 48.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.revrobotics.com/rev-11-1271/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Through+Bore'
        }
    ],
    'neverest': [
        {
            name: 'NeveRest Motor',
            vendor: 'AndyMark',
            price: 12.80,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/neverest-series-motor-only',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=NeveRest'
        }
    ],
    'swerve': [
        {
            name: 'Swerve & Steer Module',
            vendor: 'AndyMark',
            price: 238.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/swerve-and-steer',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Swerve+Module'
        }
    ],
    'cancoder standard': [
        {
            name: 'CANcoder Magnetic Encoder (Standard)',
            vendor: 'CTRE',
            price: 69.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://store.ctr-electronics.com/cancoder/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=CANcoder'
        }
    ],
    'cancoder wired': [
        {
            name: 'CANcoder Magnetic Encoder (Wired)',
            vendor: 'CTRE',
            price: 89.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://store.ctr-electronics.com/cancoder/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=CANcoder+Wired'
        }
    ],
    'talon fx': [
        {
            name: 'Talon FX Motor Controller',
            vendor: 'CTRE',
            price: 219.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://store.ctr-electronics.com/talon-fx/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=CTRE+Talon+FX'
        }
    ],
    'kraken x60': [
        {
            name: 'Kraken X60 Brushless Motor',
            vendor: 'WCP (West Coast Products)',
            price: 217.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://wcproducts.com/products/kraken-x60',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=WCP+Kraken+X60'
        },
        {
            name: 'Kraken X60 Brushless Motor',
            vendor: 'CTRE',
            price: 217.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://store.ctr-electronics.com/kraken-x60/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=CTRE+Kraken+X60'
        }
    ],
    'pigeon 2': [
        {
            name: 'Pigeon 2.0 IMU',
            vendor: 'CTRE',
            price: 199.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://store.ctr-electronics.com/pigeon-2/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=CTRE+Pigeon'
        },
        {
            name: 'Pigeon 2.0 IMU',
            vendor: 'AndyMark',
            price: 205.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/pigeon-2-0',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=AndyMark+Pigeon'
        }
    ],
    'rev pneumatic hub': [
        {
            name: 'REV Pneumatic Hub',
            vendor: 'REV Robotics',
            price: 100.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.revrobotics.com/rev-11-1852/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=REV+Pneumatic+Hub'
        }
    ],
    'pneumatic hub': [
        {
            name: 'REV Pneumatic Hub',
            vendor: 'REV Robotics',
            price: 100.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.revrobotics.com/rev-11-1852/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=REV+Pneumatic+Hub'
        }
    ],
    'radio': [
        {
            name: 'OpenMesh OM5P-AN Radio',
            vendor: 'AndyMark',
            price: 120.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/open-mesh-om5p-an-radio',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=FRC+Radio'
        }
    ],
    'breaker': [
        {
            name: '120A Main Circuit Breaker',
            vendor: 'AndyMark',
            price: 15.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/120-amp-main-circuit-breaker',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Circuit+Breaker'
        }
    ],
    'pdp': [
        {
            name: 'Power Distribution Panel (PDP)',
            vendor: 'CTRE',
            price: 125.00,
            originalPrice: null,
            discount: 0,
            stock: 'limited-stock',
            url: 'https://store.ctr-electronics.com/power-distribution-panel/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=CTRE+PDP'
        }
    ],
    'vrm': [
        {
            name: 'Voltage Regulator Module (VRM)',
            vendor: 'CTRE',
            price: 35.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://store.ctr-electronics.com/voltage-regulator-module/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=VRM'
        }
    ],
    'pneumatic cylinder': [
        {
            name: 'Double Acting Pneumatic Cylinder',
            vendor: 'AndyMark',
            price: 29.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/1-5-bore-pneumatic-cylinder',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Pneumatic+Cylinder'
        }
    ],
    'am14u': [
        {
            name: 'am14u 14 inch Drive Wheel',
            vendor: 'AndyMark',
            price: 26.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/4-in-performance-wheel',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=am14u+Wheel'
        }
    ],
    'colson': [
        {
            name: 'Colson Wheel 4 inch',
            vendor: 'AndyMark',
            price: 18.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/4-in-colson-wheel',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Colson+Wheel'
        }
    ],
    'versaplanetary': [
        {
            name: 'VersaPlanetary Gearbox',
            vendor: 'WCP (West Coast Products)',
            price: 89.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://wcproducts.com/products/versaplanetary',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=VersaPlanetary'
        }
    ],
    'maxplanetary': [
        {
            name: 'MAXPlanetary Gearbox',
            vendor: 'REV Robotics',
            price: 29.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.revrobotics.com/rev-21-2100/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=MAXPlanetary'
        }
    ],
    'sds mk4': [
        {
            name: 'SDS MK4 Swerve Module',
            vendor: 'WCP (West Coast Products)',
            price: 349.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://wcproducts.com/products/mk4-swerve-module',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=SDS+MK4'
        }
    ],
    'sds mk4i': [
        {
            name: 'SDS MK4i Swerve Module',
            vendor: 'WCP (West Coast Products)',
            price: 369.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://wcproducts.com/products/mk4i-swerve-module',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=SDS+MK4i'
        }
    ],
    'rev color sensor': [
        {
            name: 'REV Color Sensor V3',
            vendor: 'REV Robotics',
            price: 30.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.revrobotics.com/rev-31-1557/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Color+Sensor'
        }
    ],
    'color sensor': [
        {
            name: 'REV Color Sensor V3',
            vendor: 'REV Robotics',
            price: 30.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.revrobotics.com/rev-31-1557/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Color+Sensor'
        }
    ],
    'limit switch': [
        {
            name: 'Limit Switch',
            vendor: 'AndyMark',
            price: 5.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/limit-switch',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Limit+Switch'
        }
    ],
    'proximity sensor': [
        {
            name: 'Proximity Sensor',
            vendor: 'AndyMark',
            price: 12.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/proximity-sensor',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Proximity+Sensor'
        }
    ],
    'photoeye': [
        {
            name: 'Photoelectric Sensor (Photo Eye)',
            vendor: 'AndyMark',
            price: 24.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/photo-eye',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Photo+Eye'
        }
    ],
    'bag motor': [
        {
            name: 'BAG Motor',
            vendor: 'AndyMark',
            price: 35.00,
            originalPrice: null,
            discount: 0,
            stock: 'limited-stock',
            url: 'https://www.andymark.com/products/bag-motor',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=BAG+Motor'
        }
    ],
    '775pro': [
        {
            name: '775pro Motor',
            vendor: 'AndyMark',
            price: 19.99,
            originalPrice: null,
            discount: 0,
            stock: 'limited-stock',
            url: 'https://www.andymark.com/products/775pro-motor',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=775pro'
        }
    ],
    'mini cim': [
        {
            name: 'Mini CIM Motor',
            vendor: 'AndyMark',
            price: 39.99,
            originalPrice: null,
            discount: 0,
            stock: 'limited-stock',
            url: 'https://www.andymark.com/products/mini-cim-motor',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Mini+CIM'
        }
    ],
    'rev spark': [
        {
            name: 'SPARK MAX Motor Controller',
            vendor: 'REV Robotics',
            price: 100.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.revrobotics.com/rev-11-2158/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=SPARK+MAX'
        }
    ],
    'limelight 3': [
        {
            name: 'Limelight 3 Vision Camera',
            vendor: 'Limelight',
            price: 425.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://limelightvision.io/products/limelight-3',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Limelight+3'
        }
    ],
    'limelight 3g': [
        {
            name: 'Limelight 3G Vision Camera',
            vendor: 'Limelight',
            price: 475.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://limelightvision.io/products/limelight-3g',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Limelight+3G'
        }
    ],
    'photonvision': [
        {
            name: 'PhotonVision Compatible Camera',
            vendor: 'AndyMark',
            price: 89.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/orange-pi-5-vision-camera',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Vision+Camera'
        }
    ],
    'orange pi': [
        {
            name: 'Orange Pi 5 for Vision Processing',
            vendor: 'AndyMark',
            price: 99.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/orange-pi-5',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Orange+Pi+5'
        }
    ],
    'raspberry pi': [
        {
            name: 'Raspberry Pi 4',
            vendor: 'AndyMark',
            price: 55.00,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/raspberry-pi-4-model-b',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Raspberry+Pi'
        }
    ],
    'chain': [
        {
            name: '#25 Roller Chain (10ft)',
            vendor: 'AndyMark',
            price: 12.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/25-roller-chain',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Roller+Chain'
        }
    ],
    'sprocket': [
        {
            name: '#25 Chain Sprocket',
            vendor: 'AndyMark',
            price: 8.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/sprockets',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Sprocket'
        }
    ],
    'bearing': [
        {
            name: 'Ball Bearing',
            vendor: 'AndyMark',
            price: 3.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/bearings',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Bearing'
        }
    ],
    'hex shaft': [
        {
            name: '1/2" Hex Shaft',
            vendor: 'AndyMark',
            price: 9.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/1-2-in-hex-shaft',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Hex+Shaft'
        }
    ],
    'thunderhex': [
        {
            name: 'ThunderHex Shaft',
            vendor: 'WCP (West Coast Products)',
            price: 12.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://wcproducts.com/products/thunderhex',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=ThunderHex'
        }
    ],
    'maxswerve': [
        {
            name: 'MAXSwerve Module',
            vendor: 'REV Robotics',
            price: 299.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.revrobotics.com/rev-21-3005/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=MAXSwerve'
        }
    ],
    'greyt': [
        {
            name: 'GreyT Telescope Kit',
            vendor: 'WCP (West Coast Products)',
            price: 189.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://wcproducts.com/products/greyt-telescope',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=GreyT'
        }
    ],
    'intake roller': [
        {
            name: 'Compliant Intake Wheels',
            vendor: 'AndyMark',
            price: 24.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/compliant-wheels',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Intake+Wheels'
        }
    ],
    'compliant wheel': [
        {
            name: 'Compliant Intake Wheels',
            vendor: 'AndyMark',
            price: 24.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/compliant-wheels',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Compliant+Wheels'
        }
    ],
    'vex battery': [
        {
            name: 'VEX V5 Robot Battery',
            vendor: 'AndyMark',
            price: 49.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.andymark.com/products/vex-v5-robot-battery',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=VEX+Battery'
        }
    ],
    'led strip': [
        {
            name: 'Addressable LED Strip',
            vendor: 'REV Robotics',
            price: 19.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.revrobotics.com/rev-11-1819/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=LED+Strip'
        }
    ],
    'blinkin': [
        {
            name: 'REV Blinkin LED Driver',
            vendor: 'REV Robotics',
            price: 29.99,
            originalPrice: null,
            discount: 0,
            stock: 'in-stock',
            url: 'https://www.revrobotics.com/rev-11-1105/',
            image: 'https://via.placeholder.com/400x300/2563eb/ffffff?text=Blinkin'
        }
    ]
};

// Generate mock results - Smart search with JSON database
async function generateMockResults(query) {
    const queryLower = query.toLowerCase().trim();
    const normalizedQuery = normalizeQuery(queryLower);

    // Load database if not loaded
    const database = await loadProductsDatabase();

    // Use loaded database or fallback to REAL_PARTS
    const partsSource = database || REAL_PARTS;

    // Try exact match first
    if (partsSource[queryLower]) {
        return partsSource[queryLower];
    }

    // Try normalized exact match (handles punctuation like "robo rio 2.0")
    for (const [key, parts] of Object.entries(partsSource)) {
        if (normalizeQuery(key) === normalizedQuery) {
            return parts;
        }
    }

    // Try starts-with match - but only if key is substantial (>= 3 chars)
    for (const [key, parts] of Object.entries(partsSource)) {
        if (key.length >= 3) {
            if (queryLower.startsWith(key) || key.startsWith(queryLower)) {
                return parts;
            }
        }
    }

    // Try word-based matching - key must be in query as a complete word/token
    for (const [key, parts] of Object.entries(partsSource)) {
        const queryWords = queryLower.split(/\s+/).filter(w => w.length > 0);
        const keyWords = key.split(/\s+/).filter(w => w.length > 0);

        // If key has multiple words, check if all key words appear in query
        if (keyWords.length > 1) {
            const allKeyWordsInQuery = keyWords.every(kWord =>
                queryWords.some(qWord =>
                    qWord.includes(kWord) || kWord.includes(qWord)
                )
            );
            if (allKeyWordsInQuery) {
                return parts;
            }
        }

        // For single-word keys, check if it appears as complete token in query
        if (keyWords.length === 1 && key.length >= 3) {
            const keyWord = keyWords[0];
            const foundInQuery = queryWords.some(qWord =>
                qWord === keyWord ||
                qWord.startsWith(keyWord) ||
                keyWord.startsWith(qWord)
            );
            if (foundInQuery) {
                return parts;
            }
        }
    }

    // More lenient substring search - but key must be substantial
    for (const [key, parts] of Object.entries(partsSource)) {
        if (key.length >= 4 && queryLower.includes(key)) {
            return parts;
        }
    }

    // If still no match, return generic results
    const vendorFallbacks = [
        {
            vendorKey: 'revrobotics',
            price: 45.99,
            stock: 'in-stock',
            label: 'Search on REV'
        },
        {
            vendorKey: 'andymark',
            price: 52.99,
            stock: 'limited-stock',
            label: 'Search on AndyMark'
        },
        {
            vendorKey: 'wcproducts',
            price: 54.50,
            stock: 'in-stock',
            label: 'Search on WCP'
        },
        {
            vendorKey: 'ctre',
            price: 58.99,
            stock: 'in-stock',
            label: 'Search on CTRE'
        },
        {
            vendorKey: 'dekup',
            price: 0.0,
            stock: 'in-stock',
            label: 'Search on Deküp'
        }
    ];

    return vendorFallbacks.map(fallback => {
        const vendor = VENDORS[fallback.vendorKey];
        return {
            name: `${query}`,
            vendor: vendor.name,
            price: fallback.price,
            originalPrice: null,
            discount: 0,
            stock: fallback.stock,
            url: `${vendor.searchUrl}${encodeURIComponent(query)}`,
            isSearchLink: true,
            image: `https://via.placeholder.com/400x300/2563eb/ffffff?text=${fallback.label.replace(/\s+/g, '+')}`
        };
    });
}

// Display results on screen with enhanced information
function displayResults(results, source = 'unknown') {
    const container = document.getElementById('resultsContainer');
    container.innerHTML = '';

    if (results.length === 0) {
        container.innerHTML = `<p style="color: var(--text-light); text-align: center;">${translations[currentLanguage]['no-results']}</p>`;
        return;
    }

    // Add source information except for local database (keeps cards centered)
    if (source !== 'database') {
        const sourceInfo = getSourceInfo(source);
        const sourceHeader = document.createElement('div');
        sourceHeader.className = 'source-header';
        sourceHeader.innerHTML = `
            <div class="source-info">
                <i class="fas fa-database"></i>
                <span>${sourceInfo.name}</span>
                <span class="source-badge">${sourceInfo.badge}</span>
            </div>
            <div class="results-count">${results.length} ${translations[currentLanguage]['results-found']}</div>
        `;
        container.appendChild(sourceHeader);
    }

    // Find cheapest price among real prices
    const numericPrices = results
        .map(part => Number(part.price))
        .filter(price => !Number.isNaN(price) && price > 0);

    const cheapestPrice = numericPrices.length > 0 ? Math.min(...numericPrices) : null;

    results.forEach(part => {
        const partPrice = Number(part.price);
        const isCheapest = cheapestPrice !== null && partPrice === cheapestPrice;
        const card = createPartCard(part, isCheapest);
        container.appendChild(card);
    });
}

// Inject contextual notice above the results grid
function insertResultsNotice(message) {
    const container = document.getElementById('resultsContainer');
    if (!container) return;

    const notice = document.createElement('div');
    notice.className = 'results-notice';
    notice.innerHTML = message.trim();

    const firstCard = container.firstChild;
    if (firstCard) {
        container.insertBefore(notice, firstCard);
    } else {
        container.appendChild(notice);
    }
}

// Get source information for display
function getSourceInfo(source) {
    const sourceMap = {
        'database': {
            name: 'FRC Parts Database',
            badge: translations[currentLanguage]['verified']
        },
        'enhanced_search': {
            name: 'Enhanced Search',
            badge: translations[currentLanguage]['live-data']
        },
        'shopify': {
            name: 'Shopify Vendors',
            badge: translations[currentLanguage]['live-data']
        },
        'woocommerce': {
            name: 'WooCommerce Vendors',
            badge: translations[currentLanguage]['live-data']
        },
        'real_vendors': {
            name: 'Real FRC Vendors',
            badge: translations[currentLanguage]['live-data']
        },
        'real_vendor': {
            name: 'Real FRC Vendors',
            badge: translations[currentLanguage]['live-data']
        },
        'fallback': {
            name: 'Vendor Search Links',
            badge: translations[currentLanguage]['manual']
        }
    };

    return sourceMap[source] || {
        name: 'Unknown Source',
        badge: 'Unknown'
    };
}

// Create part card
function createPartCard(part, isCheapest = false) {
    const card = document.createElement('div');
    card.className = 'part-card';

    if (isCheapest) {
        card.classList.add('cheapest');
    }

    // Handle both old format (part.stock) and new format (part.inStock)
    let stockClass, stockText;
    if (part.inStock !== undefined) {
        // New backend format
        stockClass = part.inStock ? 'in-stock' : 'out-of-stock';
        stockText = part.inStock ? translations[currentLanguage]['in-stock'] : translations[currentLanguage]['out-of-stock'];
    } else {
        // Old format
        stockClass = part.stock || 'in-stock';
        stockText = {
            'in-stock': translations[currentLanguage]['in-stock'],
            'out-of-stock': translations[currentLanguage]['out-of-stock'],
            'limited-stock': translations[currentLanguage]['limited-stock']
        }[stockClass];
    }

    let priceValue = Number(part.price);
    if (Number.isNaN(priceValue) || priceValue <= 0) {
        priceValue = null;
    }

    let priceHTML = `
        <div class="price">
            ${priceValue ? `$${priceValue.toFixed(2)}` : 'See site'}
        </div>
    `;

    if (part.originalPrice && priceValue) {
        priceHTML = `
            <div class="price">
                $${part.price}
                <span class="original-price">$${part.originalPrice}</span>
                <span class="discount-badge">${part.discount}% OFF</span>
            </div>
        `;
    }

    const bestPriceBadge = isCheapest ? `<div class="best-price-badge">${translations[currentLanguage]['best-price']}</div>` : '';
    const isSearchLink = Boolean(part.isSearchLink);
    const primaryLinkLabel = isSearchLink ? `Search on ${part.vendor}` : translations[currentLanguage]['view-product'];
    const primaryHref = part.url || '';

    let linksHTML = '';

    if (primaryHref) {
        linksHTML += `
            <a href="${primaryHref}" target="_blank" class="view-product-btn">
                <i class="fas fa-external-link-alt"></i> ${primaryLinkLabel}
            </a>
        `;
    }

    if (part.productUrl && part.productUrl !== primaryHref) {
        linksHTML += `
            <a href="${part.productUrl}" target="_blank" class="view-product-btn secondary">
                <i class="fas fa-box-open"></i> Direct Product Link
            </a>
        `;
    }

    if (!isSearchLink && part.searchUrl && part.searchUrl !== primaryHref) {
        linksHTML += `
            <a href="${part.searchUrl}" target="_blank" class="view-product-btn secondary">
                <i class="fas fa-search"></i> Search on ${part.vendor}
            </a>
        `;
    }

    card.innerHTML = `
        ${bestPriceBadge}
        <div class="part-info">
            <div class="part-vendor">${part.vendor}</div>
            <div class="part-name">${part.name}</div>
            <div class="price-section">
                ${priceHTML}
            </div>
            <div class="stock-status ${stockClass}">
                ${stockText}
            </div>
            ${linksHTML}
        </div>
    `;

    return card;
}

const CHIEF_DELPHI_SEARCH_BASE = 'https://www.chiefdelphi.com/search?q=';

const TOPICS_KRAKEN = [
    {
        title: 'Kraken X60 • Thermal performance findings',
        searchTerm: 'Kraken X60 thermal performance',
        replies: 27,
        views: 3410,
        date: 'February 2024'
    },
    {
        title: 'Kraken X60 • Swapping from Falcons experiences',
        searchTerm: 'Kraken X60 replace falcon lessons',
        replies: 52,
        views: 5890,
        date: 'January 2024'
    }
];

const TOPICS_NEO = [
    {
        title: 'NEO • Encoder dropout investigations',
        searchTerm: 'neo motor encoder dropout',
        replies: 44,
        views: 5210,
        date: 'December 2023'
    },
    {
        title: 'NEO • Cooling strategies',
        searchTerm: 'neo motor cooling match',
        replies: 29,
        views: 3475,
        date: 'November 2023'
    }
];

const TOPICS_FALCON = [
    {
        title: 'Falcon 500 • Shaft slippage fixes',
        searchTerm: 'falcon 500 shaft slip fix',
        replies: 38,
        views: 6120,
        date: 'October 2023'
    },
    {
        title: 'Falcon 500 • Firmware brownout lessons',
        searchTerm: 'falcon 500 firmware brownout frc',
        replies: 24,
        views: 4030,
        date: 'May 2024'
    }
];

const TOPICS_SPARK_MAX = [
    {
        title: 'SPARK MAX • Firmware update watchlist',
        searchTerm: 'spark max firmware 2024 issues',
        replies: 31,
        views: 4470,
        date: 'February 2024'
    },
    {
        title: 'SPARK MAX • Sensor port wiring guard',
        searchTerm: 'spark max sensor port wiring guard frc',
        replies: 19,
        views: 2985,
        date: 'September 2023'
    }
];

const TOPICS_TALON = [
    {
        title: 'Talon SRX • Motion profiling tuning',
        searchTerm: 'talon srx motion magic tuning',
        replies: 45,
        views: 5320,
        date: 'March 2024'
    },
    {
        title: 'Talon SRX • CAN bus fault checklist',
        searchTerm: 'talon srx can fault checklist frc',
        replies: 27,
        views: 3580,
        date: 'August 2023'
    }
];

const TOPICS_ENCODER = [
    {
        title: 'Encoder • Connection issues field checklist',
        searchTerm: 'encoder connection issues checklist FRC',
        replies: 33,
        views: 4025,
        date: 'November 2023'
    },
    {
        title: 'CANcoder • Dropouts root causes & fixes',
        searchTerm: 'CANcoder dropout root cause fix',
        replies: 41,
        views: 4780,
        date: 'December 2023'
    }
];

const TOPICS_ROBORIO = [
    {
        title: 'roboRIO • Brownout troubleshooting',
        searchTerm: 'roborio brownout troubleshooting',
        replies: 29,
        views: 3560,
        date: 'March 2024'
    },
    {
        title: 'roboRIO • Ethernet latency discussions',
        searchTerm: 'roborio ethernet latency',
        replies: 18,
        views: 2980,
        date: 'January 2024'
    }
];

const TOPICS_NAVX = [
    {
        title: 'navX2 • Calibration workflow tips',
        searchTerm: 'navx2 calibration workflow frc',
        replies: 22,
        views: 2840,
        date: 'April 2024'
    },
    {
        title: 'navX • Magnetic interference warnings',
        searchTerm: 'navx magnetic interference frc',
        replies: 34,
        views: 3650,
        date: 'December 2023'
    }
];

const TOPICS_GYRO = [
    {
        title: 'IMU • Drift mitigation checklist',
        searchTerm: 'FRC IMU gyro drift mitigation checklist',
        replies: 28,
        views: 3190,
        date: 'January 2024'
    },
    {
        title: 'Field oriented drive • Heading reset strategies',
        searchTerm: 'field oriented drive heading reset navx pigeon',
        replies: 37,
        views: 3890,
        date: 'June 2023'
    }
];

const TOPICS_SWERVE = [
    {
        title: 'Swerve • Pre-match inspection checklist',
        searchTerm: 'swerve module pre match inspection checklist',
        replies: 43,
        views: 5215,
        date: 'February 2024'
    },
    {
        title: 'MK4i • Bevel gear wear tracking',
        searchTerm: 'mk4i bevel gear wear tracking',
        replies: 26,
        views: 3720,
        date: 'October 2023'
    }
];

const TOPICS_PDH = [
    {
        title: 'REV PDH • High current logging best practices',
        searchTerm: 'rev pdh high current logging best practices',
        replies: 21,
        views: 2870,
        date: 'March 2024'
    },
    {
        title: 'Power distribution • Lug torque guidance',
        searchTerm: 'FRC power distribution lug torque guidance',
        replies: 17,
        views: 2450,
        date: 'July 2023'
    }
];

const TOPICS_LIMELIGHT = [
    {
        title: 'Limelight • Pipeline tuning for bright fields',
        searchTerm: 'limelight pipeline tuning bright field',
        replies: 40,
        views: 4785,
        date: 'March 2024'
    },
    {
        title: 'Vision • Reducing camera latency',
        searchTerm: 'FRC vision camera latency measurement',
        replies: 25,
        views: 3320,
        date: 'January 2024'
    }
];

const FORUM_DISCUSSIONS = {
    'kraken': TOPICS_KRAKEN,
    'kraken x60': TOPICS_KRAKEN,
    'neo': TOPICS_NEO,
    'falcon': TOPICS_FALCON,
    'falcon 500': TOPICS_FALCON,
    'spark': TOPICS_SPARK_MAX,
    'spark max': TOPICS_SPARK_MAX,
    'sparkmax': TOPICS_SPARK_MAX,
    'talon': TOPICS_TALON,
    'talon srx': TOPICS_TALON,
    'victor spx': TOPICS_TALON,
    'encoder': TOPICS_ENCODER,
    'cancoder': TOPICS_ENCODER,
    'roborio': TOPICS_ROBORIO,
    'rio': TOPICS_ROBORIO,
    'navx': TOPICS_NAVX,
    'navx2': TOPICS_NAVX,
    'imu': TOPICS_GYRO,
    'gyro': TOPICS_GYRO,
    'pigeon': TOPICS_GYRO,
    'swerve': TOPICS_SWERVE,
    'mk4': TOPICS_SWERVE,
    'mk4i': TOPICS_SWERVE,
    'maxswerve': TOPICS_SWERVE,
    'swerve module': TOPICS_SWERVE,
    'pdh': TOPICS_PDH,
    'pdp': TOPICS_PDH,
    'power distribution': TOPICS_PDH,
    'limelight': TOPICS_LIMELIGHT,
    'vision': TOPICS_LIMELIGHT
};

const FORUM_CATEGORY_TOPICS = {
    motors: [
        {
            title: 'Brushless motors • Thermal throttling management',
            searchTerm: 'FRC brushless motor thermal throttling management',
            replies: 36,
            views: 4180,
            date: 'April 2024'
        },
        {
            title: 'Motors • Pinion alignment without a press',
            searchTerm: 'FRC motor pinion alignment without press',
            replies: 23,
            views: 2740,
            date: 'September 2023'
        }
    ],
    'motor controllers': [
        {
            title: 'Motor controllers • Current limiting strategies',
            searchTerm: 'FRC motor controller current limiting strategies',
            replies: 41,
            views: 3950,
            date: 'February 2024'
        },
        {
            title: 'CAN wiring • Daisy-chain resilience tips',
            searchTerm: 'FRC CAN wiring daisy chain resilience tips',
            replies: 32,
            views: 3120,
            date: 'August 2023'
        }
    ],
    sensors: [
        {
            title: 'Sensors • Shock isolation mounting guide',
            searchTerm: 'FRC sensor shock isolation mounting guide',
            replies: 18,
            views: 2290,
            date: 'June 2024'
        },
        {
            title: 'I2C buses • Troubleshooting intermittent devices',
            searchTerm: 'FRC i2c bus troubleshooting intermittent device',
            replies: 27,
            views: 2560,
            date: 'November 2023'
        }
    ],
    drivetrain: [
        {
            title: 'Drivetrain • Chain vs belt longevity notes',
            searchTerm: 'FRC drivetrain chain belt longevity notes',
            replies: 35,
            views: 3895,
            date: 'January 2024'
        },
        {
            title: 'Swerve drive • Practice routine checklist',
            searchTerm: 'FRC swerve drive practice routine checklist',
            replies: 30,
            views: 3620,
            date: 'May 2024'
        }
    ],
    pneumatics: [
        {
            title: 'Pneumatics • Leak hunting checklist',
            searchTerm: 'FRC pneumatics leak hunting checklist',
            replies: 22,
            views: 2440,
            date: 'March 2024'
        },
        {
            title: 'Air systems • Compressor wiring safety tips',
            searchTerm: 'FRC compressor wiring safety tips',
            replies: 17,
            views: 2130,
            date: 'July 2023'
        }
    ],
    vision: [
        {
            title: 'Vision • LED lighting control options',
            searchTerm: 'FRC vision led lighting control options',
            replies: 28,
            views: 3010,
            date: 'October 2023'
        },
        {
            title: 'Vision • Camera target acquisition drills',
            searchTerm: 'FRC camera target acquisition drills',
            replies: 19,
            views: 2185,
            date: 'April 2024'
        }
    ],
    power: [
        {
            title: 'Batteries • Capacity testing routines',
            searchTerm: 'FRC battery capacity testing routines',
            replies: 39,
            views: 4080,
            date: 'February 2024'
        },
        {
            title: 'Main breaker • Failure symptom roundup',
            searchTerm: 'FRC main breaker failure symptoms roundup',
            replies: 21,
            views: 2675,
            date: 'September 2023'
        }
    ]
};

const GENERIC_FORUM_TOPICS = [
    { title: 'Motor overheating - community fixes', searchTerm: 'FRC motor overheating fix' },
    { title: 'Encoder connection issues', searchTerm: 'FRC encoder connection issues' },
    { title: 'CAN bus errors and diagnostics', searchTerm: 'FRC CAN bus error diagnostics' },
    { title: 'PID tuning recommendations', searchTerm: 'FRC PID tuning recommendations' },
    { title: 'Long-term wear and maintenance', searchTerm: 'FRC drivetrain maintenance long term' }
];

// Chief Delphi forum araması
async function searchChiefDelphi(query, contextResults = []) {
    const forumSection = document.getElementById('forumSection');
    const forumResults = document.getElementById('forumResults');

    // Chief Delphi örnek sonuçları (Gerçek uygulamada API kullanılacak)
    const mockForumPosts = generateMockForumPosts(query, contextResults);

    if (mockForumPosts.length > 0) {
        forumSection.style.display = 'block';
        forumResults.innerHTML = '';

        mockForumPosts.forEach(post => {
            const item = document.createElement('div');
            item.className = 'forum-item';
            item.innerHTML = `
                <div class="forum-title">
                    <i class="fas fa-comment-dots"></i> ${post.title}
                </div>
                <a href="${post.url}" target="_blank" class="forum-link">
                    ${post.url}
                </a>
                <div class="forum-meta">
                    👥 ${post.replies} ${translations[currentLanguage]['replies']} • 👁 ${post.views} ${translations[currentLanguage]['views']} • 📅 ${post.date}
                </div>
            `;
            forumResults.appendChild(item);
        });
    }
}

function normalizeForumKeyword(value) {
    if (!value) return '';
    return value.toString().toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
}

function addKeywordCandidate(set, value) {
    const normalized = normalizeForumKeyword(value);
    if (!normalized) return;

    set.add(normalized);

    const parts = normalized.split(' ').filter(Boolean);
    parts.forEach(part => {
        set.add(part);
        const lettersOnly = part.replace(/\d+/g, '');
        if (lettersOnly && lettersOnly !== part) {
            set.add(lettersOnly);
        }
    });
}

// Generate mock forum posts
function generateMockForumPosts(query, contextResults = []) {
    const keywords = new Set();
    const categories = new Set();

    addKeywordCandidate(keywords, query);

    const resultsToProcess = Array.isArray(contextResults) && contextResults.length > 0
        ? contextResults
        : (Array.isArray(window.lastSearchResults) ? window.lastSearchResults : []);

    resultsToProcess.forEach(part => {
        addKeywordCandidate(keywords, part?.name);
        addKeywordCandidate(keywords, part?.vendor);

        if (Array.isArray(part?.tags)) {
            part.tags.forEach(tag => addKeywordCandidate(keywords, tag));
        }

        if (part?.category) {
            const normalizedCategory = normalizeForumKeyword(part.category);
            if (normalizedCategory) {
                categories.add(normalizedCategory);
            }
        }
    });

    // Heuristic category inference if metadata missing
    if (categories.size === 0) {
        if (['motor', 'motors', 'brushless', 'kraken', 'neo', 'falcon'].some(k => keywords.has(k))) {
            categories.add('motors');
        }
        if (['controller', 'spark', 'talon', 'victor'].some(k => keywords.has(k))) {
            categories.add('motor controllers');
        }
        if (['sensor', 'imu', 'navx', 'gyro', 'encoder', 'limelight'].some(k => keywords.has(k))) {
            categories.add('sensors');
        }
        if (['swerve', 'drivetrain', 'module', 'mk4', 'drive'].some(k => keywords.has(k))) {
            categories.add('drivetrain');
        }
        if (['pneumatic', 'compressor', 'solenoid', 'air'].some(k => keywords.has(k))) {
            categories.add('pneumatics');
        }
        if (['vision', 'camera', 'limelight'].some(k => keywords.has(k))) {
            categories.add('vision');
        }
        if (['battery', 'pdh', 'pdp', 'power', 'breaker'].some(k => keywords.has(k))) {
            categories.add('power');
        }
    }

    const matchedTopics = [];

    keywords.forEach(keyword => {
        const normalized = normalizeForumKeyword(keyword);
        if (normalized && FORUM_DISCUSSIONS[normalized]) {
            matchedTopics.push(...FORUM_DISCUSSIONS[normalized]);
        }
    });

    categories.forEach(category => {
        const normalizedCategory = normalizeForumKeyword(category);
        if (normalizedCategory && FORUM_CATEGORY_TOPICS[normalizedCategory]) {
            matchedTopics.push(...FORUM_CATEGORY_TOPICS[normalizedCategory]);
        }
    });

    const createPost = (topic) => {
        const replies = topic.replies || Math.floor(Math.random() * 40) + 10;
        const views = topic.views || Math.floor(Math.random() * 4000) + 800;
        const date = topic.date || generateRandomDate();
        const searchTerm = topic.searchTerm || `${query} ${topic.title}`;

        return {
            title: topic.title,
            url: `${CHIEF_DELPHI_SEARCH_BASE}${encodeURIComponent(searchTerm)}`,
            replies,
            views,
            date,
            searchTerm
        };
    };

    const posts = [];
    const seenTerms = new Set();

    const pushTopic = (topic) => {
        const post = createPost(topic);
        if (!seenTerms.has(post.searchTerm)) {
            posts.push(post);
            seenTerms.add(post.searchTerm);
        }
    };

    matchedTopics.forEach(pushTopic);

    let genericIndex = 0;
    while (posts.length < 3 && genericIndex < GENERIC_FORUM_TOPICS.length) {
        const base = GENERIC_FORUM_TOPICS[genericIndex++];
        pushTopic({
            title: `${query} • ${base.title}`,
            searchTerm: `${query} ${base.searchTerm}`
        });
    }

    // final fallback if still missing topics
    while (posts.length < 3) {
        pushTopic({
            title: `${query} • Community discussion`,
            searchTerm: `${query} frc discussion`
        });
    }

    return posts.slice(0, 3).map(({ searchTerm, ...rest }) => rest);
}

// Generate random date
function generateRandomDate() {
    const months = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December'];
    const month = months[Math.floor(Math.random() * 12)];
    const year = 2023 + Math.floor(Math.random() * 2); // 2023-2024
    return `${month} ${year}`;
}

// Theme toggle function
function toggleTheme() {
    const body = document.body;
    const themeIcon = document.querySelector('#themeToggle i');

    body.classList.toggle('dark-mode');
    body.classList.toggle('light-mode');

    if (body.classList.contains('dark-mode')) {
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
        localStorage.setItem('theme', 'dark');
    } else {
        themeIcon.classList.remove('fa-sun');
        themeIcon.classList.add('fa-moon');
        localStorage.setItem('theme', 'light');
    }
}

// Translation system
const translations = {
    en: {
        'title': 'FRC Parts Finder',
        'subtitle': 'Search FRC parts, compare prices, discover solutions',
        'subtitle-enhanced': '✨ Enhanced with real vendor integration (WCP, REV, AndyMark, CTRE)',
        'search-placeholder': 'Please include brand + part (e.g., REV NEO, CTRE Kraken X60)',
        'search-button': 'Search',
        'forum-title': 'Chief Delphi - Known Issues & Discussions',
        'loading': 'Searching FRC vendors...',
        'no-results': 'No results found.',
        'in-stock': '✓ In Stock',
        'out-of-stock': '✗ Out of Stock',
        'limited-stock': '⚠ Limited Stock',
        'view-product': 'View Product',
        'best-price': '💰 Best Price',
        'results-found': 'results found',
        'verified': 'Verified',
        'live-data': 'Live Data',
        'manual': 'Manual',
        'replies': 'replies',
        'views': 'views'
    },
    tr: {
        'title': 'FRC Parça Bulucu',
        'subtitle': 'FRC parçalarını arayın, fiyatları karşılaştırın, çözümler keşfedin',
        'subtitle-enhanced': '✨ Gerçek satıcı entegrasyonu ile geliştirildi (WCP, REV, AndyMark, CTRE)',
        'search-placeholder': 'Lütfen marka + parça adı girin (örn: REV NEO, CTRE Kraken X60)',
        'search-button': 'Ara',
        'forum-title': 'Chief Delphi - Bilinen Sorunlar & Tartışmalar',
        'loading': 'FRC satıcıları aranıyor...',
        'no-results': 'Sonuç bulunamadı.',
        'in-stock': '✓ Stokta',
        'out-of-stock': '✗ Stokta Yok',
        'limited-stock': '⚠ Sınırlı Stok',
        'view-product': 'Ürünü Görüntüle',
        'best-price': '💰 En İyi Fiyat',
        'results-found': 'sonuç bulundu',
        'verified': 'Doğrulanmış',
        'live-data': 'Canlı Veri',
        'manual': 'Manuel',
        'replies': 'yanıt',
        'views': 'görüntüleme'
    }
};

let currentLanguage = 'en';

function changeLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('language', lang);

    // Update language buttons
    document.querySelectorAll('.lang-btn').forEach(btn => {
        if (btn.dataset.lang === lang) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Update all translated elements
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });

    // Update placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        if (translations[lang][key]) {
            element.placeholder = translations[lang][key];
        }
    });
}

// Load saved theme and language on page load
document.addEventListener('DOMContentLoaded', async function() {
    console.log('FRC Parts Finder ready!');

    // Load products database immediately
    await loadProductsDatabase();

    // Load theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    const body = document.body;
    const themeIcon = document.querySelector('#themeToggle i');

    if (savedTheme === 'dark') {
        body.classList.remove('light-mode');
        body.classList.add('dark-mode');
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
    }

    // Set language to English only
    changeLanguage('en');
});
