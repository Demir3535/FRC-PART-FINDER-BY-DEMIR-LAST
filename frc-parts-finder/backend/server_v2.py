from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus
import time

app = Flask(__name__)
CORS(app)

# Generic scraper that works for any search query
def scrape_andymark_generic(search_query):
    """Scrape AndyMark for ANY product search"""
    results = []
    try:
        url = f"https://www.andymark.com/search?q={quote_plus(search_query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        print(f"  → Searching AndyMark: {url}")
        response = requests.get(url, headers=headers, timeout=8)

        if response.status_code != 200:
            print(f"  ✗ AndyMark returned status {response.status_code}")
            return results

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all product cards - AndyMark uses various classes
        products = soup.find_all('div', class_='ProductItem')
        if not products:
            products = soup.find_all('article', class_='product-item')
        if not products:
            products = soup.find_all('div', class_='product-card')

        print(f"  → Found {len(products)} products on AndyMark")

        for product in products[:5]:  # Limit to 5 results
            try:
                # Try multiple possible selectors
                name_elem = (product.find('h3', class_='ProductItem-title') or
                           product.find('a', class_='product-item__title') or
                           product.find('h2', class_='product-title') or
                           product.find('a', class_='ProductItem-title'))

                price_elem = (product.find('span', class_='Price') or
                            product.find('span', class_='price') or
                            product.find('div', class_='product-price'))

                if name_elem and price_elem:
                    name = name_elem.get_text(strip=True)

                    # Get URL
                    link = name_elem if name_elem.name == 'a' else name_elem.find_parent('a')
                    if link and link.get('href'):
                        product_url = link['href']
                        if not product_url.startswith('http'):
                            product_url = 'https://www.andymark.com' + product_url
                    else:
                        continue

                    # Extract price
                    price_text = price_elem.get_text(strip=True)
                    price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                    if price_match:
                        price = float(price_match.group(1).replace(',', ''))
                    else:
                        continue

                    results.append({
                        'name': name,
                        'vendor': 'AndyMark',
                        'price': price,
                        'url': product_url,
                        'inStock': True,
                        'onSale': False
                    })
                    print(f"  ✓ Found: {name} - ${price}")

            except Exception as e:
                print(f"  ✗ Error parsing product: {e}")
                continue

    except Exception as e:
        print(f"  ✗ Error scraping AndyMark: {e}")

    return results


def scrape_revrobotics_generic(search_query):
    """Scrape REV Robotics for ANY product search"""
    results = []
    try:
        url = f"https://www.revrobotics.com/search/?q={quote_plus(search_query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        print(f"  → Searching REV Robotics: {url}")
        response = requests.get(url, headers=headers, timeout=8)

        if response.status_code != 200:
            return results

        soup = BeautifulSoup(response.content, 'html.parser')
        products = soup.find_all('div', class_='product')

        print(f"  → Found {len(products)} products on REV")

        for product in products[:5]:
            try:
                name_elem = product.find('h4', class_='name') or product.find('a', class_='product-name')
                price_elem = product.find('span', class_='price') or product.find('div', class_='price')

                if name_elem and price_elem:
                    link = name_elem.find('a')
                    name = link.get_text(strip=True) if link else name_elem.get_text(strip=True)

                    product_url = link['href'] if link else ''
                    if product_url and not product_url.startswith('http'):
                        product_url = 'https://www.revrobotics.com' + product_url

                    price_text = price_elem.get_text(strip=True)
                    price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                    price = float(price_match.group(1).replace(',', '')) if price_match else 0

                    if price > 0:
                        results.append({
                            'name': name,
                            'vendor': 'REV Robotics',
                            'price': price,
                            'url': product_url,
                            'inStock': True,
                            'onSale': False
                        })
                        print(f"  ✓ Found: {name} - ${price}")

            except Exception as e:
                continue

    except Exception as e:
        print(f"  ✗ Error scraping REV: {e}")

    return results


def scrape_vexrobotics_generic(search_query):
    """Scrape VEX Robotics for ANY product search"""
    results = []
    try:
        url = f"https://www.vexrobotics.com/catalogsearch/result/?q={quote_plus(search_query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        print(f"  → Searching VEX Robotics: {url}")
        response = requests.get(url, headers=headers, timeout=8)

        if response.status_code != 200:
            return results

        soup = BeautifulSoup(response.content, 'html.parser')
        products = soup.find_all('li', class_='product-item')

        print(f"  → Found {len(products)} products on VEX")

        for product in products[:5]:
            try:
                name_elem = product.find('a', class_='product-item-link')
                price_elem = product.find('span', class_='price')

                if name_elem and price_elem:
                    name = name_elem.get_text(strip=True)
                    product_url = name_elem['href']

                    price_text = price_elem.get_text(strip=True)
                    price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                    price = float(price_match.group(1).replace(',', '')) if price_match else 0

                    if price > 0:
                        results.append({
                            'name': name,
                            'vendor': 'VEX Robotics',
                            'price': price,
                            'url': product_url,
                            'inStock': True,
                            'onSale': False
                        })
                        print(f"  ✓ Found: {name} - ${price}")

            except Exception as e:
                continue

    except Exception as e:
        print(f"  ✗ Error scraping VEX: {e}")

    return results


