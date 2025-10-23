"""
Gerçek FRC tedarikçi siteleri için özelleştirilmiş arama sistemi
WCP, REV, AndyMark, CTRE siteleri için optimize edilmiş
"""

import requests
import re
import json
import time
from urllib.parse import urljoin, urlparse, quote
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class RealVendorSearchEngine:
    def __init__(self, rate_limit_delay: float = 1.0):
        """
        Gerçek FRC tedarikçi arama motoru
        
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
        
        # Gerçek FRC tedarikçi siteleri
        self.vendors = {
            'wcproducts.com': {
                'name': 'WCP (West Coast Products)',
                'base_url': 'https://wcproducts.com',
                'search_url': 'https://wcproducts.com/search',
                'type': 'shopify',
                'search_params': {'q': '{query}'}
            },
            'www.revrobotics.com': {
                'name': 'REV Robotics',
                'base_url': 'https://www.revrobotics.com',
                'search_url': 'https://www.revrobotics.com/search',
                'type': 'shopify',
                'search_params': {'q': '{query}'}
            },
            'andymark.com': {
                'name': 'AndyMark',
                'base_url': 'https://andymark.com',
                'search_url': 'https://andymark.com/search',
                'type': 'woocommerce',
                'search_params': {'q': '{query}'}
            },
            'store.ctr-electronics.com': {
                'name': 'CTRE (Cross The Road Electronics)',
                'base_url': 'https://store.ctr-electronics.com',
                'search_url': 'https://store.ctr-electronics.com',
                'type': 'woocommerce',
                'search_params': {'s': '{query}'}
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

    def search_wcp(self, query: str) -> List[Dict]:
        """WCP (West Coast Products) arama"""
        try:
            # Öncelik: Shopify suggest API (deterministik JSON)
            suggest_url = "https://wcproducts.com/search/suggest.json"
            response = self._make_request(suggest_url, params={
                "q": query,
                "resources[type]": "product",
                "resources[limit]": 10
            })
            product_urls: List[str] = []
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    prods = data.get("resources", {}).get("results", {}).get("products", [])
                    product_urls = [urljoin("https://wcproducts.com", p.get("url", "")) for p in prods if p.get("url")]
                except Exception:
                    product_urls = []

            # Yedek: HTML search sayfasından link çıkarımı
            if not product_urls:
                search_url = f"https://wcproducts.com/search?q={quote(query)}"
                response = self._make_request(search_url)
                if not response:
                    return []
                html = response.text
                links = re.findall(r'href=\"(\/products\/[^\"]+)\"', html)
                product_urls = [urljoin('https://wcproducts.com', u) for u in links]
            
            results = []
            for full_url in product_urls[:10]:  # İlk 10 ürün
                product_info = self._extract_wcp_product(full_url)
                if product_info:
                    results.append(product_info)
            
            return results
            
        except Exception as e:
            logger.error(f"WCP search failed: {e}")
            return []

    def search_rev(self, query: str) -> List[Dict]:
        """REV Robotics arama"""
        try:
            # REV: search sayfası 404 verebilir; sitemap.xml deterministik
            sitemap_url = "https://www.revrobotics.com/sitemap.xml"
            response = self._make_request(sitemap_url)
            if not response:
                return []
            sm = response.text
            # Ürün URL'leri genelde /rev-xx-xxxx/ şeklinde
            urls = re.findall(r"<loc>(https:\/\/www\.revrobotics\.com\/[a-z0-9\-]+\/)<\/loc>", sm, re.IGNORECASE)
            # Sorgu kelimelerini URL'de arayalım (basit filtre)
            tokens = [t for t in re.split(r"\s+", query.strip()) if t]
            def token_match(u: str) -> bool:
                ul = u.lower()
                return all(t.lower() in ul for t in tokens)
            candidate_urls = [u for u in urls if token_match(u)]
            candidate_urls = candidate_urls[:12]
            
            results = []
            for full_url in candidate_urls:
                product_info = self._extract_rev_product(full_url)
                if product_info:
                    results.append(product_info)
            
            return results
            
        except Exception as e:
            logger.error(f"REV search failed: {e}")
            return []

    def search_andymark(self, query: str) -> List[Dict]:
        """AndyMark arama"""
        try:
            # AndyMark WooCommerce arama
            search_url = f"https://andymark.com/search?q={quote(query)}"
            response = self._make_request(search_url)
            
            if not response:
                return []
            
            # HTML'den ürün linklerini çıkar (absolute/relative)
            html = response.text
            product_links = re.findall(r'href=\"(https?:\/\/andymark\.com[^\"]*|\/products\/[^\"]*)\"', html)
            
            results = []
            for link in product_links[:10]:  # İlk 10 ürün
                full_url = urljoin('https://andymark.com', link)
                product_info = self._extract_andymark_product(full_url)
                if product_info:
                    results.append(product_info)
            
            return results
            
        except Exception as e:
            logger.error(f"AndyMark search failed: {e}")
            return []

    def search_ctre(self, query: str) -> List[Dict]:
        """CTRE arama"""
        try:
            # CTRE WooCommerce arama
            search_url = f"https://store.ctr-electronics.com/?s={quote(query)}"
            response = self._make_request(search_url)
            
            if not response:
                return []
            
            # HTML'den ürün linklerini çıkar (absolute/relative)
            html = response.text
            product_links = re.findall(r'href=\"(https?:\/\/store\.ctr-electronics\.com[^\"]*|\/products\/[^\"]*)\"', html)
            
            results = []
            for link in product_links[:10]:  # İlk 10 ürün
                full_url = urljoin('https://store.ctr-electronics.com', link)
                product_info = self._extract_ctre_product(full_url)
                if product_info:
                    results.append(product_info)
            
            return results
            
        except Exception as e:
            logger.error(f"CTRE search failed: {e}")
            return []

    def _extract_wcp_product(self, url: str) -> Optional[Dict]:
        """WCP ürün sayfasından bilgileri çıkar"""
        try:
            response = self._make_request(url)
            if not response:
                return None
            
            html = response.text
            
            # JSON-LD Product verisi ara
            json_ld = self._extract_json_ld(html)
            if json_ld:
                return self._parse_json_ld_product(json_ld, url, 'WCP (West Coast Products)')
            
            # HTML'den manuel parsing
            return self._parse_html_product(html, url, 'WCP (West Coast Products)')
            
        except Exception as e:
            logger.warning(f"Failed to extract WCP product from {url}: {e}")
            return None

    def _extract_rev_product(self, url: str) -> Optional[Dict]:
        """REV ürün sayfasından bilgileri çıkar"""
        try:
            response = self._make_request(url)
            if not response:
                return None
            
            html = response.text
            
            # JSON-LD Product verisi ara
            json_ld = self._extract_json_ld(html)
            if json_ld:
                return self._parse_json_ld_product(json_ld, url, 'REV Robotics')
            
            # HTML'den manuel parsing
            return self._parse_html_product(html, url, 'REV Robotics')
            
        except Exception as e:
            logger.warning(f"Failed to extract REV product from {url}: {e}")
            return None

    def _extract_andymark_product(self, url: str) -> Optional[Dict]:
        """AndyMark ürün sayfasından bilgileri çıkar"""
        try:
            response = self._make_request(url)
            if not response:
                return None
            
            html = response.text
            
            # JSON-LD Product verisi ara
            json_ld = self._extract_json_ld(html)
            if json_ld:
                return self._parse_json_ld_product(json_ld, url, 'AndyMark')
            
            # HTML'den manuel parsing
            return self._parse_html_product(html, url, 'AndyMark')
            
        except Exception as e:
            logger.warning(f"Failed to extract AndyMark product from {url}: {e}")
            return None

    def _extract_ctre_product(self, url: str) -> Optional[Dict]:
        """CTRE ürün sayfasından bilgileri çıkar"""
        try:
            response = self._make_request(url)
            if not response:
                return None
            
            html = response.text
            
            # JSON-LD Product verisi ara
            json_ld = self._extract_json_ld(html)
            if json_ld:
                return self._parse_json_ld_product(json_ld, url, 'CTRE')
            
            # HTML'den manuel parsing
            return self._parse_html_product(html, url, 'CTRE')
            
        except Exception as e:
            logger.warning(f"Failed to extract CTRE product from {url}: {e}")
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

    def _parse_json_ld_product(self, json_ld: Dict, url: str, vendor: str) -> Dict:
        """JSON-LD Product verisini parse et"""
        # Fiyat bilgisi
        price = None
        offers = json_ld.get('offers', {})
        if isinstance(offers, dict):
            price = offers.get('price')
        elif isinstance(offers, list) and offers:
            price = offers[0].get('price')
        
        # Fiyatı normalize et
        if price:
            try:
                if isinstance(price, str):
                    price_clean = re.sub(r'[^\d.,]', '', price)
                    price = float(price_clean.replace(',', ''))
                else:
                    price = float(price)
            except (ValueError, TypeError):
                price = None
        
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
            'name': json_ld.get('name', '').strip(),
            'url': url,
            'price': price,
            'inStock': in_stock,
            'sku': json_ld.get('sku') or json_ld.get('mpn'),
            'image': image,
            'vendor': vendor,
            'description': json_ld.get('description', '')[:200] if json_ld.get('description') else '',
            'source': 'real_vendor'
        }

    def _parse_html_product(self, html: str, url: str, vendor: str) -> Optional[Dict]:
        """HTML'den manuel olarak ürün bilgilerini çıkar"""
        try:
            # Ürün başlığı
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
            name = title_match.group(1).strip() if title_match else ''
            
            # Fiyat bilgisi
            price_patterns = [
                r'<span[^>]*class="[^"]*price[^"]*"[^>]*>([^<]+)</span>',
                r'<span[^>]*class="[^"]*amount[^"]*"[^>]*>([^<]+)</span>',
                r'<div[^>]*class="[^"]*price[^"]*"[^>]*>([^<]+)</div>',
                r'<span[^>]*class="[^"]*money[^"]*"[^>]*>([^<]+)</span>'
            ]
            
            price = None
            for pattern in price_patterns:
                price_match = re.search(pattern, html, re.IGNORECASE)
                if price_match:
                    price_text = price_match.group(1).strip()
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
                r'unavailable',
                r'sold out'
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
                r'<img[^>]*class="[^"]*attachment-[^"]*"[^>]*src="([^"]*)"',
                r'<img[^>]*class="[^"]*product-photo[^"]*"[^>]*src="([^"]*)"'
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
                'vendor': vendor,
                'description': '',
                'source': 'real_vendor'
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse HTML product: {e}")
            return None

    def search_all_vendors(self, query: str) -> Dict[str, List[Dict]]:
        """
        Tüm gerçek FRC tedarikçilerinde arama yap
        
        Args:
            query: Arama terimi
            
        Returns:
            Tedarikçi bazında sonuçlar
        """
        all_results = {}
        
        # WCP arama
        try:
            logger.info(f"Searching WCP for: {query}")
            wcp_results = self.search_wcp(query)
            all_results['WCP (West Coast Products)'] = wcp_results
            logger.info(f"Found {len(wcp_results)} products from WCP")
        except Exception as e:
            logger.error(f"Error searching WCP: {e}")
            all_results['WCP (West Coast Products)'] = []
        
        # REV arama
        try:
            logger.info(f"Searching REV for: {query}")
            rev_results = self.search_rev(query)
            all_results['REV Robotics'] = rev_results
            logger.info(f"Found {len(rev_results)} products from REV")
        except Exception as e:
            logger.error(f"Error searching REV: {e}")
            all_results['REV Robotics'] = []
        
        # AndyMark arama
        try:
            logger.info(f"Searching AndyMark for: {query}")
            andymark_results = self.search_andymark(query)
            all_results['AndyMark'] = andymark_results
            logger.info(f"Found {len(andymark_results)} products from AndyMark")
        except Exception as e:
            logger.error(f"Error searching AndyMark: {e}")
            all_results['AndyMark'] = []
        
        # CTRE arama
        try:
            logger.info(f"Searching CTRE for: {query}")
            ctre_results = self.search_ctre(query)
            all_results['CTRE'] = ctre_results
            logger.info(f"Found {len(ctre_results)} products from CTRE")
        except Exception as e:
            logger.error(f"Error searching CTRE: {e}")
            all_results['CTRE'] = []
        
        return all_results


# Test ve örnek kullanım
if __name__ == "__main__":
    # Test arama
    engine = RealVendorSearchEngine()
    
    # Arama yap
    results = engine.search_all_vendors("NEO motor")
    
    # Sonuçları yazdır
    for vendor, products in results.items():
        print(f"\n{vendor}:")
        for product in products:
            print(f"  - {product['name']}: ${product['price']} ({product['url']})")
