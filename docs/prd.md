PROJE ÜRÜN GEREKSİNİM BELGESİ (PRD)

Proje Adı: Gold-Sense AI: Haber Odaklı Altın Piyasa Analiz ve Öngörü Sistemi

Versiyon: 1.0 (MVP)

Geliştirme Dili: Python 3.14+

Altyapı: Modüler, SOLID uyumlu, Genişletilebilir Yapı
1. Proje Özeti ve Amaç

Bu proje, küresel finans haberlerini (NewsAPI) ve anlık altın fiyat verilerini (yfinance) kullanarak, yapay zeka (Cerebras + DSPy) aracılığıyla altının kısa vadeli (haftalık) eğilimini analiz eden otonom bir karar destek sistemidir.

Temel Hedef: Binlerce haber içinden gürültüyü (NASA, Magazin vb.) ayıklayıp sadece piyasayı sarsacak makro-ekonomik ve jeopolitik haberleri süzmek, bunları puanlamak ve nihai bir "Piyasa Tansiyonu" raporu oluşturmaktır.
2. Hedef Kitle (Sunum)

Proje, akademik bir jüriye (Yüksek Lisans/Bitirme Tezi) sunulacak şekilde tasarlanmıştır. Bu nedenle:

    Hesap Verilebilirlik: Yapay zekanın her kararı (puanı) bir mantıksal gerekçeye (reasoning) dayanmalıdır.

    Hız: Cerebras NIM kullanımıyla "anlık" analiz kabiliyeti ispatlanmalıdır.

    Mühendislik Kalitesi: Kodun modülerliği ve dokümantasyonu ön planda olmalıdır.

3. Teknolojik Altyapı (Tech Stack)

    Dil: Python 3.14 (Gelecek nesil özelliklere uyumluluk).

    Çevre Yönetimi: venv (Sanal ortam zorunludur).

    Veri Kaynakları:

        NewsAPI: /v2/everything endpoint'i üzerinden finansal query'ler.

        yfinance: Güncel altın ons (GC=F) fiyat verisi.

    Yapay Zeka Katmanı:

        Cerebras NIM API: Yüksek hızlı model çıkarımı (Llama 3.x).

        DSPy: Prompt yazmak yerine "Programmatic Logic" (Signature) kullanımı.

    Arayüz: Streamlit (Dashboard ve grafik görselleştirme).

4. Fonksiyonel Gereksinimler (Modüller)
M1: Veri Toplama Modülü (NewsFetcher)

    NewsAPI üzerinden son 7 günlük haberleri çeker.

    Sorgu parametresi: (gold price OR XAU OR central banks OR inflation) AND (Fed OR Geopolitical).

    Haberlerin başlık (title), özet (description) ve yayın tarihini (publishedAt) temiz bir liste olarak döndürür.

M2: AI Analiz Modülü (GoldAnalyst) - DSPy Katmanı

    Persona: "Senior Financial Analyst & Geopolitics Expert".

    Akış: Gelen her haberi tek tek Cerebras üzerinden DSPy Signature yapısıyla işler.

    Çıktı Alanları (OutputFields):

        is_relevant (bool): Haber altınla alakalı mı?

        category (str): Macro, Geopolitical, Industrial veya Irrelevant.

        sentiment_score (int): 1-10 arası (1: Çok Ayı, 10: Çok Boğa).

        impact_reasoning (str): Neden bu puan verildi? (Kısa cümle).

M3: Piyasa Motoru (MarketEngine)

    Analiz edilen haberlerden "Irrelevant" olanları filtreler.

    Kalan haberlerin sentiment_score ortalamasını alır.

    Nihai Eğilim Hesabı: Eğer ortalama > 7 ise "Strong Bullish", < 4 ise "Bearish", arası ise "Neutral".

M4: Görselleştirme Modülü (Streamlit UI)

    Dashboard Üst Kısım: Mevcut Altın Fiyatı ve AI Haftalık Eğilim Skoru.

    Orta Kısım: Plotly kullanılarak çizilen "Haber Yoğunluğu vs Etki Puanı" grafiği.

    Alt Kısım: Haber kartları (Başlık + Puan + AI Gerekçesi).

5. Uygulama ve Yazılım Kuralları (Kritik)

    Venv Kurulumu: Proje başlamadan önce python -m venv venv ile ortam kurulmalı ve tüm bağımlılıklar requirements.txt dosyasında listelenmelidir.

    Modüler Yapı: Her modül kendi Python dosyasında (fetcher.py, analyst.py vb.) olmalıdır. Global bir main.py veya app.py bunları çağırmalıdır.

    Hata Yönetimi: API key eksikliği veya internet kesintisi gibi durumlarda sistem çökmemeli, kullanıcıya uyarı vermelidir.

    Hız Odaklılık: Haber analizleri asyncio veya paralel döngü ile yapılarak Cerebras'ın hızı maksimize edilmelidir.

    Geleceğe Hazırlık: Kod, ileride eklenecek olan "Haftalık Kendi Kendine Öğrenme" (Few-shot optimization) modülü için gerekli hook'lara (JSON loglama) sahip olmalıdır.

6. Örnek Veri Akış Senaryosu

    Haber: "Fed Başkanı faiz indirim sinyali verdi."

    AI Analiz: Relevant: Yes | Category: Macro | Score: 9 | Reasoning: "Lower rates increase gold's attractiveness."

    UI: Altın fiyatı grafiğinin yanına "Boğa Sinyali" damgası basılır.