def scrape_wcproducts_generic(search_query):
    """Scrape WCP for ANY product search"""
    results = []
    try:
        url = f"https://wcproducts.com/search?q={quote_plus(search_query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        print(f"  → Searching WCP: {url}")
        response = requests.get(url, headers=headers, timeout=8)

        if response.status_code != 200:
            return results

        soup = BeautifulSoup(response.content, 'html.parser')
        products = soup.find_all('div', class_='product-card')

        print(f"  → Found {len(products)} products on WCP")

        for product in products[:5]:
            try:
                name_elem = product.find('a', class_='product-card__title')
                price_elem = product.find('span', class_='price-item')

                if name_elem and price_elem:
                    name = name_elem.get_text(strip=True)
                    product_url = 'https://wcproducts.com' + name_elem['href']

                    price_text = price_elem.get_text(strip=True)
                    price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                    price = float(price_match.group(1).replace(',', '')) if price_match else 0

                    if price > 0:
                        results.append({
                            'name': name,
                            'vendor': 'WCP (West Coast Products)',
                            'price': price,
                            'url': product_url,
                            'inStock': True,
                            'onSale': False
                        })
                        print(f"  ✓ Found: {name} - ${price}")

            except Exception as e:
                continue

    except Exception as e:
        print(f"  ✗ Error scraping WCP: {e}")

    return results


def scrape_ctre_generic(search_query):
    """Scrape CTRE for ANY product search"""
    results = []
    try:
        url = f"https://store.ctr-electronics.com/search?q={quote_plus(search_query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        print(f"  → Searching CTRE: {url}")
        response = requests.get(url, headers=headers, timeout=8)

        if response.status_code != 200:
            return results

        soup = BeautifulSoup(response.content, 'html.parser')
        products = soup.find_all('div', class_='product-item')

        print(f"  → Found {len(products)} products on CTRE")

        for product in products[:5]:
            try:
                name_elem = product.find('a', class_='product-item__title')
                price_elem = product.find('span', class_='price-item')

                if name_elem and price_elem:
                    name = name_elem.get_text(strip=True)
                    product_url = 'https://store.ctr-electronics.com' + name_elem['href']

                    price_text = price_elem.get_text(strip=True)
                    price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                    price = float(price_match.group(1).replace(',', '')) if price_match else 0

                    if price > 0:
                        results.append({
                            'name': name,
                            'vendor': 'CTRE',
                            'price': price,
                            'url': product_url,
                            'inStock': True,
                            'onSale': False
                        })
                        print(f"  ✓ Found: {name} - ${price}")

            except Exception as e:
                continue

    except Exception as e:
        print(f"  ✗ Error scraping CTRE: {e}")

    return results


@app.route('/api/search', methods=['GET'])
def search():
    """Main search endpoint - searches ALL vendors for ANY product"""
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify({'error': 'Search query is required'}), 400

    print(f"\n{'='*60}")
    print(f"🔍 Searching for: '{query}'")
    print(f"{'='*60}")

    all_results = []

    # Try scraping all vendors
    print("\n📦 Scraping vendors...")
    all_results.extend(scrape_andymark_generic(query))
    all_results.extend(scrape_revrobotics_generic(query))
    all_results.extend(scrape_vexrobotics_generic(query))
    all_results.extend(scrape_wcproducts_generic(query))
    all_results.extend(scrape_ctre_generic(query))

    print(f"\n✅ Total results found: {len(all_results)}")
    print(f"{'='*60}\n")

    return jsonify({
        'query': query,
        'results': all_results,
        'count': len(all_results)
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'FRC Parts Finder API is running'})


if __name__ == '__main__':
    print("="*60)
    print("🚀 FRC Parts Finder Backend Server v2.0")
    print("="*60)
    print("✅ Generic search enabled - search ANY FRC part!")
    print("🌐 API available at: http://localhost:5001")
    print("="*60)
    app.run(debug=True, port=5001)
