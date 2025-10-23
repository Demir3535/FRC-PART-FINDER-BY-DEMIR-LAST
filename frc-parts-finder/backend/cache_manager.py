"""
URL→fiyat/stok/img önbellek sistemi
24-48 saat TTL ile akıllı önbellek yönetimi
"""

import json
import time
import hashlib
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, cache_dir: str = "cache", default_ttl: int = 24 * 3600):
        """
        Önbellek yöneticisi
        
        Args:
            cache_dir: Önbellek dosyalarının saklanacağı dizin
            default_ttl: Varsayılan TTL (saniye) - 24 saat
        """
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        
        # Önbellek dizinini oluştur
        os.makedirs(cache_dir, exist_ok=True)
        
        # Önbellek dosya yolları
        self.url_cache_file = os.path.join(cache_dir, "url_cache.json")
        self.search_cache_file = os.path.join(cache_dir, "search_cache.json")
        self.product_cache_file = os.path.join(cache_dir, "product_cache.json")
        
        # Önbellek verilerini yükle
        self.url_cache = self._load_cache(self.url_cache_file)
        self.search_cache = self._load_cache(self.search_cache_file)
        self.product_cache = self._load_cache(self.product_cache_file)

    def _load_cache(self, file_path: str) -> Dict:
        """Önbellek dosyasını yükle"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache from {file_path}: {e}")
        return {}

    def _save_cache(self, file_path: str, cache_data: Dict):
        """Önbellek dosyasını kaydet"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Failed to save cache to {file_path}: {e}")

    def _generate_key(self, *args) -> str:
        """Önbellek anahtarı oluştur"""
        key_string = "|".join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _is_expired(self, timestamp: float, ttl: int) -> bool:
        """Önbellek kaydının süresi dolmuş mu kontrol et"""
        return time.time() - timestamp > ttl

    def _clean_expired_entries(self, cache_data: Dict, ttl: int = None) -> Dict:
        """Süresi dolmuş kayıtları temizle"""
        if ttl is None:
            ttl = self.default_ttl
            
        current_time = time.time()
        cleaned_cache = {}
        
        for key, value in cache_data.items():
            if isinstance(value, dict) and 'timestamp' in value:
                if current_time - value['timestamp'] <= ttl:
                    cleaned_cache[key] = value
            else:
                # Eski format - timestamp yoksa varsayılan TTL uygula
                cleaned_cache[key] = value
                
        return cleaned_cache

    def get_url_status(self, url: str) -> Optional[Dict]:
        """
        URL durumunu önbellekten al
        
        Args:
            url: Kontrol edilecek URL
            
        Returns:
            URL durumu bilgisi veya None
        """
        key = self._generate_key("url", url)
        entry = self.url_cache.get(key)
        
        if entry and not self._is_expired(entry.get('timestamp', 0), self.default_ttl):
            return entry.get('data')
        
        return None

    def set_url_status(self, url: str, status: Dict, ttl: int = None):
        """
        URL durumunu önbelleğe kaydet
        
        Args:
            url: URL
            status: Durum bilgisi
            ttl: TTL (saniye)
        """
        if ttl is None:
            ttl = self.default_ttl
            
        key = self._generate_key("url", url)
        self.url_cache[key] = {
            'data': status,
            'timestamp': time.time(),
            'ttl': ttl
        }
        
        # Süresi dolmuş kayıtları temizle
        self.url_cache = self._clean_expired_entries(self.url_cache, ttl)
        
        # Önbelleği kaydet
        self._save_cache(self.url_cache_file, self.url_cache)

    def get_search_results(self, query: str, vendor: str = None) -> Optional[List[Dict]]:
        """
        Arama sonuçlarını önbellekten al
        
        Args:
            query: Arama terimi
            vendor: Tedarikçi (opsiyonel)
            
        Returns:
            Arama sonuçları veya None
        """
        key = self._generate_key("search", query, vendor or "all")
        entry = self.search_cache.get(key)
        
        if entry and not self._is_expired(entry.get('timestamp', 0), self.default_ttl):
            return entry.get('data')
        
        return None

    def set_search_results(self, query: str, results: List[Dict], vendor: str = None, ttl: int = None):
        """
        Arama sonuçlarını önbelleğe kaydet
        
        Args:
            query: Arama terimi
            results: Arama sonuçları
            vendor: Tedarikçi (opsiyonel)
            ttl: TTL (saniye)
        """
        if ttl is None:
            ttl = self.default_ttl
            
        key = self._generate_key("search", query, vendor or "all")
        self.search_cache[key] = {
            'data': results,
            'timestamp': time.time(),
            'ttl': ttl
        }
        
        # Süresi dolmuş kayıtları temizle
        self.search_cache = self._clean_expired_entries(self.search_cache, ttl)
        
        # Önbelleği kaydet
        self._save_cache(self.search_cache_file, self.search_cache)

    def get_product_info(self, url: str) -> Optional[Dict]:
        """
        Ürün bilgilerini önbellekten al
        
        Args:
            url: Ürün URL'i
            
        Returns:
            Ürün bilgileri veya None
        """
        key = self._generate_key("product", url)
        entry = self.product_cache.get(key)
        
        if entry and not self._is_expired(entry.get('timestamp', 0), self.default_ttl):
            return entry.get('data')
        
        return None

    def set_product_info(self, url: str, product_info: Dict, ttl: int = None):
        """
        Ürün bilgilerini önbelleğe kaydet
        
        Args:
            url: Ürün URL'i
            product_info: Ürün bilgileri
            ttl: TTL (saniye)
        """
        if ttl is None:
            ttl = self.default_ttl
            
        key = self._generate_key("product", url)
        self.product_cache[key] = {
            'data': product_info,
            'timestamp': time.time(),
            'ttl': ttl
        }
        
        # Süresi dolmuş kayıtları temizle
        self.product_cache = self._clean_expired_entries(self.product_cache, ttl)
        
        # Önbelleği kaydet
        self._save_cache(self.product_cache_file, self.product_cache)

    def get_cached_price(self, url: str) -> Optional[float]:
        """Önbellekten fiyat bilgisini al"""
        product_info = self.get_product_info(url)
        if product_info:
            return product_info.get('price')
        return None

    def get_cached_stock(self, url: str) -> Optional[bool]:
        """Önbellekten stok durumunu al"""
        product_info = self.get_product_info(url)
        if product_info:
            return product_info.get('inStock')
        return None

    def get_cached_image(self, url: str) -> Optional[str]:
        """Önbellekten görsel URL'ini al"""
        product_info = self.get_product_info(url)
        if product_info:
            return product_info.get('image')
        return None

    def invalidate_url(self, url: str):
        """Belirli URL'nin önbelleğini temizle"""
        key = self._generate_key("url", url)
        if key in self.url_cache:
            del self.url_cache[key]
            self._save_cache(self.url_cache_file, self.url_cache)

    def invalidate_product(self, url: str):
        """Belirli ürünün önbelleğini temizle"""
        key = self._generate_key("product", url)
        if key in self.product_cache:
            del self.product_cache[key]
            self._save_cache(self.product_cache_file, self.product_cache)

    def invalidate_search(self, query: str, vendor: str = None):
        """Belirli arama sonuçlarının önbelleğini temizle"""
        key = self._generate_key("search", query, vendor or "all")
        if key in self.search_cache:
            del self.search_cache[key]
            self._save_cache(self.search_cache_file, self.search_cache)

    def clear_all_cache(self):
        """Tüm önbelleği temizle"""
        self.url_cache = {}
        self.search_cache = {}
        self.product_cache = {}
        
        self._save_cache(self.url_cache_file, self.url_cache)
        self._save_cache(self.search_cache_file, self.search_cache)
        self._save_cache(self.product_cache_file, self.product_cache)

    def get_cache_stats(self) -> Dict:
        """Önbellek istatistiklerini al"""
        current_time = time.time()
        
        def count_valid_entries(cache_data: Dict, ttl: int) -> int:
            count = 0
            for entry in cache_data.values():
                if isinstance(entry, dict) and 'timestamp' in entry:
                    if current_time - entry['timestamp'] <= ttl:
                        count += 1
                else:
                    count += 1
            return count
        
        return {
            'url_cache_entries': count_valid_entries(self.url_cache, self.default_ttl),
            'search_cache_entries': count_valid_entries(self.search_cache, self.default_ttl),
            'product_cache_entries': count_valid_entries(self.product_cache, self.default_ttl),
            'total_entries': (
                count_valid_entries(self.url_cache, self.default_ttl) +
                count_valid_entries(self.search_cache, self.default_ttl) +
                count_valid_entries(self.product_cache, self.default_ttl)
            ),
            'cache_dir': self.cache_dir,
            'default_ttl_hours': self.default_ttl / 3600
        }

    def cleanup_expired(self):
        """Süresi dolmuş tüm kayıtları temizle"""
        self.url_cache = self._clean_expired_entries(self.url_cache)
        self.search_cache = self._clean_expired_entries(self.search_cache)
        self.product_cache = self._clean_expired_entries(self.product_cache)
        
        self._save_cache(self.url_cache_file, self.url_cache)
        self._save_cache(self.search_cache_file, self.search_cache)
        self._save_cache(self.product_cache_file, self.product_cache)

    def set_custom_ttl(self, url: str, ttl_hours: int):
        """
        Belirli URL için özel TTL ayarla
        
        Args:
            url: URL
            ttl_hours: TTL (saat)
        """
        ttl_seconds = ttl_hours * 3600
        
        # URL cache'de varsa güncelle
        key = self._generate_key("url", url)
        if key in self.url_cache:
            self.url_cache[key]['ttl'] = ttl_seconds
        
        # Product cache'de varsa güncelle
        product_key = self._generate_key("product", url)
        if product_key in self.product_cache:
            self.product_cache[product_key]['ttl'] = ttl_seconds
        
        # Önbellekleri kaydet
        self._save_cache(self.url_cache_file, self.url_cache)
        self._save_cache(self.product_cache_file, self.product_cache)


# Test ve örnek kullanım
if __name__ == "__main__":
    cache = CacheManager()
    
    # Test verileri
    test_url = "https://example.com/product"
    test_product = {
        'name': 'Test Product',
        'price': 29.99,
        'inStock': True,
        'image': 'https://example.com/image.jpg'
    }
    
    # Ürün bilgilerini kaydet
    cache.set_product_info(test_url, test_product, ttl=3600)  # 1 saat
    
    # Ürün bilgilerini al
    cached_product = cache.get_product_info(test_url)
    print(f"Cached product: {cached_product}")
    
    # Fiyat bilgisini al
    price = cache.get_cached_price(test_url)
    print(f"Cached price: {price}")
    
    # Önbellek istatistikleri
    stats = cache.get_cache_stats()
    print(f"Cache stats: {stats}")
