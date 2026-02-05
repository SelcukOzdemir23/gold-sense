from dspy import Example

# Few-Shot Examples for Gold Analysis
# Features explicit 'rationale' (Chain of Thought) to guide the model's reasoning process.

TRAINING_SET = [
    # --- MACRO EKONOMİK (Bullish - Faiz İndirimi) ---
    Example(
        title="Fed Cuts Interest Rates by 25 Basis Points, Signals End of Tightening",
        description="The Federal Reserve announced a 0.25% rate cut today, citing cooling inflation and a softening labor market. Chairman Powell hinted that further cuts could follow in 2024.",
        is_relevant="True",
        rationale="Fed rates have a direct inverse correlation with gold prices. A rate cut lowers the opportunity cost of holding non-yielding bullion and weakens the USD. The signal of 'end of tightening' suggests a prolonged period of favorable conditions.",
        category="Macro",
        sentiment_score="9",
        impact_reasoning="Fed'in faiz indirimine gitmesi ve gevşeme sinyali vermesi, dolar endeksini (DXY) zayıflatır ve ABD tahvil getirilerini düşürür. Getirisi olmayan altının fırsat maliyeti azaldığı için bu durum fiyatlarda güçlü bir yükseliş trendi başlatır.",
        confidence_score="0.95"
    ).with_inputs("title", "description"),

    # --- MACRO EKONOMİK (Bearish - Güçlü İstihdam) ---
    Example(
        title="US Non-Farm Payrolls Smash Expectations: 350k Jobs Added",
        description="The latest jobs report shows the US economy added 350,000 jobs last month, far exceeding the 180,000 forecast. Unemployment dipped to 3.4%.",
        is_relevant="True",
        rationale="Strong employment data implies a robust economy, giving the Fed room to keep interest rates higher for longer to combat inflation. Higher rates strengthen the USD and increase bond yields, which is bearish for gold.",
        category="Macro",
        sentiment_score="2",
        impact_reasoning="Beklentilerin çok üzerinde gelen tarım dışı istihdam verisi, ekonominin hala çok sıcak olduğunu gösterir. Bu durum Fed'in faizleri 'daha uzun süre yüksek' tutacağı beklentisini artırır, doları güçlendirir ve altın üzerinde ciddi satış baskısı yaratır.",
        confidence_score="0.90"
    ).with_inputs("title", "description"),

    # --- JEOPOLİTİK (Bullish - Güvenli Liman) ---
    Example(
        title="Russia-Ukraine Conflict Escalates: Missiles Strike Kyiv",
        description="Tensions reached a new high as missile strikes were reported in the capital. Global leaders warn of broader conflict risks involving NATO supply lines.",
        is_relevant="True",
        rationale="War and geopolitical instability increase global risk aversion. Investors flee from riskier assets like stocks to 'safe haven' assets like gold. The involvement of NATO supply lines hints at further escalation.",
        category="Geopolitical",
        sentiment_score="8",
        impact_reasoning="Savaş riskinin artması ve çatışmanın yayılma ihtimali, piyasalarda korku endeksini yükseltir. Yatırımcılar riskli varlıklardan kaçıp 'güvenli liman' (safe-haven) varlığı olan altına sığınır. Jeopolitik risk primi fiyatlara eklenir.",
        confidence_score="0.85"
    ).with_inputs("title", "description"),

    # --- MERKEZ BANKALARI (Bullish - Uzun Vadeli Talep) ---
    Example(
        title="China's Central Bank Adds Gold Reserves for 18th Consecutive Month",
        description="The PBOC reported buying another 10 tons of gold in March, continuing its diversification away from US dollar assets.",
        is_relevant="True",
        rationale="Central bank buying is a fundamental driver of demand. Continuous purchasing by PBOC signals a strategic shift away from USD (de-dollarization), creating a strong price floor for gold.",
        category="Macro",
        sentiment_score="8",
        impact_reasoning="Dünyanın en büyük merkez bankalarından birinin rezervlerini sürekli artırması (Dedolarizasyon), altına olan fiziksel talebin güçlü kaldığını gösterir. Bu durum piyasaya taban fiyat (floor) desteği sağlar ve uzun vadeli boğa trendini destekler.",
        confidence_score="0.90"
    ).with_inputs("title", "description"),

    # --- ALAKASIZ (Irrelevant) ---
    Example(
        title="Bitcoin ETFs See Record Inflows as Ether Surge Continues",
        description="Crypto markets are rallying with Bitcoin breaking $70k. Investors are excited about the new institutional adoption via ETFs.",
        is_relevant="False",
        rationale="While crypto is sometimes called 'digital gold', its price action is driven by different factors (tech adoption, liquidity). A rally in crypto does not mechanistically force gold prices up or down.",
        category="Irrelevant",
        sentiment_score="5",
        impact_reasoning="Kripto para piyasalarındaki hareketlilik bazen likidite geçişi yaratsa da, bu haberin doğrudan altın fiyatlarını etkileyecek bir mekanizması yoktur. Altın ve Bitcoin farklı dinamiklerle (dijital vs fiziksel değer saklama) çalışır.",
        confidence_score="0.95"
    ).with_inputs("title", "description"),

    # --- ENDÜSTRİYEL (Nötr/Bullish) ---
    Example(
        title="Strike at World's Largest Gold Mine Halts Production",
        description="Workers at the Nevada Gold Mines have walked out over pay disputes, potentially disrupting global supply for weeks.",
        is_relevant="True",
        rationale="Supply constraints generally support prices, but gold is not a purely industrial commodity. The massive above-ground stocks mean mine disruptions have a smaller, slower impact than in oil markets.",
        category="Industrial",
        sentiment_score="6",
        impact_reasoning="Büyük ölçekli bir madendeki üretim duruşu arzı kısıtlar. Altın fiyatları genelde makro verilere duyarlı olsa da, fiziksel arzın azalması fiyatları hafifçe yukarı destekleyebilir.",
        confidence_score="0.75"
    ).with_inputs("title", "description"),
]
