"""
FRC Parts Finder - Enhanced Backend Server
Shopify/WooCommerce tabanlı arama sistemi ile entegre edilmiş
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import logging
from typing import Dict, List, Optional

# Import our new modules
from shopify_search import ShopifySearchEngine
from woocommerce_search import WooCommerceSearchEngine
from json_ld_validator import JSONLDValidator
from cache_manager import CacheManager
from simple_vendor_search import SimpleVendorSearch

# Import existing modules
from frc_parts_db import FRC_PARTS_DATABASE, VENDOR_SEARCH_URLS

app = Flask(__name__)
CORS(app)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize search engines and cache
shopify_engine = ShopifySearchEngine(rate_limit_delay=0.5)
woocommerce_engine = WooCommerceSearchEngine(rate_limit_delay=0.5)
real_vendor_engine = SimpleVendorSearch(rate_limit_delay=1.0)
json_ld_validator = JSONLDValidator()
cache_manager = CacheManager()

# Default headers for requests
DEFAULT_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0 Safari/537.36'
    )
}
REQUEST_TIMEOUT = 8

# FRC parça kategorileri ve canonical özellikleri
FRC_CANONICAL_SPECS = {
    'neo': {
        'must_keywords': ['NEO', 'brushless'],
        'optional_keywords': ['motor', '550'],
        'brands': ['REV', 'REV Robotics']
    },
    'kraken': {
        'must_keywords': ['Kraken', 'X60'],
        'optional_keywords': ['brushless', 'motor'],
        'brands': ['WCP', 'West Coast Products']
    },
    'spark_max': {
        'must_keywords': ['SPARK', 'MAX'],
        'optional_keywords': ['controller', 'esc'],
        'brands': ['REV', 'REV Robotics']
    },
    'talon_srx': {
        'must_keywords': ['Talon', 'SRX'],
        'optional_keywords': ['controller', 'esc'],
        'brands': ['CTRE']
    },
    'victor_spx': {
        'must_keywords': ['Victor', 'SPX'],
        'optional_keywords': ['controller', 'esc'],
        'brands': ['CTRE']
    },
    'cancoder': {
        'must_keywords': ['CANcoder'],
        'optional_keywords': ['encoder', 'magnetic'],
        'brands': ['CTRE']
    }
}

def resolve_query(query: str):
    """Kullanıcının sorgusunu veri tabanındaki parça ile eşleştir."""
    query_lower = query.strip().lower()
    if not query_lower:
        return None

    if query_lower in FRC_PARTS_DATABASE:
        result = FRC_PARTS_DATABASE[query_lower]
        if isinstance(result, str):
            result = FRC_PARTS_DATABASE[result]
        return result

    # kısmi eşleşme: bütün kelimeler geçsin
    query_words = query_lower.split()
    for key, value in FRC_PARTS_DATABASE.items():
        if isinstance(value, str):
            continue
        key_words = key.split()
        if all(any(qw in kw or kw in qw for kw in key_words) for qw in query_words):
            return value

    return None

def get_canonical_specs(query: str) -> Optional[Dict]:
    """Sorgu için canonical özellikleri belirle"""
    query_lower = query.lower()
    
    for part_name, specs in FRC_CANONICAL_SPECS.items():
        if any(keyword.lower() in query_lower for keyword in specs['must_keywords']):
            return specs
    
    return None

def is_url_alive(url: str) -> bool:
    """URL'nin canlı olup olmadığını kontrol et (cache'li)"""
    if not url:
        return False
    
    # Önbellekten kontrol et
    cached_status = cache_manager.get_url_status(url)
    if cached_status is not None:
        return cached_status.get('alive', False)
    
    # URL'yi kontrol et
    try:
        response = requests.head(
            url,
            allow_redirects=True,
            timeout=REQUEST_TIMEOUT,
            headers=DEFAULT_HEADERS,
        )
        alive = response.status_code < 400
    except Exception:
        alive = False
    
    # Sonucu önbelleğe kaydet
    cache_manager.set_url_status(url, {'alive': alive}, ttl=3600)  # 1 saat
    
    return alive

def search_shopify_vendors(query: str, canonical_specs: Optional[Dict] = None) -> List[Dict]:
    """Shopify tedarikçilerinde arama yap"""
    try:
        # Önbellekten kontrol et
        cached_results = cache_manager.get_search_results(query, "shopify")
        if cached_results:
            return cached_results
        
        # Arama yap
        all_results = shopify_engine.search_all_vendors(query, canonical_specs)
        
        # Sonuçları birleştir ve normalize et
        combined_results = []
        for vendor_name, products in all_results.items():
            for product in products:
                product['vendor'] = vendor_name
                product['source'] = 'shopify'
                combined_results.append(product)
        
        # Sonuçları önbelleğe kaydet
        cache_manager.set_search_results(query, combined_results, "shopify", ttl=7200)  # 2 saat
        
        return combined_results
        
    except Exception as e:
        logger.error(f"Shopify search failed: {e}")
        return []

def search_woocommerce_vendors(query: str, canonical_specs: Optional[Dict] = None) -> List[Dict]:
    """WooCommerce tedarikçilerinde arama yap"""
    try:
        # Önbellekten kontrol et
        cached_results = cache_manager.get_search_results(query, "woocommerce")
        if cached_results:
            return cached_results
        
        # Arama yap
        all_results = woocommerce_engine.search_all_vendors(query, canonical_specs)
        
        # Sonuçları birleştir ve normalize et
        combined_results = []
        for vendor_name, products in all_results.items():
            for product in products:
                product['vendor'] = vendor_name
                product['source'] = 'woocommerce'
                combined_results.append(product)
        
        # Sonuçları önbelleğe kaydet
        cache_manager.set_search_results(query, combined_results, "woocommerce", ttl=7200)  # 2 saat
        
        return combined_results
        
    except Exception as e:
        logger.error(f"WooCommerce search failed: {e}")
        return []

def search_real_vendors(query: str, canonical_specs: Optional[Dict] = None) -> List[Dict]:
    """Gerçek FRC tedarikçilerinde arama yap (WCP, REV, AndyMark, CTRE)"""
    try:
        # Önbellekten kontrol et
        cached_results = cache_manager.get_search_results(query, "real_vendors")
        if cached_results:
            return cached_results
        
        # Arama yap
        all_results = real_vendor_engine.search_all_vendors(query)
        
        # Sonuçları birleştir ve normalize et
        combined_results = []
        for vendor_name, products in all_results.items():
            for product in products:
                product['vendor'] = vendor_name
                product['source'] = 'real_vendor'
                combined_results.append(product)
        
        # Sonuçları önbelleğe kaydet
        cache_manager.set_search_results(query, combined_results, "real_vendors", ttl=3600)  # 1 saat
        
        return combined_results
        
    except Exception as e:
        logger.error(f"Real vendor search failed: {e}")
        return []

def validate_and_enhance_products(products: List[Dict]) -> List[Dict]:
    """Ürünleri doğrula ve geliştir"""
    enhanced_products = []
    
    for product in products:
        try:
            # Önbellekten ürün bilgilerini kontrol et
            cached_product = cache_manager.get_product_info(product.get('url', ''))
            if cached_product:
                # Önbellekten gelen bilgileri kullan
                product.update(cached_product)
                enhanced_products.append(product)
                continue
            
            # URL'yi kontrol et
            if not is_url_alive(product.get('url', '')):
                continue
            
            # Ürün sayfasını çek ve JSON-LD doğrula
            try:
                response = requests.get(
                    product.get('url', ''),
                    headers=DEFAULT_HEADERS,
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    # JSON-LD çıkar
                    json_ld = json_ld_validator.extract_json_ld(response.text)
                    
                    if json_ld:
                        # Ürün bilgilerini çıkar ve doğrula
                        enhanced_info = json_ld_validator.extract_product_info(json_ld, product.get('url', ''))
                        
                        # FRC parça kontrolü
                        is_frc, category, score = json_ld_validator.is_frc_part(json_ld, response.text)
                        
                        if is_frc and score >= 0.3:  # Eşik değeri
                            product.update(enhanced_info)
                            product['frc_category'] = category
                            product['match_score'] = score
                            
                            # Önbelleğe kaydet
                            cache_manager.set_product_info(
                                product.get('url', ''),
                                enhanced_info,
                                ttl=86400  # 24 saat
                            )
                            
                            enhanced_products.append(product)
                    else:
                        # JSON-LD yoksa mevcut bilgileri kullan
                        enhanced_products.append(product)
                        
            except Exception as e:
                logger.warning(f"Failed to validate product {product.get('url', '')}: {e}")
                # Hata durumunda mevcut bilgileri kullan
                enhanced_products.append(product)
                
        except Exception as e:
            logger.warning(f"Failed to process product: {e}")
            continue
    
    return enhanced_products

def build_fallback_links(query: str):
    """Fallback arama linkleri oluştur"""
    encoded = query.strip().replace(' ', '+')
    links = []
    for vendor, base_url in VENDOR_SEARCH_URLS.items():
        links.append({
            'name': f'{query} aramasını {vendor} üzerinde aç',
            'vendor': vendor,
            'price': 0.0,
            'url': f'{base_url}{encoded}',
            'inStock': True,
            'isSearchLink': True,
            'source': 'fallback'
        })
    return links

@app.route('/api/search', methods=['GET'])
def search():
    """Ana arama endpoint'i"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Arama terimi gerekli'}), 400

    logger.info(f'🔍 Aranan: {query}')

    # 1. Önce mevcut veritabanından kontrol et
    results = resolve_query(query)
    
    if results:
        # URL'leri kontrol et ve canlı olanları filtrele
        filtered = [item for item in results if is_url_alive(item.get('url'))]
        if filtered:
            logger.info(f'✅ {len(filtered)} sonuç veritabanından döndü')
            return jsonify({
                'query': query,
                'results': filtered,
                'count': len(filtered),
                'source': 'database'
            })

    # 2. Canonical özellikleri belirle
    canonical_specs = get_canonical_specs(query)
    
    # 3. Gerçek FRC tedarikçilerinde arama (WCP, REV, AndyMark, CTRE)
    real_vendor_results = search_real_vendors(query, canonical_specs)
    
    # 4. Shopify tedarikçilerinde arama (backup)
    shopify_results = search_shopify_vendors(query, canonical_specs)
    
    # 5. WooCommerce tedarikçilerinde arama (backup)
    woocommerce_results = search_woocommerce_vendors(query, canonical_specs)
    
    # 6. Tüm sonuçları birleştir (gerçek tedarikçiler öncelikli)
    all_results = real_vendor_results + shopify_results + woocommerce_results
    
    if all_results:
        # Ürünleri doğrula ve geliştir
        validated_results = validate_and_enhance_products(all_results)
        
        if validated_results:
            logger.info(f'✅ {len(validated_results)} sonuç yeni arama sisteminden döndü')
            return jsonify({
                'query': query,
                'results': validated_results,
                'count': len(validated_results),
                'source': 'enhanced_search'
            })

    # 6. Fallback arama linkleri
    logger.info('⚠️ Hiçbir sonuç bulunamadı, fallback kullanılacak')
    fallback = build_fallback_links(query)
    logger.info(f'✅ {len(fallback)} fallback linki oluşturuldu')

    return jsonify({
        'query': query,
        'results': fallback,
        'count': len(fallback),
        'source': 'fallback'
    })

