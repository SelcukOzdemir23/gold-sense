# 🏆 Gold-Sense AI

**DSPy Tabanlı Finansal Haber Analiz Sistemi - Altın Piyasası Tahmin Motoru**

> ⚠️ **Akademik Proje Uyarısı:** Bu proje, Yüksek Lisans "İleri Yapay Zeka" dersi kapsamında akademik bir çalışma olarak geliştirilmiştir. Herhangi bir yatırım tavsiyesi içermez ve sadece eğitim amaçlıdır.

Gold-Sense AI, finansal haberleri işleyerek altın piyasası trendlerini tahmin eden akıllı bir haber analiz sistemidir. DSPy (Declarative Self-improving Language Programs) ile oluşturulmuş olup, token-verimli veri gösterimi (TONL), gelişmiş LLM muhakemesi (Chain of Thought) ve olasılıksal güven skorlamasını birleştirerek eyleme geçirilebilir piyasa içgörüleri sunar.

---

## 📋 İçindekiler

- [Neden Gold-Sense AI?](#-neden-gold-sense-ai)
- [Temel Özellikler](#-temel-özellikler)
- [Mimari ve Teknoloji Seçimleri](#-mimari-ve-teknoloji-seçimleri)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Proje Yapısı ve Kod Açıklamaları](#-proje-yapısı-ve-kod-açıklamaları)
- [Konfigürasyon](#-konfigürasyon)
- [Geliştirme](#-geliştirme)

---

## 🎯 Neden Gold-Sense AI?

Altın piyasaları, karmaşık ve birbiriyle bağlantılı faktörlerden etkilenir: makroekonomik politika, jeopolitik olaylar, endüstriyel talep ve para birimi dalgalanmaları. Geleneksel haber analiz sistemleri şu sorunlarla karşılaşır:

1. **Bilgi Aşırı Yüklenmesi:** Günde 50+ haber makalesi saatlerce manuel analiz gerektirir
2. **Önyargı ve Tutarsızlık:** İnsan analistler öznel yorumlar getirir
3. **Token Verimsizliği:** Standart JSON formatları LLM işlemede %40+ token israf eder
4. **Hesap Verebilirlik Eksikliği:** Güven skorlaması veya ağırlıklı kategori önemi yok

Gold-Sense AI bu zorlukları şöyle ele alır:

- **Otomatik İşleme:** Async Cerebras API ile 50 makaleyi <5 saniyede analiz et
- **DSPy Zekası:** Assertion-tabanlı doğrulamalı Chain of Thought muhakemesi
- **TONL Formatı:** Özel metin-optimize notasyon ile %40+ token tasarrufu
- **Güven Skorlaması:** Her analiz için 0-1 arası olasılıksal belirsizlik ölçümü
- **Ağırlıklı Toplama:** Kategori-tabanlı önem (Makro: 1.5x, Jeopolitik: 1.2x, Endüstriyel: 1.0x)

---

## ✨ Temel Özellikler

### 1. **The Journey UI** (3 Sekmeli Streamlit Arayüzü)

**Sekme 1: Haber Hasadı**
- NewsAPI'den altınla ilgili en son 50 haber makalesini çeker
- Şeffaflık için ham JSON verisini gösterir
- Otomatik yerel depolama (`logs/raw_news.json`)

**Sekme 2: TONL Optimizasyonu**
- JSON → TONL (Text-Optimized Notation Language) dönüşümü
- Token tasarrufu metrikleriyle yan yana karşılaştırma
- Görsel gösterim: ~%40 token azaltma başarısı

**Sekme 3: Analiz ve Rapor**
- DSPy destekli Cerebras LLM analizi
- Gerçek zamanlı debug konsolu (`dspy.inspect_history()`)
- İnteraktif haber kartları:
  - Kategori rozetleri (Makro/Jeopolitik/Endüstriyel/Alakasız)
  - 🐂/🐻 ikonlarıyla 1-10 duyarlılık skorları
  - Güven göstergeleri (🟢🟡🔴)
  - Türkçe muhakeme açıklamaları
- Stratejik Özet: Ağırlıklı piyasa trendi + güven metrikleri

### 2. **DSPy Zeka Katmanı**

**Chain of Thought (Düşünce Zinciri):**
- Temel `dspy.Predict` yerine `dspy.ChainOfThought` kullanır
- Modelin iç muhakeme sürecini yakalar (`reasoning` alanı)
- Debug konsolunda görünür şeffaf karar verme

**Gelişmiş Signature'lar (İmzalar):**
- Her giriş/çıkış için açık alan tanımları (`desc`)
- Kalibrasyon kılavuzlu güven skoru alanı (0.0-1.0)
- `Literal` tip ipuçlarıyla kategori zorunluluğu

**Assertion-Tabanlı Doğrulama:**
```python
# Skor 1-10 arasında olmalı kontrolü
dspy.Assert(1 <= score <= 10, "Sentiment score must be 1-10")

# Güven skoru 0-1 arası olmalı kontrolü
dspy.Assert(0.0 <= confidence <= 1.0, "Confidence must be 0.0-1.0")

# Türkçe dil kontrolü önerisi
dspy.Suggest(has_turkish, "Reasoning should be in Turkish")
```

**KullanıHesap Verebilirlik ve Metrikler**

**URL-Tabanlı Tekil Hale Getirme:**
- `_seen_urls` set'i mükerrer analizleri önler
- Temiz `analysis.jsonl` logları garanti eder

**Güven Skorlaması:**
- Model öz-değerlendirmesi (0.0-1.0 belirsizlik ölçümü)
- Görsel göstergeler: 🟢 Yüksek (≥%80) | 🟡 Orta (%50-80) | 🔴 Düşük (<%50)
- Signature talimatlarında kalibrasyon rehberi

**Ağırlıklı Kategori Toplama:**
```python
# Kategori ağırlıkları - her kategorinin piyasa üzerindeki etkisi
CATEGORY_WEIGHTS = {
    "Macro": 1.5,        # Ekonomi/politika (en yüksek etki)
    "Geopolitical": 1.2, # Çatışma/siyaset (orta-yüksek etki)
    "Industrial": 1.0,   # Altın endüstrisi (temel etki)
    "Irrelevant": 0.0    # Hesaplamadan hariç tutulur
}

# Ağırlıklı ortalama formülü:
# ∑(Skor × Ağırlık × Güven) / ∑(Ağırlık × Güven)
# Bu formSağlamlık ve Hata Yönetimi**

**İki Kaynaklı Fiyat Yedekleme:**
```python
# Altın fiyatı alma stratejisi
1. Truncgil API'yi dene (birincil kaynak)
2. Başarısız olursa → Binance PAXGUSDT (yedek kaynak)
3. Her ikisi de başarısız → Nazik yıkılma (None döndür, çökme)
```

**Async (Asenkron) Performans:**
- `asyncio.Semaphore` eşzamanlılık kontrolü (varsayılan: 5 eşzamanlı istek)
- Üstel geri çekilme (exponential backoff) yeniden deneme mantığı
- Zaman aşımı koruması(primary)
2. On failure → Binance PAXGUSDT (fallback)
3. On both failures → Graceful degradation (None return)
```Mimari ve Teknoloji Seçimleri

### Neden DSPy?

**DSPy** (Declarative Self-improving Language Programs), kırılgan prompt mühendisliğini şununla değiştirir:

1. **Tip-Güvenli Signature'lar:** Girdi/çıktı kontratları runtime hatalarını önler
2. **Modüler Kompozisyon:** `ChainOfThought`, `Assert`, `Suggest` yeniden kullanılabilir yapı taşlarıdır
3. **Otomatik Optimizasyon:** Gelecekte `dspy.BootstrapFewShot` prompt ayarlaması desteği
4. **Kullanım Takibi:** Özel sarmalayıcılar olmadan yerleşik token/maliyet izleme

**Reddedilen Alternatif:** LangChain (çok ağır, verbose API, zor debugging)

### Neden TONL (Text-Optimized Notation Language)?

Standart JSON yapısal yük nedeniyle token israf eder:
```json
{
  "title": "Fed Faiz Artırdı",
  "description": "Federal Reserve...",
  "source": {"name": "Reuters"},
  "publishedAt": "2026-02-04T10:00:00Z"
}
```

**TONL Kompakt Formatı:**
```
---
title: Fed Faiz Artırdı
desc: Federal Reserve...
source: Reuters
published: 2026-02-04T10:00:00Z
---
```

**Ölçülmüş Token Tasarrufu:** Cerebras tokenleştirme testlerinde ~%40 azalma

### Neden Cerebras?

- **Hız:** 1,800 token/saniye (mevcut en hızlı çıkarım)
- **Maliyet:** 1M token başına $0.30 (GPT-4'ten 10x daha ucuz)
- **Kalite:** Llama 3.3 70B, finansal görevlerde GPT-4 ile rekabetçi
- **Güvenilirlik:** Üretim iş yükleri için %99.9 çalışma süresi SLA'sı

**Measured Token Savings:** ~40% reduction in Cerebras tokenization tests

### WhKurulum

### Ön Gereksinimler

- **Python 3.11+** (3.11.8 üzerinde test edildi)
- **Sanal Ortam:** `venv` önerilir
- **API Anahtarları:**
  - [NewsAPI](https://newsapi.org/) - Haber veri kaynağı
  - [Cerebras](https://cerebras.ai/) - LLM çıkarım
  - Truncgil Gold API (opsiyonel, Binance yedekleme mevcut)

### Kurulum Adımları

```bash
# 1. Repository'i klonla
git clone https://github.com/your-username/gold-sense-ai.git
cd gold-sense-ai

# 2. Sanal ortam oluştur
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Ortam değişkenlerini yapılandır
cp .env.example .env
# .env dosyasını API anahtarlarınızla düzenleyin:
#   NEWSAPI_KEY=sizin_newsapi_anahtarınız
#   CEREBRAS_API_KEY=sizin_cerebras_anahtarınız
#   TRUNCGIL_URL=https://truncgil-endpoint (opsiyonel)

# 5. Kurulumu doğrula
python -c "import dspy; print('DSPy yüklendi:', dspy.__version__)"
```

### Gerekli Kütüphaneler

```txt
dspy-ai>=2.5.0          # DSPy framework - LLM programlama çerçevesi
httpx>=0.27.0           # Async HTTP client - Asenkron API istekleri
streamlit>=1.41.0       # Web UI - Kullanıcı arayüzü
plotly>=5.24.0          # Visualization - Grafik ve görselleştirme
python-dotenv>=1.0.0    # Environment management - .env dosya yönetimi

### Requirements

```txt
dspy-aKullanım

### Uygulamayı Başlatma

```bash
# Sanal ortamı aktifleştir
source venv/bin/activate

# Streamlit uygulamasını başlat
streamlit run app.py
```

Tarayıcıda `http://localhost:8501` adresine gidin

### İş Akışı

1. **Sekme 1 - Haber Hasadı:**
   - "📰 Haber Getir" butonuna tıklayın
   - JSON genişleticide getirilen makaleleri inceleyin
   - Veri otomatik olarak `logs/raw_news.json` dosyasına kaydedilir

2. **Sekme 2 - TONL Optimizasyonu:**
   - "🔄 TONL'a Çevir" butonuna tıklayın
   - JSON vs TONL yan yana karşılaştırın
   - Token tasarrufu yüzdesini gözlemleyin
   - Veri otomatik olarak `logs/news.tonl` dosyasına kaydedilir

3. **Sekme 3 - Analiz ve Rapor:**
   - "🧠 Analizi Başlat" butonuna tıklayın
   - LLM muhakemesi için debug konsolunu izleyin
   - Stratejik Özet'i inceleyin (trend + güven)
   - Skor/kategorilerle haber kartlarını keşfedin
   - Analiz otomatik olarak `logs/analysis.jsonl` dosyasına kaydedilir

### Komut Satırı Scriptleri

```bash
# Hızlı sağlık kontrolü
python scripts/quick_check.py

# Binance yedekleme testi
python scripts/test_binance.py

# TONL format demosucripts

```bash
# Quick health check
python scripts/quick_check.py

# Test Binance fallback
python scripts/test_binance.py

# TONL format demo
python scripts/tonl_demo.py
```

---

## 📁 Project Structure
 Yapısı ve Kod Açıklamaları

```
gold-sense-ai/
├── app.py                    # Streamlit UI (ana giriş noktası)
│                             # 4 sekme: Haber, TONL, Analiz, Debug Console
│                             # Görselleştirme ve kullanıcı etkileşimi
│
├── main.py                   # CLI runner (alternatif arayüz)
│                             # Komut satırı kullanımı için
│
├── requirements.txt          # Python bağımlılıkları
│                             # Tüm gerekli kütüphaneler ve versiyonları
│
├── src/goldsense/           # Ana uygulama modülleri
│   ├── __init__.py          # Paket başlatıcı
│   │
│   ├── analyst.py           # DSPy GoldAnalyst (ChainOfThought)
│   │                        # GoldSignalSignature: DSPy signature tanımı
│   │                        #   - Input fields: title, description
│   │                        #   - Output fields: is_relevant, category, sentiment_score,
│   │                        #     impact_reasoning, confidence_score
│   │                        # GoldAnalyst sınıfı:
│   │                        #   - _configure_lm(): Cerebras LM yapılandırması
│   │                        #   - analyze_articles(): Async batch analiz
│   │                        #   - _analyze_one(): Tek haber analizi
│   │                        #   - Assertion validations: Skor 1-10, güven 0-1 kontrolü
│   │
│   ├── config.py            # Settings & ortam değişkenleri
│   │                        # pydantic-settings ile tip-güvenli konfigürasyon
│   │                        # .env dosyasından API anahtarları yükleme
│   │                        # Cerebras, NewsAPI, Truncgil ayarları
│   │
│   ├── engine.py            # MarketEngine (ağırlıklı toplama)
│   │                        # CATEGORY_WEIGHTS: Kategori önem ağırlıkları
│   │                        # summarize(): Piyasa trendini hesaplar
│   │                        # _calculate_weighted_score(): Ağırlıklı ortalama formülü
│   │                        #   ∑(Score × Weight × Confidence) / ∑(Weight × Confidence)
│   │                        # Bullish/Bearish/Neutral karar mantığı
│   │
│   ├── exceptions.py        # Özel hata tipleri
│   │                        # ExternalServiceError: API hataları için
 │                        #   - confidence_average: Ortalama güven
│   │
│   ├── price.py             # GoldPriceService (Truncgil + Binance)
│   │                        # get_current_price(): İki kaynaklı fiyat alma
│   │                        # _fetch_price_from_truncgil(): Birincil kaynak
│   │                        # _fetch_from_binance(): Yedek kaynak (PAXGUSDT)
│   │                        # Graceful degradation: Hata durumunda None döner
│   │
│   └── tonl.py              # TONL dönüştürücü (JSON → TONL)
│                            # convert_to_tonl(): JSON'u kompakt formata çevirir
│                            # calculate_token_savings(): Token tasarrufu hesabı
│                            # ~%40 token azaltma hedefi
│
├── scripts/                 # Yardımcı scriptler
│   ├── quick_check.py       # Sağlık kontrolü - tüm servisleri test et
│   ├── test_binance.py      # Binance API testi - fiyat çekme kontrolü
│   └── tonl_demo.py         # TONL format gösterimi - format örnekleri
│
├── docs/                    # Dokümantasyon
│   ├── checklist.md         # Proje tamamlama kontrol listesi
│   ├── prd.md               # Ürün Gereksinim Dokümanı
│   └─Konfigürasyon

### Ortam Değişkenleri (.env)

```bash
# NewsAPI Yapılandırması
NEWSAPI_KEY=sizin_newsapi_anahtarınız

# Cerebras LLM Yapılandırması
CEREBRAS_API_KEY=sizin_cerebras_anahtarınız
CEREBRAS_MODEL=llama-3.3-70b  # Varsayılan model
CEREBRAS_API_BASE=https://api.cerebras.ai/v1

# Altın Fiyat Servisleri
TRUNCGIL_URL=https://truncgil-endpoint  # Opsiyonel
USE_YFINANCE_FALLBACK=true  # Binance yedeklemeyi etkinleştir

# Analiz Ayarları
MAX_CONCURRENCY=5           # Eşzamanlı istek limiti
ANALYSIS_TEMPERATURE=0.3    # LLM yaratıcılığı (0.0-1.0, düşük=tutarlı)
MAX_ARTICLES=50             # Haber çekme limiti
```

### Özelleştirme Seçenekleri

**LLM Modelini Değiştirme:**
```python
# src/goldsense/config.py dosyasında
cerebras_model: str = "llama-3.1-8b"  # Daha hızlı, daha ucuz seçenek
```

**Kategori Ağırlıklarını Ayarlama:**
```python
# src/goldsense/engine.py dosyasında
CATEGORY_WEIGHTS = {
    "Macro": 2.0,        # Makro önemini artır
    "Geopolitical": 1.0, # Jeopolitik normal
    "Industrial": 0.8,   # Endüstriyel azalt
}
```

**Güven Eşiklerini Değiştirme:**
```python
# app.py dosyasında
# Güven gösterge renkleri| <$0.05 | ~$0.023 | ✅ PASS |

### Token Savings (TONL vs JSON)

- **JSON Format:** ~185 characters per article
- **TONGeliştirme

### Testleri Çalıştırma

```bash
# Birim testleri
pytest tests/

# Belirli test dosyası
pytest tests/test_tonl.py -v

# Kapsam raporu
pytest --cov=src/goldsense --cov-report=html
```

### Kod Kalitesi

```bash
# Kod formatlama
black src/ app.py

# Lint kontrolü
ruff check src/

# Tip kontrolü
mypy src/ --strict
```

### Yeni Özellik Ekleme

1. **Yeni Analiz Kategorisi:**
   - `models.py` dosyasında `Category` tipini güncelle
   - `engine.py` dosyasında `CATEGORY_WEIGHTS` ağırlığını ekle
   - `analyst.py` dosyasında signature talimatlarını güncelle

2. **Yeni Veri Kaynağı:**
   - Temel yapıyı miras alan yeni fetcher sınıfı oluştur
   - `fetch_news()` metodunu implement et
   - `app.py` dosyasında fallback mantığı ekle

3. **Özel DSPy Signature:**
   - Yeni `dspy.Signature` sınıfı tanımla
   - `desc` ile girdi/çıktı alanları ekle
   - Muhakeme için `dspy.ChainOfThought` ile sarmala

---

## 📚 Ek Kaynaklar

- **DSPy Dokümantasyonu:** [https://dspy-docs.vercel.app/](https://dspy-docs.vercel.app/)
- **Cerebras API:** [https://inference-docs.cerebras.ai/](https://inference-docs.cerebras.ai/)
- **NewsAPI Dökümanları:** [https://newsapi.org/docs](https://newsapi.org/docs)
- **Streamlit Rehberi:** [https://docs.streamlit.io/](https://docs.streamlit.io/)

---

## 🎓 Akademik Bağlam

Bu proje, **Yüksek Lisans "İleri Yapay Zeka"** dersi kapsamında akademik bir çalışma olarak geliştirilmiştir. Amaçlar:

- DSPy framework'ünü finansal analiz alanında uygulamak
- Token verimliliği için yenilikçi veri gösterimi (TONL) geliştirmek
- LLM muhakeme süreçlerini şeffaflaştırmak (Chain of Thought)
- Hesap verebilirlik için güven skorlaması entegre etmek

### ⚠️ Önemli Uyarı

**Bu sistem yatırım tavsiyesi içermez.** Sadece eğitim ve araştırma amaçlıdır. Finansal kararlar almadan önce profesyonel danışmanlık alınmalıdır.

---

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - detaylar için LICENSE dosyasına bakın.

---

## 🙏 Teşekkürler

- **DSPy Ekibi** - Devrim niteliğinde LLM programlama framework'ü
- **Cerebras** - Ultra-hızlı, maliyet-etkin çıkarım
- **NewsAPI** - Kapsamlı haber veri kaynağı

---

**Akıllı finansal analiz için ❤️ ile geliştirildi**

*Gold-Sense AI - Altın piyasası tahminini erişilebilir, şeffaf ve güvenilir kılıyor
1. **New Analysis Category:**
   - Update `Category` type in `models.py`
   - Add weight to `CATEGORY_WEIGHTS` in `engine.py`
   - Update signature instructions in `analyst.py`

2. **New Data Source:**
   - Create new fetcher class inheriting base pattern
   - Implement `fetch_news()` method
   - Add fallback logic in `app.py`

3. **Custom DSPy Signature:**
   - Define new `dspy.Signature` class
   - Add input/output fields with `desc`
   - Wrap in `dspy.ChainOfThought` for reasoning

---

## 📚 Additional Resources

- **DSPy Documentation:** [https://dspy-docs.vercel.app/](https://dspy-docs.vercel.app/)
- **Cerebras API:** [https://inference-docs.cerebras.ai/](https://inference-docs.cerebras.ai/)
- **NewsAPI Docs:** [https://newsapi.org/docs](https://newsapi.org/docs)
- **Streamlit Guide:** [https://docs.streamlit.io/](https://docs.streamlit.io/)

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- **DSPy Team** - Revolutionary LLM programming framework
- **Cerebras** - Ultra-fast, cost-effective inference
- **NewsAPI** - Comprehensive news data source

---

**Built with ❤️ for intelligent financial analysis**

*Gold-Sense AI - Making gold market forecasting accessible, transparent, and reliable.*
