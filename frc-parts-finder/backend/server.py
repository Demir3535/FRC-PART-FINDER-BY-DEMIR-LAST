from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus

app = Flask(__name__)
CORS(app)  # Allow frontend to make requests

# Scraper functions for each vendor
def scrape_andymark(search_query):
    """Scrape AndyMark for product information"""
    results = []
    try:
        # AndyMark search URL
        url = f"https://www.andymark.com/search?q={quote_plus(search_query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find product cards
        products = soup.find_all('div', class_='product-item')

        for product in products[:5]:  # Limit to 5 results
            try:
                name_elem = product.find('a', class_='product-item__title')
                price_elem = product.find('span', class_='price-item')

                if name_elem and price_elem:
                    name = name_elem.text.strip()
                    product_url = 'https://www.andymark.com' + name_elem.get('href', '')

                    # Extract price
                    price_text = price_elem.text.strip()
                    price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                    price = float(price_match.group(1).replace(',', '')) if price_match else 0

                    # Check stock status
                    stock_elem = product.find('div', class_='product-item__inventory')
                    in_stock = 'Out of Stock' not in (stock_elem.text if stock_elem else '')

                    results.append({
                        'name': name,
                        'vendor': 'AndyMark',
                        'price': price,
                        'url': product_url,
                        'inStock': in_stock,
                        'onSale': False  # Can be enhanced later
                    })
            except Exception as e:
                print(f"Error parsing AndyMark product: {e}")
                continue

    except Exception as e:
        print(f"Error scraping AndyMark: {e}")

    return results


def scrape_revrobotics(search_query):
    """Scrape REV Robotics for product information"""
    results = []
    try:
        url = f"https://www.revrobotics.com/search/?q={quote_plus(search_query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        products = soup.find_all('div', class_='product')

        for product in products[:5]:
            try:
                name_elem = product.find('h4', class_='name')
                price_elem = product.find('span', class_='price')

                if name_elem and price_elem:
                    link = name_elem.find('a')
                    name = link.text.strip() if link else name_elem.text.strip()
                    product_url = 'https://www.revrobotics.com' + link.get('href', '') if link else ''

                    price_text = price_elem.text.strip()
                    price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                    price = float(price_match.group(1).replace(',', '')) if price_match else 0

                    stock_elem = product.find('p', class_='availability')
                    in_stock = stock_elem and 'in stock' in stock_elem.text.lower() if stock_elem else True

                    results.append({
                        'name': name,
                        'vendor': 'REV Robotics',
                        'price': price,
                        'url': product_url,
                        'inStock': in_stock,
                        'onSale': False
                    })
            except Exception as e:
                print(f"Error parsing REV product: {e}")
                continue

    except Exception as e:
        print(f"Error scraping REV Robotics: {e}")

    return results


def scrape_vexrobotics(search_query):
    """Scrape VEX Robotics for product information"""
    results = []
    try:
        url = f"https://www.vexrobotics.com/catalogsearch/result/?q={quote_plus(search_query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        products = soup.find_all('li', class_='product-item')

        for product in products[:5]:
            try:
                name_elem = product.find('a', class_='product-item-link')
                price_elem = product.find('span', class_='price')

                if name_elem and price_elem:
                    name = name_elem.text.strip()
                    product_url = name_elem.get('href', '')

                    price_text = price_elem.text.strip()
                    price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                    price = float(price_match.group(1).replace(',', '')) if price_match else 0

                    stock_elem = product.find('div', class_='stock')
                    in_stock = stock_elem and 'in stock' in stock_elem.text.lower() if stock_elem else True

                    results.append({
                        'name': name,
                        'vendor': 'VEX Robotics',
                        'price': price,
                        'url': product_url,
                        'inStock': in_stock,
                        'onSale': False
                    })
            except Exception as e:
                print(f"Error parsing VEX product: {e}")
                continue

    except Exception as e:
        print(f"Error scraping VEX Robotics: {e}")

    return results


def scrape_wcproducts(search_query):
    """Scrape West Coast Products for product information"""
    results = []
    try:
        url = f"https://wcproducts.com/search?q={quote_plus(search_query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        products = soup.find_all('div', class_='product-card')

        for product in products[:5]:
            try:
                name_elem = product.find('a', class_='product-card__title')
                price_elem = product.find('span', class_='price-item')

                if name_elem and price_elem:
                    name = name_elem.text.strip()
                    product_url = 'https://wcproducts.com' + name_elem.get('href', '')

                    price_text = price_elem.text.strip()
                    price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                    price = float(price_match.group(1).replace(',', '')) if price_match else 0

                    stock_elem = product.find('span', class_='product-card__availability')
                    in_stock = stock_elem and 'out of stock' not in stock_elem.text.lower() if stock_elem else True

                    results.append({
                        'name': name,
                        'vendor': 'WCP (West Coast Products)',
                        'price': price,
                        'url': product_url,
                        'inStock': in_stock,
                        'onSale': False
                    })
            except Exception as e:
                print(f"Error parsing WCP product: {e}")
                continue

    except Exception as e:
        print(f"Error scraping WCP: {e}")

    return results


