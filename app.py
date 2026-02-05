from __future__ import annotations

import asyncio
import json
import sys
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import dspy
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
SRC_PATH = ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

from goldsense.analyst import GoldAnalyst
from goldsense.config import Settings
from goldsense.engine import MarketEngine
from goldsense.exceptions import ConfigError, GoldSenseError
from goldsense.fetcher import NewsFetcher
from goldsense.logger import JsonlLogger
from goldsense.models import NewsArticle
from goldsense.price import GoldPriceService
from goldsense.tonl import decode_news_articles, encode_news_articles, encode_tonl, decode_tonl


st.set_page_config(page_title="Gold-Sense AI", layout="wide")

st.title("Gold-Sense AI")
st.caption("Finansal Haber Analizi - Altın Piyasası Tahmin Sistemi")

load_dotenv()
settings = Settings.from_env()

with st.sidebar:
    st.header("Ayarlar")
    confidence_threshold = st.slider(
        "Minimum Güven Seviyesi",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1,
        help="Sadece bu seviye ve üzerindeki güven skorlu haberleri göster"
    )
    st.caption(f"Gösterilecek: %{int(confidence_threshold * 100)}+ güven")

try:
    settings.validate()
except ConfigError as exc:
    st.error(f"Config error: {exc}")
    st.stop()

effective_settings = replace(settings)

# --- GLOBAL DSPY CONFIGURATION (Dependency Injection Root) ---
try:
    lm = dspy.LM(
        f"openai/{effective_settings.cerebras_model}",
        api_key=effective_settings.cerebras_api_key,
        api_base=effective_settings.cerebras_api_base,
        temperature=effective_settings.analysis_temperature,
        cache=False,  # Disable cache for fresh results
    )
    dspy.configure(lm=lm, track_usage=True)
except Exception as exc:
    st.error(f"Global LM Configuration Failed: {exc}")
    st.stop()

from goldsense import ui

fetcher = NewsFetcher(effective_settings)
analyst = GoldAnalyst(effective_settings)
engine = MarketEngine()

price_service = GoldPriceService(effective_settings)
logger = JsonlLogger(path=Path("logs/analysis.jsonl"))

if "raw_payload" not in st.session_state:
    st.session_state.raw_payload = None
if "tonl_text" not in st.session_state:
    st.session_state.tonl_text = None
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "lm_history" not in st.session_state:
    st.session_state.lm_history = None
if "token_usage" not in st.session_state:
    st.session_state.token_usage = None


def _run_fetch_sync(fetcher: NewsFetcher) -> tuple[list[NewsArticle], dict]:
    """Sync wrapper for async news fetching"""
    return asyncio.run(fetcher.fetch_latest_with_payload())


def _run_analysis_sync(analyst: GoldAnalyst, articles: list[NewsArticle]):
    return asyncio.run(analyst.analyze_articles(articles))


def _to_article(item: dict) -> NewsArticle:
    published_raw = item.get("published_at") or item.get("publishedAt")
    if isinstance(published_raw, str) and published_raw:
        try:
            published_at = datetime.fromisoformat(published_raw.replace("Z", "+00:00"))
        except ValueError:
            published_at = datetime.now(timezone.utc)
    else:
        published_at = datetime.now(timezone.utc)

    return NewsArticle(
        title=(item.get("title") or "").strip(),
        description=(item.get("description") or "").strip(),
        published_at=published_at,
        source=item.get("source"),
        url=item.get("url"),
    )


tab_fetch, tab_tonl, tab_analyze, tab_curiosity = st.tabs(
    ["Haber Hasadı", "TONL", "Analiz", "Performans"]
)

