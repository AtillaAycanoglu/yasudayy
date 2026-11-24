# Glowbird — Neon Wings

Mobil için tek dokunuşlu, neon/synthwave temalı bir uçma oyunu. Bol parçacık efekti, ekran sallanması,
zoom vuruşları ve yavaş çekim ölüm anı var.

**İçerik**
- 4 dünya, her 25 puanda değişir:
  - Neon Şehir
  - Buz Zirveleri: kar yağar, daha çok testere çıkar
  - Yanardağ: yerden ateş topları fırlar
  - Derin Uzay: yerçekimi daha düşük
- Boss: belli puanlarda gelir, lazer ve testere atar. 15 saniye dayanırsan büyük ödül verir.
- Engeller:
  - hareketli sütunlar
  - dönen testereler
  - açılıp kapanan kapılar
  - kapanan sütunlar
  - yanıp sönen lazerler
  - karşıdan gelen kuş sürüsü
  - ters yerçekimi bölgesi
- Güçlendirmeler:
  - kalkan
  - mıknatıs
  - ağır çekim
  - küçülme
  - x2 kristal
- Kombo: üst üste kıl payı geçtikçe puan çarpanı x5'e kadar çıkar.
- Görevler: aynı anda 3 görev açık olur, tamamlanınca kristal verir.
- Günlük ödül: 7 günlük seri.
- Synthwave müzik: oyunun içinde üretilir, hız arttıkça temposu artar.
- 10 karakter (bazılarının özel iz efekti var) ve 7 şapka.
- İstatistik ekranı, son anları tekrar izleme, skor kartı paylaşma.
- 20 dil, varsayılan İngilizce.

**Dosyalar**
- `game/index.html`: oyunun tamamı (tarayıcıda da açılıp oynanabilir)
- `game/i18n.js`: çeviriler. Yeni dil eklemek için bir blok eklemek yeterli.
- `android/`: oyunu tam ekran WebView içinde açan Android aktivitesi
- `tools/build_apk.sh`: Android SDK olmadan `dist/glowbird.apk` üretir (JDK, Node/Playwright ve Python 3 yeterli)
- `dist/glowbird.apk`: hazır APK (Android 7.0+)
