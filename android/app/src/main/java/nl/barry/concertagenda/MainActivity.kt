package nl.barry.concertagenda

import android.annotation.SuppressLint
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.webkit.JavascriptInterface
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat

class MainActivity : AppCompatActivity() {
    private lateinit var web: WebView
    private var fileCb: ValueCallback<Array<Uri>>? = null
    // bestand kiezen voor "Archief inlezen" (Excel of CSV van de telefoon)
    private val pick = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { r ->
        fileCb?.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(r.resultCode, r.data))
        fileCb = null
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()
        super.onCreate(savedInstanceState)
        web = WebView(this)
        web.setBackgroundColor(0x00000000)   // doorzichtig: de startfoto van het venster blijft zichtbaar tot de pagina zelf getekend is
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
        web.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(view: WebView, cb: ValueCallback<Array<Uri>>, params: FileChooserParams): Boolean {
                fileCb?.onReceiveValue(null)
                fileCb = cb
                val i = Intent(Intent.ACTION_GET_CONTENT).addCategory(Intent.CATEGORY_OPENABLE).setType("*/*")
                return try { pick.launch(Intent.createChooser(i, "Kies je concertlijst")); true }
                catch (e: Exception) { fileCb = null; false }
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
