# FRC Parts Finder - Enhanced Features

## 🚀 Yeni Özellikler

### 1. Gerçek FRC Tedarikçi Entegrasyonu
- **WCP (West Coast Products)** - https://wcproducts.com
- **REV Robotics** - https://www.revrobotics.com  
- **AndyMark** - https://andymark.com
- **CTRE** - https://store.ctr-electronics.com

### 2. Shopify/WooCommerce Arama Sistemi
- Shopify API entegrasyonu (search/suggest.json, products.json)
- WooCommerce Store API entegrasyonu
- JSON-LD Product doğrulama
- Akıllı önbellek sistemi (24-48 saat TTL)

### 3. Gelişmiş Arama Algoritmaları
- Canonical parça özellikleri eşleştirme
- FRC parça tanıma sistemi
- Çoklu tedarikçi arama
- Rate limiting ve hata yönetimi

## 📁 Dosya Yapısı

```
backend/
├── server_enhanced.py          # Ana gelişmiş server
├── real_vendor_search.py       # Gerçek tedarikçi arama
├── shopify_search.py          # Shopify arama motoru
├── woocommerce_search.py      # WooCommerce arama motoru
├── json_ld_validator.py       # JSON-LD doğrulama
├── cache_manager.py           # Önbellek yönetimi
├── test_real_vendors.py       # Test scripti
└── requirements.txt           # Güncellenmiş bağımlılıklar
```

## 🛠️ Kurulum ve Çalıştırma

### 1. Bağımlılıkları Yükle
```bash
cd backend
pip install -r requirements.txt
```

### 2. Gelişmiş Server'ı Başlat
```bash
python3 server_enhanced.py
```

### 3. Test Et
```bash
python3 test_real_vendors.py
```

## 🔧 API Endpoint'leri

### Ana Arama
- `GET /api/search?q={query}` - Tüm tedarikçilerde arama

### Özel Arama
- `GET /api/search/real-vendors?q={query}` - Gerçek FRC tedarikçileri
- `GET /api/search/shopify?q={query}` - Shopify tedarikçileri
- `GET /api/search/woocommerce?q={query}` - WooCommerce tedarikçileri

### Önbellek Yönetimi
- `GET /api/cache/stats` - Önbellek istatistikleri
- `POST /api/cache/clear` - Önbelleği temizle
- `POST /api/cache/cleanup` - Süresi dolmuş kayıtları temizle

### Sistem Durumu
- `GET /api/health` - Sistem durumu ve özellikler

## 🎯 Özellikler

### 1. Akıllı Arama Sırası
1. **Veritabanı** - Mevcut FRC parça veritabanı
2. **Gerçek Tedarikçiler** - WCP, REV, AndyMark, CTRE
3. **Shopify Tedarikçiler** - Genel Shopify mağazaları
4. **WooCommerce Tedarikçiler** - Genel WooCommerce mağazaları
5. **Fallback** - Manuel arama linkleri

### 2. JSON-LD Doğrulama
- Ürün bilgilerini otomatik doğrulama
- FRC parça tanıma sistemi
- Canonical özellik eşleştirme
- Fiyat ve stok durumu normalizasyonu

### 3. Önbellek Sistemi
- URL durumu önbelleği (1 saat)
- Arama sonuçları önbelleği (2 saat)
- Ürün bilgileri önbelleği (24 saat)
- Otomatik süresi dolmuş kayıt temizleme

### 4. Rate Limiting
- Domain başına istek sınırlaması
- Akıllı bekleme algoritması
- Hata yönetimi ve yeniden deneme

## 🔍 Kullanım Örnekleri

### Frontend'den Arama
```javascript
// Ana arama
fetch('http://localhost:5001/api/search?q=NEO%20motor')
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.count} products from ${data.source}`);
    data.results.forEach(product => {
      console.log(`${product.name}: $${product.price} (${product.vendor})`);
    });
  });
```

### Gerçek Tedarikçi Arama
```javascript
// Sadece gerçek FRC tedarikçileri
fetch('http://localhost:5001/api/search/real-vendors?q=Kraken%20X60')
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.count} products from real vendors`);
    console.log(`Vendors: ${data.vendors.join(', ')}`);
  });
```

## 📊 Performans

### Önbellek İstatistikleri
```bash
curl http://localhost:5001/api/cache/stats
```

### Önbellek Temizleme
```bash
curl -X POST http://localhost:5001/api/cache/clear
```

## 🚨 Hata Yönetimi

### Yaygın Hatalar
1. **Rate Limiting** - Çok fazla istek
2. **Network Timeout** - Bağlantı zaman aşımı
3. **Invalid JSON-LD** - Bozuk ürün verisi
4. **Cache Miss** - Önbellek hatası

### Çözümler
- Otomatik yeniden deneme
- Fallback arama sistemleri
- Hata loglama ve raporlama
- Graceful degradation

## 🔧 Konfigürasyon

### Rate Limiting
```python
# Her tedarikçi için farklı rate limit
real_vendor_engine = RealVendorSearchEngine(rate_limit_delay=1.0)
shopify_engine = ShopifySearchEngine(rate_limit_delay=0.5)
```

### Önbellek TTL
```python
# Farklı veri türleri için farklı TTL
cache_manager.set_url_status(url, status, ttl=3600)      # 1 saat
cache_manager.set_search_results(query, results, ttl=7200) # 2 saat
cache_manager.set_product_info(url, info, ttl=86400)     # 24 saat
```

## 🎉 Sonuç

Bu gelişmiş sistem ile:
- ✅ Gerçek FRC tedarikçilerinden canlı veri
- ✅ Akıllı önbellek sistemi
- ✅ JSON-LD doğrulama
- ✅ Rate limiting ve hata yönetimi
- ✅ Çoklu arama stratejisi
- ✅ Performans optimizasyonu

**Başlatmak için:**
```bash
cd backend
python3 server_enhanced.py
```

**Test etmek için:**
```bash
python3 test_real_vendors.py
```