with tab_fetch:
    st.subheader("📰 Haber Hasadı")
    st.caption("NewsAPI'den altın ile ilgili son haberleri çeker")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("📥 Haberleri Getir", type="primary", key="fetch_news", use_container_width=True):
            with st.spinner("🔄 Haberler çekiliyor..."):
                try:
                    articles, payload = _run_fetch_sync(fetcher)
                except GoldSenseError as exc:
                    st.error(f"❌ Haber çekme hatası: {exc}")
                    st.stop()

            st.session_state.raw_payload = payload
            Path("logs").mkdir(parents=True, exist_ok=True)
            (Path("logs") / "raw_news.json").write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            
            # Success metrics
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("📊 Çekilen Haber", len(articles))
            col_b.metric("📅 Tarih Aralığı", f"{settings.lookback_days} gün")
            col_c.metric("💾 Dosya", "raw_news.json")
            
            st.success(f"✅ {len(articles)} haber başarıyla çekildi!")
    
    with col2:
        if st.session_state.raw_payload:
            total_articles = len(st.session_state.raw_payload.get("articles", []))
            st.metric("📈 Toplam", total_articles)
            st.caption("Çekilen haber sayısı")

    if st.session_state.raw_payload:
        st.divider()
        
        # Quick preview of articles
        articles = st.session_state.raw_payload.get("articles", [])
        if articles:
            st.subheader("🔍 Haber Önizleme")
            
            # Show first 3 articles as preview
            for i, article in enumerate(articles[:3]):
                with st.container(border=True):
                    st.markdown(f"**{article.get('title', 'Başlık yok')}**")
                    st.caption(f"📰 {article.get('source', {}).get('name', 'Bilinmeyen kaynak')} | "
                             f"📅 {article.get('publishedAt', 'Tarih yok')[:10]}")
                    if article.get('description'):
                        st.write(article['description'][:150] + "..." if len(article.get('description', '')) > 150 else article['description'])
            
            if len(articles) > 3:
                st.caption(f"... ve {len(articles) - 3} haber daha")
        
        st.divider()
        st.caption("🔧 Ham JSON verisi (NewsAPI payload)")
        with st.expander("📋 Ham JSON'u Gör", expanded=False):
            st.json(st.session_state.raw_payload)
    else:
        st.info("👆 Haberleri çekmek için yukarıdaki butona tıklayın.")

