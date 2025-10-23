"""
Shopify tabanlı FRC tedarikçileri için arama sistemi
REV, WCP, ThriftyBot gibi Shopify kullanan tedarikçiler için optimize edilmiş
"""

import requests
import re
import json
import time
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional, Tuple
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShopifySearchEngine:
    def __init__(self, rate_limit_delay: float = 0.5):
        """
        Shopify arama motoru
        
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
        
        # FRC tedarikçileri - Shopify kullananlar (gerçek siteler)
        self.shopify_vendors = {
            'www.revrobotics.com': {
                'name': 'REV Robotics',
                'search_endpoints': [
                    '/search/suggest.json',
                    '/products.json'
                ],
                'base_url': 'https://www.revrobotics.com'
            },
            'wcproducts.com': {
                'name': 'WCP (West Coast Products)',
                'search_endpoints': [
                    '/search/suggest.json',
                    '/products.json'
                ],
                'base_url': 'https://wcproducts.com'
            }
        }

    def _rate_limit(self, domain: str):
        """Domain başına rate limiting"""
        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time[domain] = time.time()

    def _make_request(self, url: str, timeout: int = 10) -> Optional[requests.Response]:
        """Rate-limited HTTP request"""
        try:
            domain = urlparse(url).netloc
            self._rate_limit(domain)
            
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            return response
        except Exception as e:
            logger.warning(f"Request failed for {url}: {e}")
            return None

    def search_suggest(self, domain: str, query: str, limit: int = 10) -> List[str]:
        """
        Shopify search/suggest.json API kullanarak ürün URL'leri bul
        
        Args:
            domain: Tedarikçi domain (örn: 'revrobotics.com')
            query: Arama terimi
            limit: Maksimum sonuç sayısı
            
        Returns:
            Ürün URL'leri listesi
        """
        if not domain.startswith('http'):
            domain = f"https://{domain}"
            
        url = f"{domain}/search/suggest.json"
        params = {
            'q': query,
            'resources[type]': 'product',
            'resources[limit]': limit
        }
        
        response = self._make_request(url, params=params)
        if not response:
            return []
            
        try:
            data = response.json()
            products = data.get('resources', {}).get('results', {}).get('products', [])
            return [urljoin(domain, product.get('url', '')) for product in products if product.get('url')]
        except Exception as e:
            logger.warning(f"Failed to parse search suggest for {domain}: {e}")
            return []

    def get_products_json(self, domain: str, page: int = 1, limit: int = 50) -> List[Dict]:
        """
        Shopify products.json API kullanarak ürün listesi al
        
        Args:
            domain: Tedarikçi domain
            page: Sayfa numarası
            limit: Sayfa başına ürün sayısı
            
        Returns:
            Ürün bilgileri listesi
        """
        if not domain.startswith('http'):
            domain = f"https://{domain}"
            
        url = f"{domain}/products.json"
        params = {'page': page, 'limit': limit}
        
        response = self._make_request(url, params=params)
        if not response:
            return []
            
        try:
            data = response.json()
            return data.get('products', [])
        except Exception as e:
            logger.warning(f"Failed to parse products.json for {domain}: {e}")
            return []

    def get_sitemap_products(self, domain: str) -> List[str]:
        """
        Sitemap.xml'den ürün URL'lerini çıkar
        
        Args:
            domain: Tedarikçi domain
            
        Returns:
            Ürün URL'leri listesi
        """
        if not domain.startswith('http'):
            domain = f"https://{domain}"
            
        sitemap_url = f"{domain}/sitemap.xml"
        response = self._make_request(sitemap_url)
        if not response:
            return []
            
        try:
            # Sitemap XML parsing (basit regex yaklaşımı)
            content = response.text
            product_urls = re.findall(r'<loc>(https?://[^<]+/products/[^<]+)</loc>', content)
            return product_urls
        except Exception as e:
            logger.warning(f"Failed to parse sitemap for {domain}: {e}")
            return []

    def extract_json_ld(self, html: str) -> Optional[Dict]:
        """
        HTML'den JSON-LD Product verilerini çıkar
        
        Args:
            html: HTML içeriği
            
        Returns:
            JSON-LD Product verisi veya None
        """
        try:
            # JSON-LD script tag'lerini bul
            pattern = r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>'
            matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                try:
                    data = json.loads(match.strip())
                    
                    # Tek obje veya liste olabilir
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

    def is_product_match(self, canonical_specs: Dict, json_ld: Dict, html: str) -> bool:
        """
        Ürünün canonical özelliklerle eşleşip eşleşmediğini kontrol et
        
        Args:
            canonical_specs: Canonical parça özellikleri
            json_ld: JSON-LD Product verisi
            html: HTML içeriği
            
        Returns:
            Eşleşme durumu
        """
        if not canonical_specs.get('must_keywords'):
            return True
            
        # Tüm metin içeriğini birleştir
        text_content = ' '.join([
            json_ld.get('name', ''),
            json_ld.get('description', ''),
            json_ld.get('sku', ''),
            json_ld.get('mpn', ''),
            html
        ]).lower()
        
        # Zorunlu anahtar kelimeleri kontrol et
        must_keywords = [kw.lower() for kw in canonical_specs['must_keywords']]
        return all(keyword in text_content for keyword in must_keywords)

    def search_vendor(self, domain: str, query: str, canonical_specs: Optional[Dict] = None) -> List[Dict]:
        """
        Belirli bir tedarikçide arama yap
        
        Args:
            domain: Tedarikçi domain
            query: Arama terimi
            canonical_specs: Canonical parça özellikleri (opsiyonel)
            
        Returns:
            Eşleşen ürünler listesi
        """
        results = []
        
        # 1. Search suggest API
        product_urls = self.search_suggest(domain, query, limit=10)
        
        # 2. Products.json API (backup)
        if not product_urls:
            products_data = self.get_products_json(domain, page=1, limit=20)
            product_urls = [urljoin(f"https://{domain}", p.get('handle', '')) 
                          for p in products_data if p.get('handle')]
        
        # 3. Her ürün sayfasını kontrol et
        for url in product_urls[:15]:  # Limit to 15 products
            try:
                response = self._make_request(url)
                if not response or response.status_code != 200:
                    continue
                    
                html = response.text
                json_ld = self.extract_json_ld(html)
                
                # Canonical specs varsa eşleşme kontrolü
                if canonical_specs and not self.is_product_match(canonical_specs, json_ld or {}, html):
                    continue
                
                # Ürün bilgilerini çıkar
                product_info = self._extract_product_info(json_ld, html, url)
                if product_info:
                    results.append(product_info)
                    
            except Exception as e:
                logger.warning(f"Failed to process product {url}: {e}")
                continue
                
        return results

    def _extract_product_info(self, json_ld: Optional[Dict], html: str, url: str) -> Optional[Dict]:
        """
        JSON-LD ve HTML'den ürün bilgilerini çıkar
        
        Args:
            json_ld: JSON-LD Product verisi
            html: HTML içeriği
            url: Ürün URL'i
            
        Returns:
            Ürün bilgileri dict'i
        """
        if not json_ld:
            return None
            
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

    def search_all_vendors(self, query: str, canonical_specs: Optional[Dict] = None) -> Dict[str, List[Dict]]:
        """
        Tüm Shopify tedarikçilerinde arama yap
        
        Args:
            query: Arama terimi
            canonical_specs: Canonical parça özellikleri
            
        Returns:
            Tedarikçi bazında sonuçlar
        """
        all_results = {}
        
        for domain, vendor_info in self.shopify_vendors.items():
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
    engine = ShopifySearchEngine()
    
    # Canonical parça özellikleri örneği
    canonical_specs = {
        'must_keywords': ['NEO', 'brushless', 'motor']
    }
    
    # Arama yap
    results = engine.search_all_vendors("NEO brushless motor", canonical_specs)
    
    # Sonuçları yazdır
    for vendor, products in results.items():
        print(f"\n{vendor}:")
        for product in products:
            print(f"  - {product['name']}: ${product['price']} ({product['url']})")
