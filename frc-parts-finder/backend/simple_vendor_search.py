"""
Basit ve etkili FRC tedarikçi arama sistemi
Gerçek ürün linklerini bulmak için sitemap ve HTML parsing
"""

import requests
import re
import json
import time
from urllib.parse import urljoin, urlparse, quote
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class SimpleVendorSearch:
    def __init__(self, rate_limit_delay: float = 1.0):
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = {}
        
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0 Safari/537.36'
            ),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

    def _rate_limit(self, domain: str):
        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time[domain] = time.time()

    def _make_request(self, url: str, timeout: int = 15) -> Optional[requests.Response]:
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

    def search_wcp(self, query: str) -> List[Dict]:
        """WCP - Sitemap tabanlı arama"""
        try:
            # WCP sitemap'ini çek
            sitemap_url = "https://wcproducts.com/sitemap.xml"
            response = self._make_request(sitemap_url)
            if not response:
                return []
            
            # Sitemap'ten ürün URL'lerini çıkar
            content = response.text
            product_urls = re.findall(r'<loc>(https://wcproducts\.com/products/[^<]+)</loc>', content)
            
            # Query ile eşleşen URL'leri filtrele
            query_words = [w.lower() for w in query.split()]
            matching_urls = []
            
            for url in product_urls:
                # URL'de query kelimelerini ara
                url_lower = url.lower()
                if any(word in url_lower for word in query_words):
                    matching_urls.append(url)
            
            # İlk 10 eşleşen ürünü işle
            results = []
            for url in matching_urls[:10]:
                product_info = self._extract_product_info(url, 'WCP (West Coast Products)')
                if product_info:
                    results.append(product_info)
            
            return results
            
        except Exception as e:
            logger.error(f"WCP search failed: {e}")
            return []

    def search_rev(self, query: str) -> List[Dict]:
        """REV - Bilinen ürün URL'leri"""
        try:
            # REV'de bilinen ürün URL'leri
            known_products = {
                'neo': [
                    'https://www.revrobotics.com/rev-21-1650/',
                    'https://www.revrobotics.com/rev-21-1651/'
                ],
                'spark': [
                    'https://www.revrobotics.com/rev-11-2158/',
                    'https://www.revrobotics.com/rev-11-2159/'
                ],
                'motor': [
                    'https://www.revrobotics.com/rev-21-1650/',
                    'https://www.revrobotics.com/rev-21-1651/',
                    'https://www.revrobotics.com/rev-21-1652/'
                ],
                'controller': [
                    'https://www.revrobotics.com/rev-11-2158/',
                    'https://www.revrobotics.com/rev-11-2159/'
                ]
            }
            
            query_lower = query.lower()
            matching_urls = []
            
            for keyword, urls in known_products.items():
                if keyword in query_lower:
                    matching_urls.extend(urls)
            
            # Eşleşen URL'leri işle
            results = []
            for url in matching_urls[:8]:
                product_info = self._extract_product_info(url, 'REV Robotics')
                if product_info:
                    results.append(product_info)
            
            return results
            
        except Exception as e:
            logger.error(f"REV search failed: {e}")
            return []

    def search_andymark(self, query: str) -> List[Dict]:
        """AndyMark - HTML arama sayfası"""
        try:
            # AndyMark arama sayfası
            search_url = f"https://andymark.com/search?q={quote(query)}"
            response = self._make_request(search_url)
            if not response:
                return []
            
            html = response.text
            
            # Ürün linklerini çıkar (daha geniş pattern)
            product_links = re.findall(r'href="([^"]*(?:products|product)/[^"]*)"', html, re.IGNORECASE)
            
            # Absolute URL'leri de ara
            absolute_links = re.findall(r'href="(https://andymark\.com/[^"]*)"', html)
            
            all_links = product_links + absolute_links
            
            results = []
            for link in all_links[:10]:
                if link.startswith('http'):
                    full_url = link
                else:
                    full_url = urljoin('https://andymark.com', link)
                
                product_info = self._extract_product_info(full_url, 'AndyMark')
                if product_info:
                    results.append(product_info)
            
            return results
            
        except Exception as e:
            logger.error(f"AndyMark search failed: {e}")
            return []

    def search_ctre(self, query: str) -> List[Dict]:
        """CTRE - Bilinen ürün URL'leri"""
        try:
            # CTRE'de bilinen ürün URL'leri
            known_products = {
                'talon': [
                    'https://store.ctr-electronics.com/products/talon-srx',
                    'https://store.ctr-electronics.com/products/talon-fx'
                ],
                'victor': [
                    'https://store.ctr-electronics.com/products/victor-spx',
                    'https://store.ctr-electronics.com/products/victor-sp'
                ],
                'cancoder': [
                    'https://store.ctr-electronics.com/products/cancoder'
                ],
                'pigeon': [
                    'https://store.ctr-electronics.com/products/pigeon-2-0'
                ]
            }
            
            query_lower = query.lower()
            matching_urls = []
            
            for keyword, urls in known_products.items():
                if keyword in query_lower:
                    matching_urls.extend(urls)
            
            # Eşleşen URL'leri işle
            results = []
            for url in matching_urls[:8]:
                product_info = self._extract_product_info(url, 'CTRE')
                if product_info:
                    results.append(product_info)
            
            return results
            
        except Exception as e:
            logger.error(f"CTRE search failed: {e}")
            return []

    def _extract_product_info(self, url: str, vendor: str) -> Optional[Dict]:
        """Ürün sayfasından bilgileri çıkar"""
        try:
            response = self._make_request(url)
            if not response:
                return None
            
            html = response.text
            
            # JSON-LD Product verisi ara
            json_ld = self._extract_json_ld(html)
            if json_ld:
                return self._parse_json_ld_product(json_ld, url, vendor)
            
            # HTML'den manuel parsing
            return self._parse_html_product(html, url, vendor)
            
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
            
            # Fiyat bilgisi (daha geniş pattern)
            price_patterns = [
                r'<span[^>]*class="[^"]*price[^"]*"[^>]*>([^<]+)</span>',
                r'<span[^>]*class="[^"]*amount[^"]*"[^>]*>([^<]+)</span>',
                r'<div[^>]*class="[^"]*price[^"]*"[^>]*>([^<]+)</div>',
                r'<span[^>]*class="[^"]*money[^"]*"[^>]*>([^<]+)</span>',
                r'\$[\d,]+\.?\d*',  # Basit $ fiyat pattern
                r'USD\s*[\d,]+\.?\d*'  # USD fiyat pattern
            ]
            
            price = None
            for pattern in price_patterns:
                price_match = re.search(pattern, html, re.IGNORECASE)
                if price_match:
                    price_text = price_match.group(1) if price_match.groups() else price_match.group(0)
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
                r'sold out',
                r'not available'
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
                r'<img[^>]*class="[^"]*product-photo[^"]*"[^>]*src="([^"]*)"',
                r'<img[^>]*src="([^"]*)"[^>]*class="[^"]*product[^"]*"'
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
        """Tüm tedarikçilerde arama yap"""
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


# Test
if __name__ == "__main__":
    engine = SimpleVendorSearch()
    
    # Test arama
    results = engine.search_all_vendors("NEO motor")
    
    # Sonuçları yazdır
    for vendor, products in results.items():
        print(f"\n{vendor}:")
        for product in products:
            print(f"  - {product['name']}: ${product['price']} ({product['url']})")