with tab_tonl:
    subtab_news, subtab_playground = st.tabs(["📰 Haber Dönüştürücü", "🎮 Playground"])
    
    with subtab_news:
        if not st.session_state.raw_payload:
            st.info("Önce 1. adımı tamamla (haberleri çek).")
        else:
            if st.button("TONL'e Çevir (Haberler)", type="primary", key="convert_tonl_news"):
                raw_articles = st.session_state.raw_payload.get("articles", [])
                tonl_text = encode_news_articles(raw_articles)
                st.session_state.tonl_text = tonl_text

                Path("logs").mkdir(parents=True, exist_ok=True)
                (Path("logs") / "news.tonl").write_text(tonl_text, encoding="utf-8")

            if st.session_state.tonl_text:
                raw_articles = st.session_state.raw_payload.get("articles", [])
                json_text = json.dumps(raw_articles, ensure_ascii=False)
                tonl_text = st.session_state.tonl_text

                json_chars = len(json_text)
                tonl_chars = len(tonl_text)
                savings = (1 - (tonl_chars / json_chars)) * 100 if json_chars else 0

                col1, col2, col3 = st.columns(3)
                col1.metric("JSON Karakter", f"{json_chars}")
                col2.metric("TONL Karakter", f"{tonl_chars}")
                col3.metric("Tasarruf", f"%{savings:.1f}")

                col_json, col_tonl = st.columns(2)
                with col_json:
                    st.caption("JSON (Ham)")
                    with st.expander("Tıkla: JSON Formatını Göster", expanded=False):
                        st.code(json.dumps(raw_articles, ensure_ascii=False, indent=2), language="json")
                with col_tonl:
                    st.caption("TONL (Optimize)")
                    with st.expander("Tıkla: TONL Formatını Göster", expanded=False):
                        st.code(tonl_text, language="text")
            else:
                st.info("TONL dönüşümü için butona bas.")

    with subtab_playground:
        st.subheader("🛠️ TONL Playground")
        st.caption("Genel amaçlı JSON <-> TONL dönüştürücü. Haberlerden bağımsız test edebilirsiniz.")
        
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            st.markdown("### JSON -> TONL")
            pg_json_input = st.text_area("JSON Verisi Giriniz:", height=300, placeholder='{"key": "value", "list": [1, 2]}')
            
            if st.button("Encode to TONL", key="pg_encode"):
                if not pg_json_input.strip():
                    st.warning("Lütfen JSON verisi girin.")
                else:
                    try:
                        data = json.loads(pg_json_input)
                        encoded = encode_tonl(data)
                        
                        chars_j = len(pg_json_input)
                        chars_t = len(encoded)
                        sav = (1 - (chars_t / chars_j)) * 100 if chars_j else 0
                        
                        st.success(f"Dönüştürüldü! Tasarruf: %{sav:.1f}")
                        st.code(encoded, language="text")
                    except json.JSONDecodeError as e:
                        st.error(f"Geçersiz JSON: {e}")
                    except Exception as e:
                        st.error(f"Hata: {e}")

        with col_p2:
            st.markdown("### TONL -> JSON")
            pg_tonl_input = st.text_area("TONL Verisi Giriniz:", height=300, placeholder='#version 1.0\nroot:\n  key: "value"')
            
            if st.button("Decode to JSON", key="pg_decode"):
                if not pg_tonl_input.strip():
                    st.warning("Lütfen TONL verisi girin.")
                else:
                    try:
                        decoded = decode_tonl(pg_tonl_input)
                        st.success("Dönüştürüldü!")
                        st.json(decoded)
                    except Exception as e:
                        st.error(f"Hata: {e}")

