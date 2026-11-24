# Glowbird — Neon Wings

Mobil için tek dokunuşlu, neon/synthwave temalı bir uçma oyunu. Bol parçacık efekti, ekran sallanması,
zoom vuruşları ve yavaş çekim ölüm anı var.

**İçerik**
- Görevler: aynı anda 3 görev açık olur. Tamamlanan görev kristal kazandırır ve yerine daha zor bir yenisi gelir.
- Engeller:
  - hareketli sütunlar (12+)
  - dönen testereler (6+)
  - açılıp kapanan kapılar (15+)
  - yanıp sönen lazerler (20+)
- Güçlendirmeler:
  - Kalkan: bir çarpmayı emer
  - Mıknatıs: 7 saniye boyunca kristalleri çeker
- Kristallerle açılan 6 karakter, kıl payı bonusu, madalyalar
- 20 dil, varsayılan İngilizce

**Dosyalar**
- `game/index.html`: oyunun tamamı (tarayıcıda da açılıp oynanabilir)
- `game/i18n.js`: çeviriler. Yeni dil eklemek için bir blok eklemek yeterli.
- `android/`: oyunu tam ekran WebView içinde açan Android aktivitesi
- `tools/build_apk.sh`: Android SDK olmadan `dist/glowbird.apk` üretir (JDK, Node/Playwright ve Python 3 yeterli)
- `dist/glowbird.apk`: hazır APK (Android 7.0+)
