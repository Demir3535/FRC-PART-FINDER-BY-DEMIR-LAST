# FRC Parts Database - JSON Implementation Guide

## 🎉 Yeni Özellikler

Projeniz artık **JSON tabanlı ürün veritabanı** kullanıyor! Tüm ürünler artık kolayca yönetilebilir, güncellenebilir ve genişletilebilir.

## 📁 Dosya Yapısı

```
frc-parts-finder/
├── data/
│   └── products-database.json    # Ana ürün veritabanı
├── js/
│   └── app.js                     # Güncellenmiş JavaScript
├── index.html                     # Ana sayfa
├── test-database.html             # Test sayfası
└── DATABASE-README.md             # Bu dosya
```

## 🚀 Nasıl Çalışır?

### 1. Otomatik Yükleme
Sayfa açıldığında `products-database.json` otomatik olarak yüklenir:

```javascript
// Sayfa yüklendiğinde veritabanı otomatik yüklenir
document.addEventListener('DOMContentLoaded', async function() {
    await loadProductsDatabase();
});
```

### 2. Akıllı Arama
Arama fonksiyonları JSON veritabanını kullanır:

- **Tam eşleşme**: "neo motor" → NEO Motor ürünlerini bulur
- **Normalleştirilmiş arama**: "robo rio 2.0" → roboRIO 2.0'ı bulur
- **Kısmi eşleşme**: "kraken" → Kraken X60'ı bulur
- **Kelime bazlı**: "spark max" → SPARK MAX'i bulur

### 3. Direkt Linkler
Her ürünün **doğrulanmış direkt linki** var:

```json
{
  "url": "https://www.revrobotics.com/rev-21-1650/"
}
```

## 📊 Veritabanı Yapısı

### JSON Format
```json
{
  "version": "1.0.0",
  "lastUpdated": "2025-01-24",
  "products": {
    "neo motor": [
      {
        "name": "NEO Brushless Motor",
        "vendor": "REV Robotics",
        "price": 50.00,
        "stock": "in-stock",
        "url": "https://www.revrobotics.com/rev-21-1650/",
        "category": "motors",
        "tags": ["brushless", "neo", "drivetrain"]
      }
    ]
  }
}
```

### Ürün Özellikleri

| Alan | Tip | Açıklama | Zorunlu |
|------|-----|----------|---------|
| `name` | string | Ürün adı | ✅ |
| `vendor` | string | Satıcı adı | ✅ |
| `price` | number | Fiyat (USD) | ✅ |
| `stock` | string | Stok durumu | ✅ |
| `url` | string | Direkt ürün linki | ✅ |
| `category` | string | Kategori | ⚪ |
| `tags` | array | Etiketler | ⚪ |
| `image` | string | Görsel URL | ⚪ |
| `originalPrice` | number | Eski fiyat | ⚪ |
| `discount` | number | İndirim yüzdesi | ⚪ |

## ✏️ Ürün Ekleme/Güncelleme

### Yeni Ürün Eklemek

1. `data/products-database.json` dosyasını açın
2. İlgili arama terimine yeni ürün ekleyin:

```json
{
  "products": {
    "yeni motor": [
      {
        "name": "Yeni Motor Adı",
        "vendor": "Satıcı Adı",
        "price": 99.99,
        "stock": "in-stock",
        "url": "https://satiCI.com/urun-linki",
        "category": "motors",
        "tags": ["motor", "yeni"]
      }
    ]
  }
}
```

### Fiyat Güncellemek

Sadece `price` alanını değiştirin:

```json
{
  "price": 55.00  // Eski: 50.00
}
```

### Yeni Satıcı Eklemek

Aynı ürün için farklı satıcı ekleyin:

```json
{
  "neo motor": [
    {
      "name": "NEO Brushless Motor",
      "vendor": "REV Robotics",
      "price": 50.00,
      "url": "https://www.revrobotics.com/rev-21-1650/"
    },
    {
      "name": "NEO Brushless Motor",
      "vendor": "Yeni Satıcı",  // YENİ
      "price": 48.00,
      "url": "https://yenisatici.com/neo"
    }
  ]
}
```

## 🧪 Test Etme

