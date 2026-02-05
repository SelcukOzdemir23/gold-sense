from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st
import dspy

from .models import MarketSummary, AnalysisResult

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

def render_results(price: float | None, summary: MarketSummary, results: list[AnalysisResult], confidence_threshold: float):
    # ... (Existing code kept as is, but focusing on new function below)
    # Strategic Summary
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
        # Top 5 Section
        top_results = sorted(relevant_results, key=lambda x: x.sentiment_score, reverse=True)[:5]
        st.subheader("Top 5 En Etkili Haber")
        for idx, item in enumerate(top_results, 1):
            _render_article_card(item, rank=idx)

    st.divider()

    # Chart Section
    _render_chart(results)

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
            filtered = [r for r in sorted_results if _category_tr(r.category) == selected_category_display]
        
        # Apply confidence filter
        filtered = [r for r in filtered if r.confidence_score >= confidence_threshold]

        for item in filtered:
            _render_article_card(item)
    else:
        st.info("İlgili haber bulunamadı.")

def _render_article_card(item: AnalysisResult, rank: int | None = None):
    with st.container(border=True):
        if rank:
            col_rank, col_content = st.columns([0.5, 9.5])
            col_rank.markdown(f"### #{rank}")
            container = col_content
        else:
            container = st
            
        container.markdown(f"**{item.article.title}**")
        container.write(item.article.description or "-")
        
        # Badges
        col_cat, col_score, col_conf, col_date = container.columns(4)
        col_cat.caption(f"{_category_tr(item.category)}")

        # Score badge
        if item.sentiment_score >= 7:
            score_color = ":green[High]"
        elif item.sentiment_score <= 4:
            score_color = ":red[Low]"
        else:
            score_color = ":orange[Med]"
        col_score.caption(f"{score_color} Skor: **{item.sentiment_score}/10**")
        
        # Confidence badge
        conf_pct = int(item.confidence_score * 100)
        if item.confidence_score >= 0.8:
            conf_color = ":green[High]"
        elif item.confidence_score >= 0.5:
            conf_color = ":orange[Med]"
        else:
            conf_color = ":red[Low]"
        col_conf.caption(f"{conf_color} Güven: **%{conf_pct}**")
        
        col_date.caption(f"{item.article.published_at.strftime('%d %b %H:%M')}")

        container.write(f"*{item.impact_reasoning}*")
        
        if item.reasoning:
            with container.expander("AI Muhakeme Süreci"):
                st.caption("Modelin bu sonuca nasıl vardığını görebilirsiniz:")
                st.info(item.reasoning)

def _render_chart(results: list[AnalysisResult]):
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
        st.info("Grafik oluşturulacak veri yok.")

def render_performance_tab(lm_history: list | None, token_usage: dict | None):
    """
    Renders detailed performance metrics and DSPy prompt inspection.
    Uses persisted session state data instead of volatile dspy.settings.lm.
    """
    st.subheader("🚀 Sistem Performansı & DSPy Optimizasyonu")
    
    if not lm_history:
        st.info("Henüz analiz yapılmadı. Lütfen 'Analiz' sekmesinden bir işlem başlatın.")
        return

    # 1. Token Metrics
    st.markdown("### 📊 Token ve Maliyet Analizi")
    
    last_call = lm_history[-1]
    # Try to find usage in last call or use accumulated stats
    usage = last_call.get('usage', {})
    if not usage and token_usage:
         # Fallback to session accumulated data if raw call doesn't have it
         pass 

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Toplam Çağrı", len(lm_history))
    col2.metric("Prompt Token", usage.get('prompt_tokens', 'N/A'))
    col3.metric("Completion Token", usage.get('completion_tokens', 'N/A'))
    col4.metric("Model", last_call.get('model', 'Unknown'))

    st.divider()

    # 2. Prompt Optimization Inspector
    st.markdown("### 🧠 DSPy Prompt Inspector (Few-Shot Learning)")
    st.caption("Modelin 'Train' edilmesi için kullanılan dinamik prompt yapısı. Few-Shot örneklerinin nasıl enjekte edildiğini buradan görebilirsiniz.")

    # Extract the actual prompt sent to the model
    # Usually in 'messages' for chat models
    messages = last_call.get('messages', [])
    
    if messages:
        # User message usually contains the compiled prompt with examples
        for msg in messages:
            role = msg.get('role', '').upper()
            content = msg.get('content', '')
            
            # Simple highlighting for DSPy sections
            if "---" in content:
                st.markdown(f"#### {role} Mesajı (Compiled Context)")
                
                parts = content.split("---")
                
                st.markdown("**1. Görev Talimatı (Signature Instructions):**")
                st.code(parts[0].strip(), language="text")
                
                if len(parts) > 2:
                    st.markdown(f"**2. Few-Shot Örnekleri ({len(parts)-2} Adet Enjekte Edildi):**")
                    with st.expander("Örnekleri İncele (Eğitim Verisi)", expanded=True):
                        examples_text = "\n---\n".join(parts[1:-1])
                        st.code(examples_text, language="text")
                
                st.markdown("**3. Mevcut Görev (Input):**")
                st.code(parts[-1].strip(), language="text")
                
            else:
                with st.expander(f"{role} Mesajı", expanded=False):
                    st.code(content, language="text")
    else:
        st.warning("Prompt geçmişi okunamadı (Non-Chat model formatı olabilir).")

    st.divider()
    
    # 3. Raw Response Validation
    with st.expander("🛠️ Ham Model Çıktısı (Raw Response)"):
        st.json(last_call)
