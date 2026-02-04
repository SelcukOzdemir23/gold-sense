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
from goldsense.tonl import decode_news_articles, encode_news_articles


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


def _trend_tr(value: str) -> str:
    mapping = {
        "Strong Bullish": "Güçlü Boğa",
        "Bearish": "Ayı",
        "Neutral": "Nötr",
    }
    return mapping.get(value, value)


def _category_tr(value: str) -> str:
    mapping = {
        "Macro": "Makro",
        "Geopolitical": "Jeopolitik",
        "Industrial": "Endüstriyel",
        "Irrelevant": "Alakasız",
    }
    return mapping.get(value, value)


def _run_fetch_sync(fetcher: NewsFetcher) -> tuple[list[NewsArticle], dict]:
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


def _render_results(price, summary, results):
    # Strategic Summary (Phase-3)
    st.subheader("Stratejik Değerlendirme")
    
    confidence_pct = int(summary.confidence_average * 100)
    
    strategic_text = (
        f"**Piyasa Eğilimi:** {summary.trend} "
        f"(Ağırlıklı Skor: {summary.weighted_score:.1f}/10)\n\n"
        f"**Model Eminliği:** %{confidence_pct} "
        f"(Ortalama güven seviyesi)\n\n"
            f"**Analiz Kapsamı:** {summary.relevant_articles}/{summary.total_articles} haber "
        f"altın piyasasını etkiliyor. "
        f"Makro haberler (x1.5 ağırlık) diğer kategorilerden daha etkili sayılmıştır."
    )
    st.info(strategic_text)
    
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Handle None price gracefully
    if price is None:
        col1.metric("Altın Fiyatı", "Veri Yok")
    else:
        col1.metric("Altın Fiyatı", f"{price:.2f} USD")
    
    col2.metric("Eğilim", _trend_tr(summary.trend))
    col3.metric("Ort. Skor", f"{summary.average_score:.1f}/10")
    col4.metric("İlgili Haber", f"{summary.relevant_articles}/{summary.total_articles}")

    st.divider()

    relevant_results = [r for r in results if r.is_relevant]
    if relevant_results:
        top_results = sorted(relevant_results, key=lambda x: x.sentiment_score, reverse=True)[:5]
        st.subheader("Top 5 En Etkili Haber")
        for idx, item in enumerate(top_results, 1):
            with st.container(border=True):
                col_rank, col_content = st.columns([0.5, 9.5])
                col_rank.markdown(f"### #{idx}")
                col_content.markdown(f"**{item.article.title}**")
                col_content.write(item.article.description or "-")
                
                # Confidence badge
                conf_pct = int(item.confidence_score * 100)
                if item.confidence_score >= 0.8:
                    conf_symbol = "[High]"
                elif item.confidence_score >= 0.5:
                    conf_symbol = "[Med]"
                else:
                    conf_symbol = "[Low]"
                
                col_content.caption(
                    f"{_category_tr(item.category)} | "
                    f"Skor: **{item.sentiment_score}/10** | "
                    f"{conf_symbol} Güven: **%{conf_pct}** | "
                    f"{item.article.published_at.strftime('%d %b %H:%M')}"
                )
                col_content.write(f"*{item.impact_reasoning}*")
                
                # Show reasoning if available
                if item.reasoning:
                    with st.expander("AI Muhakeme Süreci"):
                        st.caption("Modelin bu sonuca nasıl vardığını görebilirsiniz:")
                        st.info(item.reasoning)

    st.divider()

    chart_data = pd.DataFrame(
        [
            {
                "title": r.article.title,
                "score": r.sentiment_score,
                "category": _category_tr(r.category),
                "published_at": r.article.published_at,
            }
            for r in results
            if r.is_relevant
        ]
    )

    if not chart_data.empty:
        fig = px.scatter(
            chart_data,
            x="published_at",
            y="score",
            color="category",
            hover_name="title",
            title="Haber Yoğunluğu vs Etki Puanı",
            labels={"score": "Etki Puanı (1-10)", "published_at": "Yayın Tarihi"},
        )
        fig.add_hline(
            y=7,
            line_dash="dash",
            line_color="green",
            annotation_text="Boğa Eşiği",
            annotation_position="right",
        )
        fig.add_hline(
            y=4,
            line_dash="dash",
            line_color="red",
            annotation_text="Ayı Eşiği",
            annotation_position="right",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("İlgili haber bulunamadı.")

    st.divider()
    st.subheader("Tüm İlgili Haberler")

    if relevant_results:
        sorted_results = sorted(relevant_results, key=lambda x: x.sentiment_score, reverse=True)

        categories = sorted(set(r.category for r in sorted_results))
        category_display = ["Tümü"] + [_category_tr(c) for c in categories]
        selected_category_display = st.selectbox(
            "Kategoriye göre filtrele:",
            category_display,
        )

        if selected_category_display == "Tümü":
            filtered = sorted_results
        else:
            rev_map = {
                "Makro": "Macro",
                "Jeopolitik": "Geopolitical",
                "Endüstriyel": "Industrial",
                "Alakasız": "Irrelevant",
            }
            selected_cat_en = rev_map.get(selected_category_display)
            filtered = [r for r in sorted_results if r.category == selected_cat_en]
        
        # Apply confidence filter
        filtered = [r for r in filtered if r.confidence_score >= confidence_threshold]

        for item in filtered:
            with st.container(border=True):
                st.markdown(f"**{item.article.title}**")
                st.write(item.article.description or "-")

                col_cat, col_score, col_conf, col_date = st.columns(4)
                col_cat.caption(f"{_category_tr(item.category)}")

                if item.sentiment_score >= 7:
                    score_color = "[High]"
                elif item.sentiment_score <= 4:
                    score_color = "[Low]"
                else:
                    score_color = "[Med]"
                col_score.caption(f"{score_color} Skor: **{item.sentiment_score}/10**")
                
                # Confidence badge
                conf_pct = int(item.confidence_score * 100)
                if item.confidence_score >= 0.8:
                    conf_color = "[High]"
                elif item.confidence_score >= 0.5:
                    conf_color = "[Med]"
                else:
                    conf_color = "[Low]"
                col_conf.caption(f"{conf_color} Güven: **%{conf_pct}**")
                
                col_date.caption(f"{item.article.published_at.strftime('%d %b %H:%M')}")

                st.write(f"*{item.impact_reasoning}*")
                
                # Show reasoning if available
                if item.reasoning:
                    with st.expander("AI Muhakeme Süreci"):
                        st.caption("Modelin bu sonuca nasıl vardığını görebilirsiniz:")
                        st.info(item.reasoning)
    else:
        st.info("İlgili haber bulunamadı.")


tab_fetch, tab_tonl, tab_analyze, tab_debug = st.tabs(
    ["Haber Hasadı", "TONL", "Analiz", "Debug"]
)

with tab_fetch:

    if st.button("Haberleri Getir", type="primary", key="fetch_news"):
        with st.spinner("Haberler çekiliyor..."):
            try:
                articles, payload = _run_fetch_sync(fetcher)
            except GoldSenseError as exc:
                st.error(f"Haber çekme hatası: {exc}")
                st.stop()

        st.session_state.raw_payload = payload
        Path("logs").mkdir(parents=True, exist_ok=True)
        (Path("logs") / "raw_news.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        st.success(f"{len(articles)} haber çekildi ve raw_news.json kaydedildi.")

    if st.session_state.raw_payload:
        st.caption("Ham JSON verisi (NewsAPI payload)")
        with st.expander("Ham JSON'u Gör"):
            st.json(st.session_state.raw_payload)
    else:
        st.info("Haberleri çekmek için butona bas.")

with tab_tonl:
    if not st.session_state.raw_payload:
        st.info("Önce 1. adımı tamamla (haberleri çek).")
    else:
        if st.button("TONL'e Çevir", type="primary", key="convert_tonl"):
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
                # Clear previous LM history to capture only this run
                analyst._configure_lm()
                
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
            _render_results(price, summary, results)
            
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
            st.info("Analizi başlatmak için butona bas.")

with tab_debug:
    if not st.session_state.lm_history:
        st.info("Henüz analiz yapılmadı. Önce 3. adımı (Analiz ve Rapor) tamamla.")
    else:
        st.success(f"{len(st.session_state.lm_history)} LM çağrısı kaydedildi (son 3 adet gösteriliyor)")
        
        for idx, call in enumerate(st.session_state.lm_history, 1):
            with st.expander(f"🔍 LM Çağrısı #{idx} - {call.get('model', 'unknown')}"):
                st.caption(f"Timestamp: {call.get('timestamp', 'N/A')}")
                
                # Show prompt/messages
                if 'messages' in call and call['messages']:
                    st.markdown("**Messages (Input):**")
                    for msg in call['messages']:
                        role = msg.get('role', 'unknown')
                        content = msg.get('content', '')
                        st.markdown(f"**{role.upper()}:**")
                        st.code(content[:500] + ('...' if len(content) > 500 else ''), language='text')
                
                # Show response
                if 'outputs' in call and call['outputs']:
                    st.markdown("**Response (Output):**")
                    for output in call['outputs']:
                        st.code(str(output)[:500] + ('...' if len(str(output)) > 500 else ''), language='text')
                
                # Show usage stats
                if 'usage' in call and call['usage']:
                    st.markdown("**Token Usage:**")
                    usage = call['usage']
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Prompt", usage.get('prompt_tokens', 'N/A'))
                    col2.metric("Completion", usage.get('completion_tokens', 'N/A'))
                    col3.metric("Total", usage.get('total_tokens', 'N/A'))
                    
                    if 'cost' in call and call['cost']:
                        st.metric("💵 Estimated Cost", f"${call['cost']:.6f}")