with tab_analyze:
    if not st.session_state.tonl_text:
        st.info("Önce 2. adımı tamamla (TONL'e çevir).")
    else:
        if st.button("Analizi Başlat", type="primary", key="run_analysis"):
            # STEP 1: Fetch gold price first (non-blocking)
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Altın fiyatı sorgulanıyor...")
            progress_bar.progress(10)
            
            price = price_service.get_current_price()
            
            if price is None:
                st.warning("Altın fiyat bilgisi alınamadı (Truncgil/Binance yanıt vermedi). Analiz devam ediyor...")
            else:
                st.success(f"✅ Güncel altın fiyatı: **${price:.2f}**")
            
            progress_bar.progress(20)
            
            # STEP 2: Parse TONL
            status_text.text("📄 TONL verisi decode ediliyor...")
            tonl_items = decode_news_articles(st.session_state.tonl_text)
            articles = [_to_article(item) for item in tonl_items]
            progress_bar.progress(30)
            
            # STEP 3: Run analysis with progress updates
            status_text.text(f"{len(articles)} haber DSPy ile analiz ediliyor...")
            try:
                
                # Analyze articles (this is the heavy operation)

                results = _run_analysis_sync(analyst, articles)
                progress_bar.progress(80)
                
                # Log results
                status_text.text("💾 Sonuçlar kaydediliyor...")
                for result in results:
                    logger.log(result)
                progress_bar.progress(90)

                # Generate summary
                status_text.text("Özet rapor oluşturuluyor...")
                summary = engine.summarize(results)
                
                # Capture LM history and usage for debug console
                lm = dspy.settings.lm
                st.session_state.lm_history = lm.history[-min(3, len(lm.history)):] if lm.history else []
                
                # Get token usage from last result if available
                if results:
                    # Store token usage info
                    st.session_state.token_usage = {
                        'total_calls': len(results),
                        'history_count': len(lm.history) if lm.history else 0
                    }
                
                progress_bar.progress(100)
                status_text.text("✅ Tamamlandı!")
                
            except GoldSenseError as exc:
                st.error(f"Çalıştırma hatası: {exc}")
                st.stop()

            st.session_state.analysis = (price, summary, results)
            st.success("✅ Analiz tamamlandı! Aşağıda sonuçları görebilirsin.")
            st.rerun()  # Refresh to show results

        if st.session_state.analysis:
            price, summary, results = st.session_state.analysis
            ui.render_results(price, summary, results, confidence_threshold)
            
            # Token Usage Summary
            if st.session_state.token_usage:
                st.divider()
                st.subheader("Token Kullanım İstatistikleri")
                col1, col2 = st.columns(2)
                col1.metric("Toplam LM Çağrısı", st.session_state.token_usage.get('total_calls', 0))
                col2.metric("History Kayıt Sayısı", st.session_state.token_usage.get('history_count', 0))
                
                # Show usage details if available
                lm = dspy.settings.lm
                if hasattr(lm, 'history') and lm.history:
                    st.caption("Son LM çağrısı detayları:")
                    last_call = lm.history[-1]
                    if 'usage' in last_call and last_call['usage']:
                        usage_data = last_call['usage']
                        col_a, col_b, col_c = st.columns(3)
                        col_a.metric("Prompt Tokens", usage_data.get('prompt_tokens', 'N/A'))
                        col_b.metric("Completion Tokens", usage_data.get('completion_tokens', 'N/A'))
                        col_c.metric("Total Tokens", usage_data.get('total_tokens', 'N/A'))
        else:
            # Informative onboarding panel
            st.markdown("### 🎯 Hoşgeldiniz - Sistem Rehberi")
            
            with st.container(border=True):
                st.markdown("""
                **Amaç:**  
                Bu sistem, küresel finans haberlerinin **altın piyasaları** üzerindeki olası etkilerini yapay zeka ile analiz eder.
                Haberleri okuyup puanlayarak, piyasanın hangi yönde hareket edebileceğini tahmin eder.
                
                ---
                
                **📊 Eğilim Terimleri:**
                
                - 🟢 **Güçlü Boğa (Strong Bullish):** Altın fiyatlarında **güçlü yükseliş** beklentisi.  
                  *Örnek: "Fed faiz indirdi" haberi → Altın talebi artar → Fiyat yükselir.*
                
                - 🔴 **Ayı (Bearish):** Altın fiyatlarında **düşüş** beklentisi.  
                  *Örnek: "Güçlü istihdam verisi" → Fed faizleri yüksek tutar → Altın çekiciliği azalır.*
                
                - ⚪ **Nötr (Neutral):** Piyasada **yatay seyir** veya belirgin bir etki yok.  
                  *Örnek: Altınla doğrudan ilgisi olmayan teknoloji haberleri.*
                
                ---
                
                **⚙️ Sistem Nasıl Çalışır?**
                
                1. **Haber Analizi:** AI (Llama-3 70B) her haberi okur ve 1-10 arası puan verir.
                2. **Ağırlıklı Değerlendirme:** Makro haberler (Fed kararları, enflasyon) daha yüksek ağırlık alır.
                3. **Trend Tahmini:** Tüm skorlar birleştirilerek genel piyasa eğilimi belirlenir.
                4. **Açıklama:** Model sadece sonuç vermez, *neden* bu karara vardığını da açıklar (Chain-of-Thought).
                
                ---
                
                ⚠️ **Not:** Bu analiz sadece bilgilendirme amaçlıdır. Yatırım tavsiyesi değildir.
                """)
            
            st.info("👆 Hazır olduğunda yukarıdaki butona basarak analizi başlatabilirsin.")

with tab_curiosity:
    # Use global session state token usage if available
    usage_data = st.session_state.token_usage if "token_usage" in st.session_state else None
    lm_history_data = st.session_state.lm_history if "lm_history" in st.session_state else None
    ui.render_performance_tab(lm_history_data, usage_data)

