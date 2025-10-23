"""
JSON-LD Product doğrulama sistemi
FRC parçaları için özelleştirilmiş doğrulama ve eşleşme algoritmaları
"""

import re
import json
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class JSONLDValidator:
    def __init__(self):
        """JSON-LD Product doğrulama sistemi"""
        
        # FRC parça kategorileri ve özellikleri
        self.frc_categories = {
            'motors': {
                'keywords': ['motor', 'brushless', 'brushed', 'servo', 'actuator'],
                'brands': ['REV', 'CTRE', 'VEX', 'AndyMark', 'Kraken', 'Falcon', 'NEO'],
                'specs': ['rpm', 'torque', 'voltage', 'current', 'encoder']
            },
            'controllers': {
                'keywords': ['controller', 'esc', 'pwm', 'can', 'spark', 'talon', 'victor'],
                'brands': ['REV', 'CTRE', 'VEX', 'AndyMark'],
                'specs': ['voltage', 'current', 'pwm', 'can', 'encoder']
            },
            'sensors': {
                'keywords': ['sensor', 'encoder', 'gyro', 'accelerometer', 'ultrasonic', 'lidar'],
                'brands': ['REV', 'CTRE', 'VEX', 'AndyMark', 'NavX', 'Pigeon'],
                'specs': ['resolution', 'accuracy', 'range', 'frequency']
            },
            'mechanical': {
                'keywords': ['gear', 'belt', 'chain', 'wheel', 'bearing', 'bracket', 'mount'],
                'brands': ['REV', 'VEX', 'AndyMark', 'West Coast Products'],
                'specs': ['size', 'pitch', 'width', 'length', 'diameter']
            }
        }
        
        # FRC özel parça tanımları
        self.frc_parts = {
            'neo': {
                'must_keywords': ['NEO', 'brushless'],
                'optional_keywords': ['motor', '550'],
                'brands': ['REV'],
                'specs': ['brushless', '550', 'motor']
            },
            'kraken': {
                'must_keywords': ['Kraken', 'X60'],
                'optional_keywords': ['brushless', 'motor'],
                'brands': ['WCP', 'West Coast Products'],
                'specs': ['X60', 'brushless', 'motor']
            },
            'spark_max': {
                'must_keywords': ['SPARK', 'MAX'],
                'optional_keywords': ['controller', 'esc'],
                'brands': ['REV'],
                'specs': ['controller', 'esc', 'brushless']
            },
            'talon_srx': {
                'must_keywords': ['Talon', 'SRX'],
                'optional_keywords': ['controller', 'esc'],
                'brands': ['CTRE'],
                'specs': ['controller', 'esc', 'brushless']
            },
            'victor_spx': {
                'must_keywords': ['Victor', 'SPX'],
                'optional_keywords': ['controller', 'esc'],
                'brands': ['CTRE'],
                'specs': ['controller', 'esc', 'pwm']
            },
            'cancoder': {
                'must_keywords': ['CANcoder'],
                'optional_keywords': ['encoder', 'magnetic'],
                'brands': ['CTRE'],
                'specs': ['encoder', 'magnetic', 'absolute']
            }
        }

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

    def validate_product_structure(self, json_ld: Dict) -> Tuple[bool, List[str]]:
        """
        JSON-LD Product yapısının geçerliliğini kontrol et
        
        Args:
            json_ld: JSON-LD Product verisi
            
        Returns:
            (geçerli_mi, hata_listesi)
        """
        errors = []
        
        # Temel alanlar
        required_fields = ['@type', 'name']
        for field in required_fields:
            if field not in json_ld:
                errors.append(f"Missing required field: {field}")
        
        # @type kontrolü
        if json_ld.get('@type') != 'Product':
            errors.append("Invalid @type, expected 'Product'")
        
        # Name kontrolü
        name = json_ld.get('name', '')
        if not name or len(name.strip()) < 3:
            errors.append("Product name too short or empty")
        
        # Offers yapısı kontrolü
        offers = json_ld.get('offers', {})
        if offers:
            if isinstance(offers, dict):
                # Tek offer
                if 'price' in offers and not self._is_valid_price(offers.get('price')):
                    errors.append("Invalid price format")
            elif isinstance(offers, list):
                # Çoklu offers
                for i, offer in enumerate(offers):
                    if not isinstance(offer, dict):
                        errors.append(f"Invalid offer structure at index {i}")
                    elif 'price' in offer and not self._is_valid_price(offer.get('price')):
                        errors.append(f"Invalid price format in offer {i}")
        
        return len(errors) == 0, errors

    def _is_valid_price(self, price) -> bool:
        """Fiyat formatının geçerliliğini kontrol et"""
        if price is None:
            return True  # Fiyat opsiyonel olabilir
        
        try:
            if isinstance(price, (int, float)):
                return price >= 0
            elif isinstance(price, str):
                # Para birimi sembolleri ve sayıları
                price_clean = re.sub(r'[^\d.,]', '', price)
                if price_clean:
                    return float(price_clean.replace(',', '')) >= 0
            return False
        except (ValueError, TypeError):
            return False

    def is_frc_part(self, json_ld: Dict, html: str = '') -> Tuple[bool, str, float]:
        """
        Ürünün FRC parçası olup olmadığını ve eşleşme skorunu hesapla
        
        Args:
            json_ld: JSON-LD Product verisi
            html: HTML içeriği (opsiyonel)
            
        Returns:
            (frc_parçası_mi, kategori, eşleşme_skoru)
        """
        if not json_ld:
            return False, 'unknown', 0.0
        
        # Tüm metin içeriğini birleştir
        text_content = ' '.join([
            json_ld.get('name', ''),
            json_ld.get('description', ''),
            json_ld.get('sku', '') or '',
            json_ld.get('mpn', '') or '',
            html
        ]).lower()
        
        # FRC kategori skorları
        category_scores = {}
        for category, specs in self.frc_categories.items():
            score = self._calculate_category_score(text_content, specs)
            category_scores[category] = score
        
        # En yüksek skorlu kategoriyi bul
        best_category = max(category_scores.items(), key=lambda x: x[1])
        
        # FRC parça eşleşmeleri
        part_scores = {}
        for part_name, part_specs in self.frc_parts.items():
            score = self._calculate_part_score(text_content, part_specs)
            part_scores[part_name] = score
        
        # En yüksek skorlu parçayı bul
        best_part = max(part_scores.items(), key=lambda x: x[1])
        
        # Genel FRC eşleşme skoru
        frc_keywords = ['frc', 'first robotics', 'robotics competition', 'vex', 'rev', 'ctre']
        frc_score = sum(1 for keyword in frc_keywords if keyword in text_content)
        frc_score = min(frc_score / len(frc_keywords), 1.0)
        
        # Toplam skor hesapla
        total_score = max(
            best_category[1] * 0.4,  # Kategori skoru
            best_part[1] * 0.6,       # Parça skoru
            frc_score * 0.3          # Genel FRC skoru
        )
        
        # Eşik değeri
        is_frc = total_score >= 0.3
        
        if best_part[1] > best_category[1]:
            return is_frc, best_part[0], total_score
        else:
            return is_frc, best_category[0], total_score

    def _calculate_category_score(self, text: str, category_specs: Dict) -> float:
        """Kategori eşleşme skorunu hesapla"""
        score = 0.0
        
        # Anahtar kelimeler
        keywords = category_specs.get('keywords', [])
        keyword_matches = sum(1 for keyword in keywords if keyword in text)
        if keywords:
            score += (keyword_matches / len(keywords)) * 0.4
        
        # Markalar
        brands = category_specs.get('brands', [])
        brand_matches = sum(1 for brand in brands if brand.lower() in text)
        if brands:
            score += (brand_matches / len(brands)) * 0.3
        
        # Özellikler
        specs = category_specs.get('specs', [])
        spec_matches = sum(1 for spec in specs if spec in text)
        if specs:
            score += (spec_matches / len(specs)) * 0.3
        
        return min(score, 1.0)

    def _calculate_part_score(self, text: str, part_specs: Dict) -> float:
        """Parça eşleşme skorunu hesapla"""
        score = 0.0
        
        # Zorunlu anahtar kelimeler
        must_keywords = part_specs.get('must_keywords', [])
        must_matches = sum(1 for keyword in must_keywords if keyword.lower() in text)
        if must_keywords:
            must_score = must_matches / len(must_keywords)
            if must_score < 1.0:  # Tüm zorunlu kelimeler yoksa düşük skor
                return 0.0
            score += must_score * 0.6
        
        # Opsiyonel anahtar kelimeler
        optional_keywords = part_specs.get('optional_keywords', [])
        optional_matches = sum(1 for keyword in optional_keywords if keyword.lower() in text)
        if optional_keywords:
            score += (optional_matches / len(optional_keywords)) * 0.2
        
        # Marka eşleşmesi
        brands = part_specs.get('brands', [])
        brand_matches = sum(1 for brand in brands if brand.lower() in text)
        if brands:
            score += (brand_matches / len(brands)) * 0.2
        
        return min(score, 1.0)

    def extract_product_info(self, json_ld: Dict, url: str = '') -> Dict:
        """
        JSON-LD'den ürün bilgilerini çıkar ve normalize et
        
        Args:
            json_ld: JSON-LD Product verisi
            url: Ürün URL'i
            
        Returns:
            Normalize edilmiş ürün bilgileri
        """
        if not json_ld:
            return {}
        
        # Fiyat bilgisi
        price = None
        currency = 'USD'
        offers = json_ld.get('offers', {})
        
        if isinstance(offers, dict):
            price = offers.get('price')
            currency = offers.get('priceCurrency', 'USD')
        elif isinstance(offers, list) and offers:
            price = offers[0].get('price')
            currency = offers[0].get('priceCurrency', 'USD')
        
        # Fiyatı normalize et
        if price:
            try:
                if isinstance(price, str):
                    # Para birimi sembollerini temizle
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
        
        # Marka
        brand = None
        brand_data = json_ld.get('brand', {})
        if isinstance(brand_data, dict):
            brand = brand_data.get('name')
        elif isinstance(brand_data, str):
            brand = brand_data
        
        return {
            'name': json_ld.get('name', '').strip(),
            'url': url,
            'price': price,
            'currency': currency,
            'inStock': in_stock,
            'sku': json_ld.get('sku') or json_ld.get('mpn'),
            'image': image,
            'brand': brand,
            'description': json_ld.get('description', '')[:200] if json_ld.get('description') else '',
            'category': json_ld.get('category', ''),
            'gtin': json_ld.get('gtin'),
            'mpn': json_ld.get('mpn')
        }

    def validate_canonical_match(self, json_ld: Dict, canonical_specs: Dict, html: str = '') -> Tuple[bool, float]:
        """
        Canonical parça özellikleriyle eşleşme kontrolü
        
        Args:
            json_ld: JSON-LD Product verisi
            canonical_specs: Canonical parça özellikleri
            html: HTML içeriği
            
        Returns:
            (eşleşme_var_mı, eşleşme_skoru)
        """
        if not json_ld or not canonical_specs:
            return False, 0.0
        
        # Tüm metin içeriğini birleştir
        text_content = ' '.join([
            json_ld.get('name', ''),
            json_ld.get('description', ''),
            json_ld.get('sku', '') or '',
            json_ld.get('mpn', '') or '',
            html
        ]).lower()
        
        # Zorunlu anahtar kelimeler
        must_keywords = canonical_specs.get('must_keywords', [])
        if must_keywords:
            must_matches = sum(1 for keyword in must_keywords if keyword.lower() in text_content)
            must_score = must_matches / len(must_keywords)
            if must_score < 1.0:  # Tüm zorunlu kelimeler yoksa eşleşme yok
                return False, 0.0
        else:
            must_score = 1.0
        
        # Opsiyonel anahtar kelimeler
        optional_keywords = canonical_specs.get('optional_keywords', [])
        optional_score = 0.0
        if optional_keywords:
            optional_matches = sum(1 for keyword in optional_keywords if keyword.lower() in text_content)
            optional_score = optional_matches / len(optional_keywords)
        
        # Marka eşleşmesi
        brand_score = 0.0
        expected_brands = canonical_specs.get('brands', [])
        if expected_brands:
            brand_matches = sum(1 for brand in expected_brands if brand.lower() in text_content)
            brand_score = brand_matches / len(expected_brands)
        
        # Toplam skor
        total_score = (must_score * 0.5 + optional_score * 0.3 + brand_score * 0.2)
        
        # Eşik değeri
        is_match = total_score >= 0.6
        
        return is_match, total_score


# Test ve örnek kullanım
if __name__ == "__main__":
    validator = JSONLDValidator()
    
    # Örnek JSON-LD
    sample_json_ld = {
        "@type": "Product",
        "name": "REV NEO 550 Brushless Motor",
        "description": "High-performance brushless motor for FRC robotics",
        "sku": "REV-21-1651",
        "brand": {"@type": "Brand", "name": "REV Robotics"},
        "offers": {
            "@type": "Offer",
            "price": "29.99",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock"
        },
        "image": "https://example.com/neo550.jpg"
    }
    
    # Doğrulama
    is_valid, errors = validator.validate_product_structure(sample_json_ld)
    print(f"Valid: {is_valid}, Errors: {errors}")
    
    # FRC parça kontrolü
    is_frc, category, score = validator.is_frc_part(sample_json_ld)
    print(f"FRC Part: {is_frc}, Category: {category}, Score: {score}")
    
    # Ürün bilgilerini çıkar
    product_info = validator.extract_product_info(sample_json_ld, "https://example.com/product")
    print(f"Product Info: {product_info}")