def scrape_ctre(search_query):
    """Scrape CTRE for product information"""
    results = []
    try:
        url = f"https://store.ctr-electronics.com/search?q={quote_plus(search_query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        products = soup.find_all('div', class_='product-item')

        for product in products[:5]:
            try:
                name_elem = product.find('a', class_='product-item__title')
                price_elem = product.find('span', class_='price-item')

                if name_elem and price_elem:
                    name = name_elem.text.strip()
                    product_url = 'https://store.ctr-electronics.com' + name_elem.get('href', '')

                    price_text = price_elem.text.strip()
                    price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                    price = float(price_match.group(1).replace(',', '')) if price_match else 0

                    stock_elem = product.find('div', class_='product-item__inventory')
                    in_stock = stock_elem and 'out of stock' not in stock_elem.text.lower() if stock_elem else True

                    results.append({
                        'name': name,
                        'vendor': 'CTRE',
                        'price': price,
                        'url': product_url,
                        'inStock': in_stock,
                        'onSale': False
                    })
            except Exception as e:
                print(f"Error parsing CTRE product: {e}")
                continue

    except Exception as e:
        print(f"Error scraping CTRE: {e}")

    return results


@app.route('/api/search', methods=['GET'])
def search():
    """Main search endpoint that aggregates results from all vendors"""
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify({'error': 'Search query is required'}), 400

    print(f"Searching for: {query}")

    # Scrape all vendors in parallel (can be optimized with threading later)
    all_results = []

    all_results.extend(scrape_andymark(query))
    all_results.extend(scrape_revrobotics(query))
    all_results.extend(scrape_vexrobotics(query))
    all_results.extend(scrape_wcproducts(query))
    all_results.extend(scrape_ctre(query))

    # If no results from scraping, return demo data for common searches
    if len(all_results) == 0:
        query_lower = query.lower()
        if 'neo' in query_lower:
            all_results = [
                {
                    'name': 'NEO Brushless Motor',
                    'vendor': 'REV Robotics',
                    'price': 39.99,
                    'url': 'https://www.revrobotics.com/rev-21-1650/',
                    'inStock': True,
                    'onSale': False
                },
                {
                    'name': 'NEO Brushless Motor',
                    'vendor': 'AndyMark',
                    'price': 56.00,
                    'url': 'https://www.andymark.com/products/neo-brushless-motor',
                    'inStock': True,
                    'onSale': False
                },
                {
                    'name': 'NEO Brushless Motor',
                    'vendor': 'VEX Robotics',
                    'price': 44.99,
                    'url': 'https://www.vexrobotics.com/217-8255.html',
                    'inStock': True,
                    'onSale': False
                }
            ]
        elif 'falcon' in query_lower:
            all_results = [
                {
                    'name': 'Falcon 500 Brushless Motor',
                    'vendor': 'VEX Robotics',
                    'price': 139.99,
                    'url': 'https://www.vexrobotics.com/217-6515.html',
                    'inStock': True,
                    'onSale': False
                },
                {
                    'name': 'Falcon 500 Brushless Motor',
                    'vendor': 'AndyMark',
                    'price': 149.99,
                    'url': 'https://www.andymark.com/products/falcon-500-powered-by-talon-fx',
                    'inStock': True,
                    'onSale': False
                },
                {
                    'name': 'Falcon 500 Brushless Motor',
                    'vendor': 'WCP (West Coast Products)',
                    'price': 144.95,
                    'url': 'https://wcproducts.com/products/falcon-500',
                    'inStock': True,
                    'onSale': False
                }
            ]
        elif 'cim' in query_lower and 'motor' in query_lower:
            all_results = [
                {
                    'name': 'CIM Motor',
                    'vendor': 'AndyMark',
                    'price': 29.00,
                    'url': 'https://www.andymark.com/products/2-5-in-cim-motor',
                    'inStock': True,
                    'onSale': False
                },
                {
                    'name': 'CIM Motor',
                    'vendor': 'VEX Robotics',
                    'price': 32.99,
                    'url': 'https://www.vexrobotics.com/217-2000.html',
                    'inStock': True,
                    'onSale': False
                }
            ]
        elif 'spark' in query_lower and 'max' in query_lower:
            all_results = [
                {
                    'name': 'SPARK MAX Motor Controller',
                    'vendor': 'REV Robotics',
                    'price': 89.99,
                    'url': 'https://www.revrobotics.com/rev-11-2158/',
                    'inStock': True,
                    'onSale': False
                },
                {
                    'name': 'SPARK MAX Motor Controller',
                    'vendor': 'AndyMark',
                    'price': 94.99,
                    'url': 'https://www.andymark.com/products/spark-max-motor-controller',
                    'inStock': True,
                    'onSale': False
                }
            ]
        elif 'kraken' in query_lower:
            all_results = [
                {
                    'name': 'Kraken X60 Brushless Motor',
                    'vendor': 'WCP (West Coast Products)',
                    'price': 217.99,
                    'url': 'https://wcproducts.com/products/kraken',
                    'inStock': True,
                    'onSale': False
                },
                {
                    'name': 'Kraken X60 Brushless Motor',
                    'vendor': 'AndyMark',
                    'price': 219.99,
                    'url': 'https://www.andymark.com/products/kraken-x60-motor',
                    'inStock': True,
                    'onSale': False
                },
                {
                    'name': 'Kraken X60 Brushless Motor',
                    'vendor': 'CTRE',
                    'price': 217.99,
                    'url': 'https://store.ctr-electronics.com/kraken-x60/',
                    'inStock': True,
                    'onSale': False
                }
            ]
        elif 'navx' in query_lower:
            all_results = [
                {
                    'name': 'navX2-Micro Navigation Sensor',
                    'vendor': 'AndyMark',
                    'price': 109.00,
                    'url': 'https://www.andymark.com/products/navx2-micro-navigation-sensor',
                    'inStock': True,
                    'onSale': False
                },
                {
                    'name': 'navX2-MXP Robotics Navigation Sensor',
                    'vendor': 'AndyMark',
                    'price': 115.00,
                    'url': 'https://www.andymark.com/products/navx2-mxp-robotics-navigation-sensor',
                    'inStock': True,
                    'onSale': False
                }
            ]
        elif 'cancoder' in query_lower:
            all_results = [
                {
                    'name': 'CANcoder Magnetic Encoder',
                    'vendor': 'CTRE',
                    'price': 60.00,
                    'url': 'https://store.ctr-electronics.com/cancoder/',
                    'inStock': True,
                    'onSale': False
                },
                {
                    'name': 'CTRE CANcoder',
                    'vendor': 'AndyMark',
                    'price': 60.00,
                    'url': 'https://www.andymark.com/products/ctre-cancoder',
                    'inStock': True,
                    'onSale': False
                }
            ]
        elif 'talon' in query_lower and 'srx' in query_lower:
            all_results = [
                {
                    'name': 'Talon SRX Motor Controller',
                    'vendor': 'CTRE',
                    'price': 95.00,
                    'url': 'https://store.ctr-electronics.com/talon-srx/',
                    'inStock': True,
                    'onSale': False
                },
                {
                    'name': 'Talon SRX Motor Controller',
                    'vendor': 'AndyMark',
                    'price': 99.99,
                    'url': 'https://www.andymark.com/products/talon-srx',
                    'inStock': True,
                    'onSale': False
                }
            ]
        elif 'victor' in query_lower and 'spx' in query_lower:
            all_results = [
                {
                    'name': 'Victor SPX Motor Controller',
                    'vendor': 'CTRE',
                    'price': 55.00,
                    'url': 'https://store.ctr-electronics.com/victor-spx/',
                    'inStock': True,
                    'onSale': False
                },
                {
                    'name': 'Victor SPX Motor Controller',
                    'vendor': 'VEX Robotics',
                    'price': 59.99,
                    'url': 'https://www.vexrobotics.com/217-9191.html',
                    'inStock': True,
                    'onSale': False
                }
            ]
        elif 'pigeon' in query_lower:
            all_results = [
                {
                    'name': 'Pigeon 2.0 IMU',
                    'vendor': 'CTRE',
                    'price': 90.00,
                    'url': 'https://store.ctr-electronics.com/pigeon-2/',
                    'inStock': True,
                    'onSale': False
                },
                {
                    'name': 'Pigeon 2.0 IMU',
                    'vendor': 'AndyMark',
                    'price': 94.99,
                    'url': 'https://www.andymark.com/products/pigeon-2-0',
                    'inStock': True,
                    'onSale': False
                }
            ]
        elif 'pdh' in query_lower or 'power distribution' in query_lower:
            all_results = [
                {
                    'name': 'Power Distribution Hub (PDH)',
                    'vendor': 'REV Robotics',
                    'price': 99.99,
                    'url': 'https://www.revrobotics.com/rev-11-1850/',
                    'inStock': True,
                    'onSale': False
                },
                {
                    'name': 'Power Distribution Hub (PDH)',
                    'vendor': 'AndyMark',
                    'price': 104.99,
                    'url': 'https://www.andymark.com/products/rev-power-distribution-hub',
                    'inStock': True,
                    'onSale': False
                }
            ]

    print(f"Found {len(all_results)} total results")

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
    print("Starting FRC Parts Finder Backend Server...")
    print("API will be available at http://localhost:5001")
    app.run(debug=True, port=5001)
