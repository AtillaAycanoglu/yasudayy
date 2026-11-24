package com.pirpir.game;

import android.app.Activity;
import android.content.ClipData;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.graphics.Color;
import android.os.Build;
import android.os.Bundle;
import android.os.Vibrator;
import android.util.Base64;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import java.io.File;
import java.io.FileOutputStream;

public class MainActivity extends Activity {
    private WebView web;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        Window w = getWindow();
        w.setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN | WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON,
                WindowManager.LayoutParams.FLAG_FULLSCREEN | WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        if (Build.VERSION.SDK_INT >= 28) {
            // LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES = 1
            try {
                WindowManager.LayoutParams lp = w.getAttributes();
                lp.getClass().getField("layoutInDisplayCutoutMode").setInt(lp, 1);
                w.setAttributes(lp);
            } catch (Throwable ignored) { }
        }

        web = new WebView(this);
        web.setBackgroundColor(Color.rgb(11, 6, 32));
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        try {
            s.getClass().getMethod("setMediaPlaybackRequiresUserGesture", boolean.class).invoke(s, false);
        } catch (Throwable ignored) { }
        web.setWebViewClient(new WebViewClient());
        web.setWebChromeClient(new WebChromeClient());
        web.setVerticalScrollBarEnabled(false);
        web.setHorizontalScrollBarEnabled(false);
        web.setOverScrollMode(View.OVER_SCROLL_NEVER);
        web.addJavascriptInterface(new Bridge(), "Android");
        web.loadUrl("file:///android_asset/index.html");
        setContentView(web);
        hideSystemUi();
    }

    private void hideSystemUi() {
        // LAYOUT_STABLE|LAYOUT_HIDE_NAV|LAYOUT_FULLSCREEN|HIDE_NAV|FULLSCREEN|IMMERSIVE_STICKY
        web.setSystemUiVisibility(0x0100 | 0x0200 | 0x0400 | 0x0002 | 0x0004 | 0x1000);
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) hideSystemUi();
    }

    @Override
    public void onBackPressed() {
        web.loadUrl("javascript:window.onBack&&window.onBack()");
    }

    @Override
    protected void onPause() {
        web.loadUrl("javascript:window.onAppPause&&window.onAppPause()");
        web.onPause();
        super.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        web.onResume();
        web.loadUrl("javascript:window.onAppResume&&window.onAppResume()");
        hideSystemUi();
    }

    @Override
    protected void onDestroy() {
        web.destroy();
        super.onDestroy();
    }

    public class Bridge {
        @JavascriptInterface
        public void vibrate(int ms) {
            try {
                Vibrator v = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);
                if (v != null) v.vibrate(ms);
            } catch (Throwable ignored) { }
        }

        @JavascriptInterface
        public void shareImage(String base64Png, final String text) {
            try {
                byte[] data = Base64.decode(base64Png, Base64.DEFAULT);
                File dir = new File(getCacheDir(), "share");
                dir.mkdirs();
                FileOutputStream out = new FileOutputStream(new File(dir, "glowbird.png"));
                out.write(data);
                out.close();
                final Uri uri = Uri.parse("content://" + ShareProvider.AUTHORITY + "/glowbird.png");
                runOnUiThread(new Runnable() { public void run() {
                    Intent send = new Intent(Intent.ACTION_SEND);
                    send.setType("image/png");
                    send.putExtra(Intent.EXTRA_STREAM, uri);
                    send.putExtra(Intent.EXTRA_TEXT, text);
                    send.setClipData(ClipData.newRawUri("", uri));
                    send.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                    Intent chooser = Intent.createChooser(send, null);
                    chooser.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                    startActivity(chooser);
                } });
            } catch (Throwable ignored) { }
        }

        @JavascriptInterface
        public void exit() {
            runOnUiThread(new Runnable() { public void run() { finish(); } });
        }
    }
}
