# FRC Parça Bulucu

FRC robotik yarışmaları için parça arama, fiyat karşılaştırma ve sorun giderme platformu.

## Özellikler

### 1. Parça Arama Motoru
- Kullanıcı parça adını arama kutusuna yazar (örn: "NEO Motor", "Falcon 500")
- Birden fazla satıcıdan sonuçlar getirir:
  - REV Robotics
  - AndyMark
  - VEX Robotics
  - West Coast Products (WCP)

### 2. Ürün Kartları
Her ürün kartında şunlar gösterilir:
- **Ürün resmi**
- **Satıcı adı** (renkli rozet)
- **Fiyat bilgisi**
- **İndirim durumu** (varsa orijinal fiyat ve indirim yüzdesi)
- **Stok durumu**:
  - ✓ Stokta Var (Yeşil)
  - ✗ Stokta Yok (Kırmızı)
  - ⚠ Sınırlı Stok (Sarı)
- **Ürünü Görüntüle butonu** (satıcının sitesine yönlendirir)

### 3. Chief Delphi Forum Entegrasyonu
Arama yapıldıktan sonra, seçilen parça için:
- Bilinen sorunlar
- Kullanıcı deneyimleri
- Çözüm önerileri
- Forum tartışma linkleri

Her forum kartında:
- Tartışma başlığı
- Chief Delphi linki
- Yanıt sayısı
- Görüntülenme sayısı
- Tarih bilgisi

## Kurulum

1. Projeyi indirin
2. `index.html` dosyasını bir web tarayıcıda açın
3. Parça aramaya başlayın!

## Kullanım

1. Arama kutusuna parça adını yazın (örn: "NEO Motor")
2. "Ara" butonuna tıklayın veya Enter tuşuna basın
3. Sonuçlar küçük kartlar halinde görünecek
4. Fiyatları, stok durumlarını ve indirimleri karşılaştırın
5. İstediğiniz ürünün "Ürünü Görüntüle" butonuna tıklayın
6. Sayfanın alt kısmında Chief Delphi forum tartışmalarını inceleyin

## Geliştirme Notları

### Şu Anki Durum
Proje şu anda **mock (örnek) veriler** kullanmaktadır. Gerçek e-ticaret sitelerinden veri çekmek için API entegrasyonu gereklidir.

### Gelecek Geliştirmeler

#### API Entegrasyonları
Gerçek veri çekmek için:
1. **REV Robotics API**: `https://www.revrobotics.com/api/...`
2. **AndyMark API**: Web scraping veya API
3. **VEX Robotics API**: Web scraping veya API
4. **Chief Delphi API**: `https://www.chiefdelphi.com` discourse API

#### Backend Geliştirme
- Node.js + Express sunucu
- Web scraping için Puppeteer veya Cheerio
- CORS sorunlarını çözmek için proxy
- Cache sistemi (hız için)

#### Örnek Backend Kodu (Node.js)
```javascript
const express = require('express');
const axios = require('axios');
const app = express();

app.get('/api/search', async (req, res) => {
    const query = req.query.q;
    // REV Robotics'ten veri çek
    const revData = await axios.get(`https://www.revrobotics.com/search?q=${query}`);
    // Veriyi parse et ve gönder
    res.json(results);
});
```

#### Discourse API (Chief Delphi)
```javascript
const searchChiefDelphi = async (query) => {
    const response = await fetch(
        `https://www.chiefdelphi.com/search.json?q=${encodeURIComponent(query)}`
    );
    const data = await response.json();
    return data.topics;
};
```

## Teknolojiler

- **HTML5**: Sayfa yapısı
- **CSS3**: Tasarım ve animasyonlar (Gradient, Grid, Flexbox)
- **JavaScript (Vanilla)**: Dinamik içerik ve interaktivite
- **Font Awesome**: İkonlar

## Responsive Tasarım

Site mobil cihazlarda da düzgün çalışır:
- Tablet: 2 sütun
- Mobil: 1 sütun
- Arama kutusu mobilde dikey hizalanır

## Lisans

Bu proje eğitim amaçlıdır. Kullanım serbest!

## Katkıda Bulunma

1. Gerçek API entegrasyonları ekleyin
2. Daha fazla satıcı ekleyin (Robot Shop, McMaster-Carr, etc.)
3. Fiyat geçmişi grafiği ekleyin
4. Favori parçalar sistemi ekleyin
5. Karşılaştırma özelliği ekleyin

## İletişim

Sorularınız için: [GitHub Issues](https://github.com)

Mutlu kodlamalar! 🤖🔧