### Test Sayfası
Tarayıcınızda açın:
```
http://localhost:8080/test-database.html
```

### Test Özellikleri
- ✅ Veritabanı yükleme testi
- ✅ Ürün arama testi
- ✅ Tüm linkleri test etme
- ✅ İstatistikler görüntüleme
- ✅ Tüm ürünleri listeleme

### Manuel Test
```javascript
// Console'da test edin:
loadProductsDatabase().then(db => {
    console.log('Products:', db);
    console.log('NEO Motors:', db['neo motor']);
});
```

## 📈 İstatistikler

Mevcut veritabanı:
- **70+ ürün tipi**
- **120+ toplam ürün**
- **6 satıcı**
- **11 kategori**

### Kategoriler
- Motors
- Motor Controllers
- Control System
- Power
- Vision
- Sensors
- Pneumatics
- Drivetrain
- Mechanisms
- Hardware
- Accessories

### Satıcılar
- REV Robotics
- AndyMark
- WCP (West Coast Products)
- CTRE
- Limelight
- Deküp Robotics

## 🔧 Sorun Giderme

### Veritabanı yüklenmiyor

**Kontrol edin:**
1. `data/products-database.json` dosyası var mı?
2. JSON formatı geçerli mi? (JSON validator kullanın)
3. Dosya yolu doğru mu?

**Çözüm:**
```javascript
// Console'da kontrol edin:
fetch('./data/products-database.json')
    .then(r => r.json())
    .then(data => console.log('✅ Database OK:', data))
    .catch(e => console.error('❌ Error:', e));
```

### Ürün bulunamıyor

**Kontrol edin:**
1. Arama terimi JSON'da var mı?
2. Küçük harfle yazıldı mı?
3. Tam eşleşme var mı?

**Örnek:**
```json
// ✅ DOĞRU
"neo motor": [...]

// ❌ YANLIŞ
"NEO Motor": [...]
"Neo motor": [...]
```

### Link çalışmıyor

**Kontrol edin:**
1. URL `http://` veya `https://` ile başlıyor mu?
2. URL geçerli mi?
3. Satıcı sitesi aktif mi?

## 📝 Best Practices

### 1. Arama Terimleri
- Küçük harf kullanın
- Yaygın isimleri kullanın
- Birden fazla varyasyon ekleyin

```json
{
  "neo motor": [...],
  "neo": [...],        // Kısa versiyon
  "rev neo": [...]     // Marka ile
}
```

### 2. Fiyatlar
- Güncel fiyatları kullanın
- USD cinsinden yazın
- İndirim varsa `originalPrice` ekleyin

### 3. Linkler
- Direkt ürün linkini kullanın
- Kısa linkler yerine tam URL kullanın
- Link çalışıyor mu test edin

### 4. Stok Durumu
Kullanılabilir değerler:
- `"in-stock"` - Stokta var
- `"limited-stock"` - Sınırlı stok
- `"out-of-stock"` - Stokta yok
- `"Sold-out"` - Tükendi

## 🎯 Gelecek Özellikler

### Planlanan
- [ ] Otomatik fiyat güncelleme
- [ ] Gerçek zamanlı stok kontrolü
- [ ] Daha fazla satıcı
- [ ] Görsel optimizasyonu
- [ ] Favori ürünler
- [ ] Fiyat karşılaştırma
- [ ] Fiyat geçmişi

### Eklenebilecek Alanlar
```json
{
  "weight": "1.2 lbs",
  "dimensions": "3.5 x 2.5 x 2.5 in",
  "specifications": {
    "maxRPM": 5676,
    "stallTorque": "3.28 N⋅m",
    "stallCurrent": "166 A"
  },
  "reviews": 4.8,
  "inKitOfParts": true
}
```

## 🤝 Katkıda Bulunma

Yeni ürün eklemek için:

1. `data/products-database.json` dosyasını düzenleyin
2. JSON formatını kontrol edin
3. Test sayfasında test edin
4. Tüm linklerin çalıştığından emin olun

## 📞 İletişim

Sorularınız için:
- GitHub Issues
- Email: [your-email]

---

**Son Güncelleme:** 2025-01-24
**Versiyon:** 1.0.0
**Oluşturan:** Demir Avci
