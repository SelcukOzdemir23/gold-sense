Muhakeme (Chain of Thought): Mevcut analyst.py dosyasında dspy.Predict kullanıyorsun. Doküman, dspy.ChainOfThought modülünün modelin önce düşünmesini sağlayarak kaliteyi artırdığını belirtiyor. Finansal analiz gibi karmaşık bir işte modelin "adım adım düşünmesi" jüriyi çok daha fazla etkiler.

Derleme ve Optimizasyon (Compilation): DSPy'ın asıl olayı prompt yazmak değil, promptu optimize etmektir. Dokümanda belirtilen BootstrapFewShot veya MIPROv2 gibi optimizer'ları kullanarak, elindeki verilerden "en iyi promptu" sisteme buldurmalısın.

Metrikler ve Değerlendirme: Kodunda henüz bir dspy.Metric tanımlı değil. Modelin başarısını ölçen (Örn: Haberle puan uyumu) bir fonksiyon yazıp, dspy.Evaluate ile test etmelisin.

Doğrulama (Assertions): Dokümanda "DSPy Assertions" özelliğinden bahsediliyor. Örneğin; "Skor mutlaka 1-10 arası olmalı" veya "Gerekçe Türkçe olmalı" gibi kuralları kod seviyesinde zorunlu kılabilirsin.