"""
WooCommerce tabanlı FRC tedarikçileri için arama sistemi
Küçük tedarikçiler ve özel mağazalar için optimize edilmiş
"""

import requests
import re
import json
import time
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WooCommerceSearchEngine:
    def __init__(self, rate_limit_delay: float = 0.5):
        """
        WooCommerce arama motoru
        
        Args:
            rate_limit_delay: Domain başına istekler arası bekleme süresi (saniye)
        """
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = {}
        
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0 Safari/537.36'
            ),
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        # FRC tedarikçileri - WooCommerce kullananlar (gerçek siteler)
        self.woocommerce_vendors = {
            'andymark.com': {
                'name': 'AndyMark',
                'api_endpoints': [
                    '/wp-json/wc/store/products',
                    '/wp-json/wc/v3/products'
                ],
                'base_url': 'https://andymark.com'
            },
            'store.ctr-electronics.com': {
                'name': 'CTRE (Cross The Road Electronics)',
                'api_endpoints': [
                    '/wp-json/wc/store/products',
                    '/wp-json/wc/v3/products'
                ],
                'base_url': 'https://store.ctr-electronics.com'
            }
        }

    def _rate_limit(self, domain: str):
        """Domain başına rate limiting"""
        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time[domain] = time.time()

    def _make_request(self, url: str, timeout: int = 10, params: Dict = None) -> Optional[requests.Response]:
        """Rate-limited HTTP request"""
        try:
            domain = urlparse(url).netloc
            self._rate_limit(domain)
            
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=timeout,
                params=params,
                allow_redirects=True
            )
            response.raise_for_status()
            return response
        except Exception as e:
            logger.warning(f"Request failed for {url}: {e}")
            return None

    def search_store_api(self, domain: str, query: str, per_page: int = 10) -> List[Dict]:
        """
        WooCommerce Store API kullanarak arama yap
        
        Args:
            domain: Tedarikçi domain
            query: Arama terimi
            per_page: Sayfa başına sonuç sayısı
            
        Returns:
            Ürün bilgileri listesi
        """
        if not domain.startswith('http'):
            domain = f"https://{domain}"
            
        # Store API endpoint'i dene
        url = f"{domain}/wp-json/wc/store/products"
        params = {
            'search': query,
            'per_page': per_page
        }
        
        response = self._make_request(url, params=params)
        if not response:
            return []
            
        try:
            data = response.json()
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.warning(f"Failed to parse Store API for {domain}: {e}")
            return []

    def search_wc_v3_api(self, domain: str, query: str, per_page: int = 10) -> List[Dict]:
        """
        WooCommerce v3 API kullanarak arama yap (authentication gerekebilir)
        
        Args:
            domain: Tedarikçi domain
            query: Arama terimi
            per_page: Sayfa başına sonuç sayısı
            
        Returns:
            Ürün bilgileri listesi
        """
        if not domain.startswith('http'):
            domain = f"https://{domain}"
            
        url = f"{domain}/wp-json/wc/v3/products"
        params = {
            'search': query,
            'per_page': per_page
        }
        
        response = self._make_request(url, params=params)
        if not response:
            return []
            
        try:
            data = response.json()
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.warning(f"Failed to parse WC v3 API for {domain}: {e}")
            return []

    def search_products_endpoint(self, domain: str, query: str) -> List[Dict]:
        """
        /products/ endpoint'ini kullanarak arama yap
        
        Args:
            domain: Tedarikçi domain
            query: Arama terimi
            
        Returns:
            Ürün bilgileri listesi
        """
        if not domain.startswith('http'):
            domain = f"https://{domain}"
            
        # WooCommerce products endpoint'i
        url = f"{domain}/products/"
        params = {'s': query}
        
        response = self._make_request(url, params=params)
        if not response:
            return []
            
        try:
            # HTML'den ürün linklerini çıkar
            html = response.text
            product_links = re.findall(r'href="([^"]*products/[^"]*)"', html)
            
            results = []
            for link in product_links[:10]:  # İlk 10 ürün
                full_url = urljoin(domain, link)
                product_info = self._extract_product_from_page(full_url)
                if product_info:
                    results.append(product_info)
                    
            return results
        except Exception as e:
            logger.warning(f"Failed to parse products page for {domain}: {e}")
            return []

    def _extract_product_from_page(self, url: str) -> Optional[Dict]:
        """
        Ürün sayfasından bilgileri çıkar
        
        Args:
            url: Ürün sayfası URL'i
            
        Returns:
            Ürün bilgileri dict'i
        """
        response = self._make_request(url)
        if not response:
            return None
            
        try:
            html = response.text
            
            # JSON-LD Product verisi ara
            json_ld = self._extract_json_ld(html)
            if json_ld:
                return self._parse_json_ld_product(json_ld, url)
            
            # HTML'den manuel parsing
            return self._parse_html_product(html, url)
            
        except Exception as e:
            logger.warning(f"Failed to extract product from {url}: {e}")
            return None

    def _extract_json_ld(self, html: str) -> Optional[Dict]:
        """HTML'den JSON-LD Product verilerini çıkar"""
        try:
            pattern = r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>'
            matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                try:
                    data = json.loads(match.strip())
                    
                    if isinstance(data, list):
                        for item in data:
                            if item.get('@type') == 'Product':
                                return item
                    elif isinstance(data, dict) and data.get('@type') == 'Product':
                        return data
                        
                except json.JSONDecodeError:
                    continue
                    
        except Exception as e:
            logger.warning(f"Failed to extract JSON-LD: {e}")
            
        return None

    def _parse_json_ld_product(self, json_ld: Dict, url: str) -> Dict:
        """JSON-LD Product verisini parse et"""
        # Fiyat bilgisi
        price = None
        offers = json_ld.get('offers', {})
        if isinstance(offers, dict):
            price = offers.get('price')
        elif isinstance(offers, list) and offers:
            price = offers[0].get('price')
            
        # Stok durumu
        in_stock = True
        if isinstance(offers, dict):
            availability = offers.get('availability', '')
            in_stock = 'instock' in availability.lower() or 'available' in availability.lower()
        elif isinstance(offers, list) and offers:
            availability = offers[0].get('availability', '')
            in_stock = 'instock' in availability.lower() or 'available' in availability.lower()
            
        # Görsel
        image = None
        images = json_ld.get('image', [])
        if isinstance(images, list) and images:
            image = images[0] if isinstance(images[0], str) else images[0].get('url')
        elif isinstance(images, str):
            image = images
            
        return {
            'name': json_ld.get('name', ''),
            'url': url,
            'price': float(price) if price else None,
            'inStock': in_stock,
            'sku': json_ld.get('sku') or json_ld.get('mpn'),
            'image': image,
            'brand': json_ld.get('brand', {}).get('name') if isinstance(json_ld.get('brand'), dict) else json_ld.get('brand'),
            'description': json_ld.get('description', '')[:200] if json_ld.get('description') else ''
        }

    def _parse_html_product(self, html: str, url: str) -> Optional[Dict]:
        """HTML'den manuel olarak ürün bilgilerini çıkar"""
        try:
            # Ürün başlığı
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
            name = title_match.group(1).strip() if title_match else ''
            
            # Fiyat bilgisi (WooCommerce format)
            price_patterns = [
                r'<span[^>]*class="[^"]*price[^"]*"[^>]*>([^<]+)</span>',
                r'<span[^>]*class="[^"]*amount[^"]*"[^>]*>([^<]+)</span>',
                r'<div[^>]*class="[^"]*price[^"]*"[^>]*>([^<]+)</div>'
            ]
            
            price = None
            for pattern in price_patterns:
                price_match = re.search(pattern, html, re.IGNORECASE)
                if price_match:
                    price_text = price_match.group(1).strip()
                    # Sayısal değeri çıkar
                    price_numbers = re.findall(r'[\d,]+\.?\d*', price_text)
                    if price_numbers:
                        try:
                            price = float(price_numbers[0].replace(',', ''))
                            break
                        except ValueError:
                            continue
            
            # Stok durumu
            in_stock = True
            stock_patterns = [
                r'class="[^"]*out-of-stock[^"]*"',
                r'class="[^"]*unavailable[^"]*"',
                r'out of stock',
                r'unavailable'
            ]
            
            for pattern in stock_patterns:
                if re.search(pattern, html, re.IGNORECASE):
                    in_stock = False
                    break
            
            # Görsel
            image = None
            img_patterns = [
                r'<img[^>]*class="[^"]*wp-post-image[^"]*"[^>]*src="([^"]*)"',
                r'<img[^>]*class="[^"]*product-image[^"]*"[^>]*src="([^"]*)"',
                r'<img[^>]*class="[^"]*attachment-[^"]*"[^>]*src="([^"]*)"'
            ]
            
            for pattern in img_patterns:
                img_match = re.search(pattern, html, re.IGNORECASE)
                if img_match:
                    image = img_match.group(1)
                    break
            
            return {
                'name': name,
                'url': url,
                'price': price,
                'inStock': in_stock,
                'sku': None,
                'image': image,
                'brand': None,
                'description': ''
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse HTML product: {e}")
            return None

    def search_vendor(self, domain: str, query: str, canonical_specs: Optional[Dict] = None) -> List[Dict]:
        """
        Belirli bir WooCommerce tedarikçisinde arama yap
        
        Args:
            domain: Tedarikçi domain
            query: Arama terimi
            canonical_specs: Canonical parça özellikleri (opsiyonel)
            
        Returns:
            Eşleşen ürünler listesi
        """
        results = []
        
        # 1. Store API dene
        try:
            store_results = self.search_store_api(domain, query, per_page=10)
            results.extend(store_results)
        except Exception as e:
            logger.warning(f"Store API failed for {domain}: {e}")
        
        # 2. WC v3 API dene
        if not results:
            try:
                v3_results = self.search_wc_v3_api(domain, query, per_page=10)
                results.extend(v3_results)
            except Exception as e:
                logger.warning(f"WC v3 API failed for {domain}: {e}")
        
        # 3. Products endpoint dene
        if not results:
            try:
                page_results = self.search_products_endpoint(domain, query)
                results.extend(page_results)
            except Exception as e:
                logger.warning(f"Products endpoint failed for {domain}: {e}")
        
        # Canonical specs varsa filtrele
        if canonical_specs and canonical_specs.get('must_keywords'):
            filtered_results = []
            for product in results:
                if self._is_product_match(canonical_specs, product):
                    filtered_results.append(product)
            results = filtered_results
        
        return results

    def _is_product_match(self, canonical_specs: Dict, product: Dict) -> bool:
        """Ürünün canonical özelliklerle eşleşip eşleşmediğini kontrol et"""
        if not canonical_specs.get('must_keywords'):
            return True
            
        # Tüm metin içeriğini birleştir
        text_content = ' '.join([
            product.get('name', ''),
            product.get('description', ''),
            product.get('sku', '') or '',
        ]).lower()
        
        # Zorunlu anahtar kelimeleri kontrol et
        must_keywords = [kw.lower() for kw in canonical_specs['must_keywords']]
        return all(keyword in text_content for keyword in must_keywords)

    def search_all_vendors(self, query: str, canonical_specs: Optional[Dict] = None) -> Dict[str, List[Dict]]:
        """
        Tüm WooCommerce tedarikçilerinde arama yap
        
        Args:
            query: Arama terimi
            canonical_specs: Canonical parça özellikleri
            
        Returns:
            Tedarikçi bazında sonuçlar
        """
        all_results = {}
        
        for domain, vendor_info in self.woocommerce_vendors.items():
            try:
                logger.info(f"Searching {vendor_info['name']} ({domain}) for: {query}")
                results = self.search_vendor(domain, query, canonical_specs)
                all_results[vendor_info['name']] = results
                logger.info(f"Found {len(results)} products from {vendor_info['name']}")
            except Exception as e:
                logger.error(f"Error searching {domain}: {e}")
                all_results[vendor_info['name']] = []
                
        return all_results


# Test ve örnek kullanım
if __name__ == "__main__":
    # Test arama
    engine = WooCommerceSearchEngine()
    
    # Canonical parça özellikleri örneği
    canonical_specs = {
        'must_keywords': ['VEX', 'motor']
    }
    
    # Arama yap
    results = engine.search_all_vendors("VEX motor", canonical_specs)
    
    # Sonuçları yazdır
    for vendor, products in results.items():
        print(f"\n{vendor}:")
        for product in products:
            print(f"  - {product['name']}: ${product['price']} ({product['url']})")
