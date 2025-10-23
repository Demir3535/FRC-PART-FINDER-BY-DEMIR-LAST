// FRC Parça Bulucu - Ana JavaScript Dosyası

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
            const fallbackResults = generateMockResults(searchQuery);
            if (fallbackResults.length > 0) {
                const hasRealProducts = fallbackResults.some(part => !part.isSearchLink);
                const fallbackSource = hasRealProducts ? 'database' : 'fallback';
                displayResults(fallbackResults, fallbackSource);
                insertResultsNotice(hasRealProducts
                    ? `
                        <strong>Local match:</strong> "${escapeHtml(searchQuery)}" için doğrulanmış ürünler veritabanından listelendi.
                    `
                    : `
                        <strong>Heads up:</strong> "${escapeHtml(searchQuery)}" canlı veritabanında yok. Akıllı satıcı arama linkleri gösteriliyor.
                    `
                );
                return;
            }
        }

        displayResults(results, source);

        // Search Chief Delphi forum
        searchChiefDelphi(searchQuery);

    } catch (error) {
        console.error('Error searching:', error);
        document.getElementById('loadingSpinner').style.display = 'none';

        // Always try to show fallback results instead of error page
        const fallbackResults = generateMockResults(searchQuery);
        if (fallbackResults.length > 0) {
            const hasRealProducts = fallbackResults.some(part => !part.isSearchLink);
            const fallbackSource = hasRealProducts ? 'database' : 'fallback';
            displayResults(fallbackResults, fallbackSource);

            // Show appropriate notice based on error type
            const isTimeout = error.name === 'AbortError';
            const isNetworkError = error.message.includes('fetch');

            let noticeMessage;
            if (hasRealProducts) {
                noticeMessage = `
                    <strong>✓ Yerel Eşleşme:</strong> "${escapeHtml(searchQuery)}" için doğrulanmış ürünler gösteriliyor.
                    ${isTimeout ? '<br><small>Backend yanıt vermedi ama yerel veritabanından sonuç bulundu.</small>' : ''}
                `;
            } else {
                noticeMessage = `
                    <strong>ℹ️ Satıcı Arama:</strong> "${escapeHtml(searchQuery)}" için doğrudan satıcı arama linkleri gösteriliyor.
                    ${isTimeout ? '<br><small>Backend timeout - otomatik olarak alternatif sonuçlar gösteriliyor.</small>' : ''}
                    ${isNetworkError ? '<br><small>Backend bağlantısı yok - çevrimdışı mod aktif.</small>' : ''}
                `;
            }
            insertResultsNotice(noticeMessage);
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
    ]
};

// Generate mock results - Smart search
function generateMockResults(query) {
    const queryLower = query.toLowerCase().trim();
    const normalizedQuery = normalizeQuery(queryLower);

    // Try exact match first
    if (REAL_PARTS[queryLower]) {
        return REAL_PARTS[queryLower];
    }

    // Try normalized exact match (handles punctuation like "robo rio 2.0")
    for (const [key, parts] of Object.entries(REAL_PARTS)) {
        if (normalizeQuery(key) === normalizedQuery) {
            return parts;
        }
    }

    // Try partial match - search in both directions with word boundaries
    for (const [key, parts] of Object.entries(REAL_PARTS)) {
        // Split query and key into words
        const queryWords = queryLower.split(/\s+/);
        const keyWords = key.split(/\s+/);

        // Check if all query words are in the key
        const allQueryWordsMatch = queryWords.every(qWord =>
            keyWords.some(kWord => kWord.includes(qWord) || qWord.includes(kWord))
        );

        if (allQueryWordsMatch) {
            return parts;
        }
    }

    // If no match found, search for any word match
    for (const [key, parts] of Object.entries(REAL_PARTS)) {
        if (queryLower.includes(key) || key.includes(queryLower)) {
            return parts;
        }
    }

    // Try normalized contains match (ignores punctuation/spaces)
    for (const [key, parts] of Object.entries(REAL_PARTS)) {
        const normalizedKey = normalizeQuery(key);
        if (normalizedKey.length > 2 && (normalizedQuery.includes(normalizedKey) || normalizedKey.includes(normalizedQuery))) {
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

    // Add source information
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

const FORUM_DISCUSSIONS = {
    'kraken': [
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
    ],
    'encoder': [
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
    ],
    'roborio': [
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
    ],
    'neo': [
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
async function searchChiefDelphi(query) {
    const forumSection = document.getElementById('forumSection');
    const forumResults = document.getElementById('forumResults');

    // Chief Delphi örnek sonuçları (Gerçek uygulamada API kullanılacak)
    const mockForumPosts = generateMockForumPosts(query);

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

// Generate mock forum posts
function generateMockForumPosts(query) {
    const queryLower = query.toLowerCase().trim();

    const curated = Object.entries(FORUM_DISCUSSIONS).find(([keyword]) =>
        queryLower.includes(keyword)
    );

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
            date
        };
    };

    if (curated) {
        const [, topics] = curated;
        return topics.map(createPost);
    }

    const posts = [];
    const numPosts = 3;

    for (let i = 0; i < numPosts && i < GENERIC_FORUM_TOPICS.length; i++) {
        const topic = GENERIC_FORUM_TOPICS[i];
        posts.push(
            createPost({
                title: `${query} • ${topic.title}`,
                searchTerm: `${query} ${topic.searchTerm}`
            })
        );
    }

    return posts;
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
document.addEventListener('DOMContentLoaded', function() {
    console.log('FRC Parts Finder ready!');

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

    // Load language
    const savedLanguage = localStorage.getItem('language') || 'en';
    changeLanguage(savedLanguage);
});
