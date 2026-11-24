#!/usr/bin/env bash
# Builds dist/pirpir.apk with only a JDK, Node+Playwright and Python 3 (no Android SDK needed).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
B="$ROOT/build"; T="$B/tools"; mkdir -p "$T" "$B/classes" "$B/stubs" "$ROOT/dist"
M=https://repo1.maven.org/maven2
fetch(){ [ -f "$T/$2" ] || curl -sfL -o "$T/$2" "$M/$1/$2"; }
fetch com/jakewharton/android/repackaged/dalvik-dx/16.0.1 dalvik-dx-16.0.1.jar
fetch com/android/tools/build/apksig/2.3.0 apksig-2.3.0.jar
fetch com/google/android/android/4.1.1.4 android-4.1.1.4.jar
ANDROID_JAR="$T/android-4.1.1.4.jar"

echo "> javac"
rm -rf "$B/classes"/* "$B/stubs"/*
javac -nowarn -d "$B/stubs" --release 8 -cp "$ANDROID_JAR" $(find "$ROOT/android/stubs" -name '*.java') 2>&1 | grep -v 'warning' || true
javac -nowarn -d "$B/classes" --release 8 -cp "$ANDROID_JAR:$B/stubs" $(find "$ROOT/android/src" -name '*.java') 2>&1 | grep -v 'warning' || true
test -f "$B/classes/com/pirpir/game/MainActivity.class"

echo "> dx"
java -cp "$T/dalvik-dx-16.0.1.jar" com.android.dx.command.Main --dex --min-sdk-version=24 --output="$B/classes.dex" "$B/classes"

echo "> icon"
node "$ROOT/tools/make_icon.js" "$ROOT/game/index.html" "$B/icon.png"

echo "> pack"
python3 "$ROOT/tools/pack_apk.py" "$B/classes.dex" "$ROOT/game" "$B/icon.png" "$B/unsigned.apk"

echo "> sign"
KS="${KEYSTORE:-$ROOT/android/release.p12}"; PW="${KEYSTORE_PASS:-pirpir123}"
[ -f "$KS" ] || keytool -genkeypair -keystore "$KS" -storetype PKCS12 -storepass "$PW" -keypass "$PW" -alias pirpir \
  -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Pirpir, O=Pirpir, C=TR" >/dev/null 2>&1
javac -d "$B/signer" -cp "$T/apksig-2.3.0.jar" "$ROOT/tools/Signer.java"
java --add-exports java.base/sun.security.x509=ALL-UNNAMED --add-exports java.base/sun.security.pkcs=ALL-UNNAMED --add-exports java.base/sun.security.util=ALL-UNNAMED -cp "$B/signer:$T/apksig-2.3.0.jar" Signer "$B/unsigned.apk" "$ROOT/dist/pirpir.apk" "$KS" "$PW" pirpir
ls -la "$ROOT/dist/pirpir.apk"
