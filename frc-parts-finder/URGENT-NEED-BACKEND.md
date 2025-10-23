# URGENT: Backend Gerekli - Manuel Veri Artık Çalışmıyor

## Mevcut Sorunlar

### 1. Fiyatlar Yanlış
- NEO Motor: Gerçek $56 → Sitede $39.99 yazıyor ❌
- Tüm fiyatlar manuel, eski, yanlış

### 2. URL'ler Sürekli Değişiyor
- AndyMark URL formatı değişti
- Her satıcı farklı URL yapısı kullanıyor
- Manuel güncelleme imkansız

### 3. Eksik Satıcılar
- CTRE yok
- WCP sadece Kraken'de var
- REV, VEX, AndyMark için bile eksik ürünler

### 4. Stok Durumu Sahte
- "In Stock" / "Out of Stock" gerçek değil
- Kullanıcıları yanıltıyor

## Çözüm: Backend Kurulumu

### Adım 1: Node.js Backend (1-2 saat)
```bash
# Backend klasörü oluştur
mkdir backend
cd backend
npm init -y
npm install express cors puppeteer cheerio
```

### Adım 2: Web Scraper Yaz (Her satıcı için)

**AndyMark Scraper:**
```javascript
async function scrapeAndyMark(query) {
    const url = `https://www.andymark.com/search?q=${query}`;
    const response = await fetch(url);
    const html = await response.text();

    // Parse HTML, extract:
    // - Product name
    // - Real price
    // - Stock status
    // - Product URL

    return products;
}
```

**REV Robotics Scraper:**
```javascript
async function scrapeREV(query) {
    const url = `https://www.revrobotics.com/search/?q=${query}`;
    // ... similar
}
```

### Adım 3: API Endpoint
```javascript
app.get('/api/search', async (req, res) => {
    const { query } = req.query;

    const results = await Promise.all([
        scrapeAndyMark(query),
        scrapeREV(query),
        scrapeVEX(query),
        scrapeWCP(query),
        scrapeCTRE(query)
    ]);

    res.json(results.flat());
});
```

### Adım 4: Frontend Değişikliği
```javascript
// OLD (fake data)
const mockResults = generateMockResults(searchQuery);

// NEW (real data from backend)
const response = await fetch(`http://localhost:3000/api/search?query=${searchQuery}`);
const realResults = await response.json();
```

## Alternatif: API Kullanımı

### Google Custom Search API
- $5 / 1000 arama
- Otomatik link bulma
- Gerçek sonuçlar

### SerpAPI (Google Shopping)
- Fiyat karşılaştırma API'si
- Gerçek zamanlı fiyatlar
- $50/ay

## Hemen Yapılacaklar

### Seçenek A: Backend Kuruyorum (Önerilen)
1. Node.js backend kuruyorum (15 dakika)
2. AndyMark scraper yazıyorum (30 dakika)
3. Test ediyoruz (gerçek fiyatlar!)
4. Diğer satıcıları ekliyorum (her biri 20 dakika)

**Toplam süre:** 2-3 saat
**Sonuç:** Gerçek fiyatlar, gerçek linkler, gerçek stok

### Seçenek B: Manuel Düzeltme (Sürdürülebilir Değil)
1. Her ürünü manuel kontrol ediyorum
2. Fiyatları tek tek bakıp yazıyorum
3. URL'leri test ediyorum
4. 1 hafta sonra yine yanlış olacak ❌

## Karar Zamanı

**Soru:** Backend kurulum için izin var mı?

✅ **Evet** → 2 saat sonra gerçek verilerle çalışan sistem
❌ **Hayır** → Manuel olarak düzelteyim (ama 1 hafta sonra yine bozulacak)

Hangisini tercih edersiniz?

## Backend Kurulumuna Başlama

Eğer "Evet" derseniz, şunları yapacağım:

1. `backend/` klasörü oluşturacağım
2. Express server kuracağım
3. İlk scraper'ı yazacağım (AndyMark)
4. Test edeceğiz (NEO motor gerçek fiyat!)
5. Diğer satıcıları ekleyeceğiz

Hazır mısınız? 🚀
