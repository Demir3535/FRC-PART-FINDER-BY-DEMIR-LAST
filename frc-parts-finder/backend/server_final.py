from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

from frc_parts_db import FRC_PARTS_DATABASE, VENDOR_SEARCH_URLS

app = Flask(__name__)
CORS(app)

DEFAULT_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0 Safari/537.36'
    )
}
REQUEST_TIMEOUT = 8
_AVAILABILITY_CACHE = {}


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


def is_url_alive(url: str) -> bool:
    if not url:
        return False
    cached = _AVAILABILITY_CACHE.get(url)
    if cached is not None:
        return cached
    try:
        response = requests.head(
            url,
            allow_redirects=True,
            timeout=REQUEST_TIMEOUT,
            headers=DEFAULT_HEADERS,
        )
        ok = response.status_code < 400
    except Exception:
        ok = False
    _AVAILABILITY_CACHE[url] = ok
    return ok


def build_fallback_links(query: str):
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
        })
    return links


@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Arama terimi gerekli'}), 400

    print('=' * 60)
    print(f'🔍 Aranan: {query}')
    print('=' * 60)

    results = resolve_query(query)

    if results:
        filtered = [item for item in results if is_url_alive(item.get('url'))]
        if filtered:
            print(f'✅ {len(filtered)} sonuç geçerli URL ile döndü')
            return jsonify({
                'query': query,
                'results': filtered,
                'count': len(filtered),
                'source': 'database'
            })
        else:
            print('⚠️ Hiçbir URL canlı değil, fallback kullanılacak')

    print('⚠️ Doğrudan eşleşme yok, satıcı arama linkleri dönüyor')
    fallback = build_fallback_links(query)
    print(f'✅ {len(fallback)} arama linki oluşturuldu')

    return jsonify({
        'query': query,
        'results': fallback,
        'count': len(fallback),
        'source': 'fallback'
    })


@app.route('/api/health', methods=['GET'])
def health():
    categories = [key for key, value in FRC_PARTS_DATABASE.items() if isinstance(value, list)]
    return jsonify({
        'status': 'ok',
        'message': 'FRC Parts Finder API v2.0 - Statik katalog',
        'category_count': len(categories),
        'vendors': list(VENDOR_SEARCH_URLS.keys())
    })


if __name__ == '__main__':
    print('=' * 60)
    print('🚀 FRC Parts Finder Backend Server v2.0')
    print('=' * 60)
    print(f'📦 Katalog kategori sayısı: {len([k for k, v in FRC_PARTS_DATABASE.items() if isinstance(v, list)])}')
    print('🌐 API: http://localhost:5001')
    print('=' * 60)
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
