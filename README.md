# Gold-Sense AI 🟡

**Finansal Haber Analizi ve Altın Piyasası Tahmin Sistemi**

[**🚀 CANLI DEMO**](https://gold-sense-cerebras.streamlit.app/) | [**📂 GitHub Repository**](https://github.com/SelcukOzdemir23/gold-sense)

---

## 🎓 Proje Hakkında
Bu proje, **Yapay Zeka Destekli Finansal Analiz** üzerine yapılan bir **Yüksek Lisans Tezi/Projesi** kapsamında geliştirilmiştir.

Amacı, doğal dil işleme (NLP) ve modern **Prompt Engineering** tekniklerini kullanarak, küresel finans haberlerinin altın piyasaları üzerindeki olası etkilerini (Bullish/Bearish/Neutral) otomatik olarak analiz etmek ve stratejik içgörüler sunmaktır.

Proje, geleneksel "Sentiment Analysis"ten (Duygu Analizi) öteye geçerek, **DSPy** kütüphanesi ile "Reasoning" (Muhakeme) yeteneği kazandırılmış bir ajan mimarisi sunar.

---

## 🏗️ Sistem Mimarisi ve Akış

Sistem 4 ana modülden oluşur:

1.  **Haber Hasadı (News Harvest):** `NewsAPI` üzerinden altın, Fed, jeopolitik vb. anahtar kelimelerle son haberler çekilir.
2.  **Veri Optimizasyonu (TONL):** Çekilen haberler, JSON yerine **TONL (Table Oriented Notation Language)** formatına dönüştürülerek LLM token maliyeti %30-%50 oranında düşürülür.
3.  **Akıllı Analiz (DSPy Engine):** **Cerebras (Llama 3 70B)** modeli, **Few-Shot Learning** tekniğiyle eğitilmiş bir `ChainOfThought` modülü üzerinden haberleri analiz eder. Model sadece skor vermekle kalmaz, *neden* bu kararı verdiğini de Türkçe olarak açıklar.
4.  **Stratejik Raporlama:** Analiz sonuçları ağırlıklı ortalamalarla birleştirilir ve **Canlı Altın Fiyatı (Truncgil/Binance API)** ile birlikte sunularak "Güçlü Boğa", "Ayı" veya "Nötr" piyasa tahmini yapılır.

---

## 🛠️ Kullanılan Teknolojiler

*   **LLM Engine:** [Cerebras Inference](https://cerebras.net/) (Llama-3-70b-Instruct ile ışık hızında analiz)
*   **Prompt Optimization:** [DSPy](https://dspy.ai/) (Declarative Self-improving Language Programs)
*   **Data Format:** [TONL](https://github.com/tonl-lang/tonl) (Table Oriented Notation Language - Token tasarruflu veri formatı)
*   **Frontend:** [Streamlit](https://streamlit.io/)
*   **Data Source:** [NewsAPI](https://newsapi.org/) (Haberler) & [Binance API](https://www.binance.com/) (Canlı Fiyat)
*   **Visualization:** [Plotly](https://plotly.com/python/)

---

## 📂 Önemli Dosyalar

*   `app.py`: Uygulamanın giriş noktası ve UI orkestrasyonu.
*   `src/goldsense/analyst.py`: DSPy tabanlı analiz motoru. Few-shot örneklerini yükler ve Llama-3 modelini yönetir.
*   `src/goldsense/examples.py`: Modele "nasıl düşünmesi gerektiğini" öğreten eğitim seti (Few-Shot Examples).
*   `src/goldsense/tonl.py`: JSON <-> TONL dönüşümünü yapan, multiline-string destekli özel parser.
*   `src/goldsense/engine.py`: Analiz sonuçlarını (skorları) ağırlıklandırıp piyasa trendini belirleyen matematiksel motor.
*   `src/goldsense/price.py`: Altın fiyatlarını Truncgil veya Binance üzerinden çeken yedekli servis.

---

## 🧠 DSPy ve Prompt Optimizasyonu

Bu projede "Hard-coded" promptlar yerine DSPy'ın **Optimizer** (Teleprompter) mimarisi kullanılmıştır.
Sistem, `src/goldsense/examples.py` içindeki uzman görüşlerini (Fed faiz kararı, savaş riski vb.) alır ve bunları modele "Context" olarak öğretir.

Bu sayede model:
*   *"Savaş çıktı"* haberine -> **(Reasoning: Güvenli liman talebi artar)** -> "Pozitiftir" diyebilir.
*   *"İstihdam güçlü geldi"* haberine -> **(Reasoning: Faiz indirimi zorlaşır)** -> "Negatiftir" diyebilir.

Sistem, **Chain-of-Thought (CoT)** tekniği sayesinde sadece sonucu değil, bu sonuca götüren mantıksal zinciri de üretir.

*Bunu canlı sistemde **Performans** sekmesinden inceleyebilirsiniz.*

---

## ⚠️ Yasal Uyarı (Disclaimer)

**Bu proje sadece eğitim ve akademik araştırma amaçlıdır.**
Burada üretilen analizler, tahminler ve skorlar **Yatırım Tavsiyesi Değildir (YTD)**. Finansal piyasalar yüksek risk içerir. Yatırım kararlarınızı kendi araştırmanıza veya lisanslı bir yatırım danışmanına dayanarak veriniz.

---

*Geliştirici: Selçuk Özdemir*
