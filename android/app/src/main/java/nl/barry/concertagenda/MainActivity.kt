package nl.barry.concertagenda

import android.annotation.SuppressLint
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.webkit.JavascriptInterface
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AppCompatActivity
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat

class MainActivity : AppCompatActivity() {
    private lateinit var web: WebView

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()
        super.onCreate(savedInstanceState)
        web = WebView(this)
        web.setBackgroundColor(0xFF0A0A12.toInt())
        setContentView(web)
        web.fitsSystemWindows = true
        // startscherm schermvullend: balken weg tot je op het plaatje tikt
        if (savedInstanceState == null) bars(false)
        web.addJavascriptInterface(object {
            @JavascriptInterface fun splashDone() { runOnUiThread { bars(true) } }
        }, "AndroidApp")

        web.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            cacheMode = WebSettings.LOAD_DEFAULT
            mediaPlaybackRequiresUserGesture = true
            // versie van de app meesturen: de infopagina laat zien welke versie op de telefoon staat
            userAgentString = userAgentString + " ConcertAgendaApp/" + packageManager.getPackageInfo(packageName, 0).versionName
        }
        web.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                val uri = request.url
                if (uri.host == HOST) return false
                startActivity(Intent(Intent.ACTION_VIEW, uri))   // zaalsites en TicketSwap openen in de browser
                return true
            }

            override fun onReceivedError(view: WebView, request: WebResourceRequest, error: WebResourceError) {
                if (request.isForMainFrame) { bars(true); view.loadUrl("file:///android_asset/offline.html") }
            }
        }
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (web.canGoBack()) web.goBack() else finish()
            }
        })
        if (savedInstanceState == null) web.loadUrl(START) else web.restoreState(savedInstanceState)
    }

    private fun bars(show: Boolean) {
        val c = WindowCompat.getInsetsController(window, window.decorView)
        if (show) c.show(WindowInsetsCompat.Type.systemBars())
        else {
            c.systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
            c.hide(WindowInsetsCompat.Type.systemBars())
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        web.saveState(outState)
    }

    companion object {
        const val HOST = "bzwijgers.github.io"
        const val START = "https://bzwijgers.github.io/Concerten/"
    }
}
