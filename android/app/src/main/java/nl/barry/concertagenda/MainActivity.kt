package nl.barry.concertagenda

import android.annotation.SuppressLint
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.webkit.JavascriptInterface
import android.webkit.PermissionRequest
import android.Manifest
import android.content.pm.PackageManager
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
    private var pendingSave: String? = null
    private var pendingCam: PermissionRequest? = null
    // camera voor 'Koppelen met QR-code': eerst Android-toestemming, dan de pagina toestaan
    private val camPerm = registerForActivityResult(ActivityResultContracts.RequestPermission()) { ok ->
        val r = pendingCam; pendingCam = null
        if (r != null) { if (ok) r.grant(arrayOf(PermissionRequest.RESOURCE_VIDEO_CAPTURE)) else r.deny() }
    }
    // back-up opslaan: de gebruiker kiest zelf waar (Downloads, Drive, ...)
    private val saveDoc = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { r ->
        val uri = r.data?.data; val txt = pendingSave; pendingSave = null
        if (r.resultCode == RESULT_OK && uri != null && txt != null) {
            try {
                contentResolver.openOutputStream(uri)?.use { it.write(txt.toByteArray(Charsets.UTF_8)) }
                android.widget.Toast.makeText(this, "Back-up opgeslagen", android.widget.Toast.LENGTH_SHORT).show()
            } catch (e: Exception) {
                android.widget.Toast.makeText(this, "Opslaan mislukt: " + e.message, android.widget.Toast.LENGTH_LONG).show()
            }
        }
    }
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
            // poster delen (Instagram, WhatsApp, ...): bestand in de cache zetten en het deelmenu van Android openen
            @JavascriptInterface fun shareImage(b64: String, mime: String, text: String) {
                try {
                    val dir = java.io.File(cacheDir, "share").apply { mkdirs() }
                    val ext = if (mime.contains("png")) "png" else if (mime.contains("webp")) "webp" else "jpg"
                    val f = java.io.File(dir, "poster.$ext")
                    f.writeBytes(android.util.Base64.decode(b64, android.util.Base64.DEFAULT))
                    val uri = androidx.core.content.FileProvider.getUriForFile(this@MainActivity, "$packageName.files", f)
                    val i = Intent(Intent.ACTION_SEND).setType(mime).putExtra(Intent.EXTRA_STREAM, uri).putExtra(Intent.EXTRA_TEXT, text).addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                    runOnUiThread { startActivity(Intent.createChooser(i, "Poster delen")) }
                } catch (e: Exception) {
                    runOnUiThread { android.widget.Toast.makeText(this@MainActivity, "Delen mislukt: " + e.message, android.widget.Toast.LENGTH_LONG).show() }
                }
            }
            @JavascriptInterface fun shareText(text: String) {
                runOnUiThread { startActivity(Intent.createChooser(Intent(Intent.ACTION_SEND).setType("text/plain").putExtra(Intent.EXTRA_TEXT, text), "Delen")) }
            }
            @JavascriptInterface fun saveFile(name: String, content: String) {
                runOnUiThread {
                    pendingSave = content
                    saveDoc.launch(Intent(Intent.ACTION_CREATE_DOCUMENT).addCategory(Intent.CATEGORY_OPENABLE).setType("application/json").putExtra(Intent.EXTRA_TITLE, name))
                }
            }
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
            override fun onPermissionRequest(request: PermissionRequest) {
                runOnUiThread {
                    if (!request.resources.contains(PermissionRequest.RESOURCE_VIDEO_CAPTURE) || request.origin.host != HOST) { request.deny(); return@runOnUiThread }
                    if (checkSelfPermission(Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) request.grant(arrayOf(PermissionRequest.RESOURCE_VIDEO_CAPTURE))
                    else { pendingCam = request; camPerm.launch(Manifest.permission.CAMERA) }
                }
            }
            override fun onShowFileChooser(view: WebView, cb: ValueCallback<Array<Uri>>, params: FileChooserParams): Boolean {
                fileCb?.onReceiveValue(null)
                fileCb = cb
                val img = params.acceptTypes.any { it.startsWith("image") }   // poster toevoegen: foto's; archief: elk bestand
                val i = Intent(Intent.ACTION_GET_CONTENT).addCategory(Intent.CATEGORY_OPENABLE).setType(if (img) "image/*" else "*/*")
                return try { pick.launch(Intent.createChooser(i, if (img) "Kies een poster" else "Kies je concertlijst")); true }
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