@app.route('/api/search/shopify', methods=['GET'])
def search_shopify():
    """Shopify tedarikçilerinde arama"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Arama terimi gerekli'}), 400
    
    canonical_specs = get_canonical_specs(query)
    results = search_shopify_vendors(query, canonical_specs)
    
    return jsonify({
        'query': query,
        'results': results,
        'count': len(results),
        'source': 'shopify'
    })

@app.route('/api/search/woocommerce', methods=['GET'])
def search_woocommerce():
    """WooCommerce tedarikçilerinde arama"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Arama terimi gerekli'}), 400
    
    canonical_specs = get_canonical_specs(query)
    results = search_woocommerce_vendors(query, canonical_specs)
    
    return jsonify({
        'query': query,
        'results': results,
        'count': len(results),
        'source': 'woocommerce'
    })

@app.route('/api/search/real-vendors', methods=['GET'])
def search_real_vendors_endpoint():
    """Gerçek FRC tedarikçilerinde arama (WCP, REV, AndyMark, CTRE)"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Arama terimi gerekli'}), 400
    
    canonical_specs = get_canonical_specs(query)
    results = search_real_vendors(query, canonical_specs)
    
    return jsonify({
        'query': query,
        'results': results,
        'count': len(results),
        'source': 'real_vendors',
        'vendors': ['WCP (West Coast Products)', 'REV Robotics', 'AndyMark', 'CTRE']
    })

@app.route('/api/cache/stats', methods=['GET'])
def cache_stats():
    """Önbellek istatistikleri"""
    stats = cache_manager.get_cache_stats()
    return jsonify(stats)

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Önbelleği temizle"""
    cache_manager.clear_all_cache()
    return jsonify({'message': 'Cache cleared successfully'})

