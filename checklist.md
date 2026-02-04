# 🏆 Gold-Sense AI: Proje Tamamlama Checklist

## 1. Altyapı ve Hazırlık (Infrastructure)
* [x] **Python 3.11** ortamının aktif olduğunu ve `venv` sanal ortamının kullanıldığını doğrula.
* [x] Tüm bağımlılıkların (`dspy-ai`, `httpx`, `yfinance`, `streamlit`, `plotly`) `requirements.txt` dosyasında listelendiğinden ve yüklendiğinden emin ol.
* [x] `.env` dosyasında `NEWSAPI_KEY`, `CEREBRAS_API_KEY` ve `TRUNCGIL_URL` bilgilerinin tanımlı olduğunu kontrol et.
* [x] Proje klasör yapısının ( `src/`, `logs/`, `docs/`) modüler mimariye uygun olduğunu doğrula.

---

## 2. Adım Adım Streamlit Arayüzü (The Journey UI) ✅ FAZ-1 TAMAMLANDI
### Adım 1: Haber Hasadı (Data Fetching)
* [x] **Haber Getir Butonu:** `NewsFetcher` modülünü tetikleyerek NewsAPI üzerinden son 50 haberi çekmeli.
* [x] **Ham Veri Görünümü:** Gelen haberlerin ham JSON formatını `st.expander` içinde jüriye göster.
* [x] **Yerel Kayıt:** Çekilen verileri `logs/raw_news.json` olarak sisteme işle.

### Adım 2: TONL Optimizasyonu (Token Efficiency)
* [x] **TONL Çevirici:** Kendi yazdığın Python scripti ile JSON verisini TONL formatına dönüştür.
* [x] **Görsel Karşılaştırma:** Streamlit ekranında JSON ve TONL metinlerini yan yana göstererek farkı vurgula.
* [x] **Tasarruf Metriği:** JSON ve TONL karakter sayılarını karşılaştırarak yüzdesel token kazancını (%40+ hedef) raporla.
* [x] **Yerel Kayıt:** Çevrilen veriyi `logs/news.tonl` olarak sakla.

### Adım 3: DSPy & LLM Analiz Süreci
* [x] **Analizi Başlat Butonu:** TONL verisini `GoldAnalyst` modülüne göndererek Cerebras üzerinden işlemeli.
* [ ] **Canlı İzleme:** `dspy.inspect_history(n=1)` çıktısını bir "Debug Console" gibi arayüzde göstererek modelin arka planını ispatla.
* [x] **Haber Kartları:** Analiz edilen haberleri; Kategori, 1-10 Puan, Boğa/Ayı İkonu ve **Türkçe Gerekçe** ile listele.

---

## 3. DSPy "Zeka" ve Optimizasyon Katmanı ✅ FAZ-2 TAMAMLANDI
* [x] **Chain of Thought (CoT):** `dspy.Predict` yerine `dspy.ChainOfThought` kullanarak modelin adım adım düşünmesini sağla.
* [x] **Gelişmiş Signature:** Çıktı alanlarının (`is_relevant`, `severity_score`, `impact_reasoning`) açıklamalarını (desc) netleştir.
* [x] **Assertions (Doğrulama):** `dspy.Assert` ile skorun 1-10 arası olmasını ve gerekçenin Türkçe olmasını zorunlu kıl.
* [x] **Usage Tracking:** `track_usage=True` yaparak toplam token harcamasını ve maliyet analizini dashboard'a ekle.
* [x] **Debug Console:** `dspy.inspect_history()` benzeri LM history görüntüleme tab'ı eklendi.

---

## 4. Hesap Verilebilirlik ve Metrikler (Accountability)
* [ ] **Deduplication:** Aynı habere (URL bazlı) sahip mükerrer kayıtların `analysis.jsonl` dosyasına yazılmasını engelle.
* [ ] **Ragas Entegrasyonu:** Modelin haber metnine sadakatini (`Faithfulness`) ölçen küçük bir test seti oluştur.
* [ ] **Güven Skoru (Confidence):** Modelden analizleri için 0-1 arası bir "Eminlik Puanı" iste ve bunu görselleştir.
* [ ] **Nihai Eğilim Kararı:** Haftalık ağırlıklı ortalamayı hesaplayan (Makro x 1.5 gibi) motoru mühürle.

---

## 5. Sağlamlık ve Hata Yönetimi (Robustness)
* [ ] **Sayı Formatı Temizliği:** Truncgil'den gelebilecek virgüllü (`2.500,50`) fiyatları float'a çeviren logic'i test et.
* [ ] **Fallback Mekanizması:** Truncgil servisi hata verdiğinde `binance`'in otomatik olarak devreye girdiğini doğrula.
* [ ] **Async Performance:** 50 haberi `asyncio.Semaphore` ile Cerebras'a gönderirken hızın 5 saniyenin altında olduğunu teyit et.

---

## 6. Sunum Materyalleri (The Grand Finale)
* [ ] **PRD ve README:** Hazırladığımız PRD'yi ve kurulum talimatlarını içeren README dosyasını hazırla.
* [ ] **Mühendislik Sunumu:** "Neden TONL?" ve "Neden DSPy?" sorularına token tasarrufu ve modülerlik üzerinden cevap verecek slaytları hazırla.