@app.route('/api/cache/cleanup', methods=['POST'])
def cleanup_cache():
    """Süresi dolmuş önbellek kayıtlarını temizle"""
    cache_manager.cleanup_expired()
    return jsonify({'message': 'Expired cache entries cleaned up'})

@app.route('/api/health', methods=['GET'])
def health():
    """Sistem durumu"""
    cache_stats = cache_manager.get_cache_stats()
    categories = [key for key, value in FRC_PARTS_DATABASE.items() if isinstance(value, list)]
    
    return jsonify({
        'status': 'ok',
        'message': 'FRC Parts Finder API v3.0 - Enhanced with Shopify/WooCommerce',
        'category_count': len(categories),
        'vendors': list(VENDOR_SEARCH_URLS.keys()),
        'cache_stats': cache_stats,
        'features': [
            'Shopify search integration',
            'WooCommerce search integration',
            'JSON-LD validation',
            'Smart caching system',
            'FRC part recognition'
        ]
    })

if __name__ == '__main__':
    print('=' * 60)
    print('🚀 FRC Parts Finder Enhanced Backend Server v3.0')
    print('=' * 60)
    print('🔧 Features:')
    print('  - Shopify/WooCommerce integration')
    print('  - JSON-LD validation')
    print('  - Smart caching (24-48h TTL)')
    print('  - FRC part recognition')
    print('=' * 60)
    print('🌐 API: http://localhost:5001')
    print('📊 Cache Stats: /api/cache/stats')
    print('🧹 Cache Clear: POST /api/cache/clear')
    print('=' * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
