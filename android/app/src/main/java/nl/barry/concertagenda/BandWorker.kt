package nl.barry.concertagenda

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.work.Worker
import androidx.work.WorkerParameters
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale

/* Dagelijks (op de achtergrond): nieuw aangekondigde concerten van bands die je zag of waarvoor je interesse hebt.
   De lijst met bands komt van de app zelf (AndroidApp.setWatch); hier alleen de openbare agenda ophalen en vergelijken. */
class BandWorker(ctx: Context, params: WorkerParameters) : Worker(ctx, params) {
    override fun doWork(): Result {
        val prefs = applicationContext.getSharedPreferences("bandnews", Context.MODE_PRIVATE)
        val watch = prefs.getString("watch", null) ?: return Result.success()
        val w = JSONObject(watch)
        val keys = HashSet<String>(); w.optJSONArray("keys")?.let { for (i in 0 until it.length()) keys.add(it.getString(i)) }
        if (keys.isEmpty()) return Result.success()
        val seen = HashSet<String>(); w.optJSONArray("seen")?.let { for (i in 0 until it.length()) seen.add(it.getString(i)) }
        val told = HashSet(prefs.getStringSet("told", emptySet()) ?: emptySet())
        val json = try { fetch("https://bzwijgers.github.io/Concerten/data/events.json") } catch (e: Exception) { return Result.retry() }
        val events = JSONObject(json).getJSONArray("events")
        val fmt = SimpleDateFormat("yyyy-MM-dd", Locale.US)
        val today = fmt.format(Calendar.getInstance().time)
        val cut = fmt.format(Calendar.getInstance().apply { add(Calendar.DAY_OF_YEAR, -14) }.time)
        val hits = ArrayList<Pair<String, String>>()   // id, regel
        for (i in 0 until events.length()) {
            val e = events.getJSONObject(i)
            val first = e.optString("first"); val d = e.optString("d")
            if (first.isEmpty() || first == "base" || first < cut || d < today) continue
            val id = e.optString("v") + "|" + d + "|" + e.optString("u")
            if (id in seen || id in told) continue
            val names = bandsOf(e.optString("n")).toMutableList()
            e.optJSONArray("la")?.let { for (j in 0 until it.length()) names.add(it.getString(j)) }
            val who = names.firstOrNull { normA(it) in keys } ?: continue
            hits.add(id to who.trim() + " · " + dayLabel(d))
        }
        if (hits.isNotEmpty() && canNotify()) {
            notify(hits.map { it.second })
            told.addAll(hits.map { it.first })
            prefs.edit().putStringSet("told", told.filter { it.split("|").getOrElse(1) { "" } >= today }.toSet()).apply()
        }
        return Result.success()
    }

    private fun canNotify(): Boolean = Build.VERSION.SDK_INT < 33 ||
        applicationContext.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED

    private fun notify(lines: List<String>) {
        val ctx = applicationContext
        val nm = ctx.getSystemService(NotificationManager::class.java)
        if (Build.VERSION.SDK_INT >= 26) nm.createNotificationChannel(NotificationChannel(CHANNEL, "Nieuw van jouw bands", NotificationManager.IMPORTANCE_DEFAULT))
        val open = PendingIntent.getActivity(ctx, 1, Intent(ctx, MainActivity::class.java).putExtra("open", "bandnews").addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        val title = if (lines.size == 1) "Nieuw van jouw bands" else "${lines.size} nieuwe concerten van jouw bands"
        val style = NotificationCompat.InboxStyle(); lines.take(6).forEach { style.addLine(it) }; if (lines.size > 6) style.setSummaryText("en nog ${lines.size - 6}")
        val n = NotificationCompat.Builder(ctx, CHANNEL).setSmallIcon(android.R.drawable.ic_popup_reminder).setContentTitle(title).setContentText(lines.first())
            .setStyle(style).setContentIntent(open).setAutoCancel(true).build()
        try { NotificationManagerCompat.from(ctx).notify(42, n) } catch (e: SecurityException) { }
    }

    private fun fetch(u: String): String {
        val c = URL(u).openConnection() as HttpURLConnection
        c.connectTimeout = 20000; c.readTimeout = 30000; c.useCaches = false
        return c.inputStream.bufferedReader().use { it.readText() }
    }

    companion object {
        const val CHANNEL = "bandnews"
        private val MON = arrayOf("jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec")
        fun dayLabel(d: String): String { val p = d.split("-"); return if (p.size == 3) "${p[2].toInt()} ${MON[p[1].toInt() - 1]}" else d }
        /* zelfde als normA in de app: kleine letters, landcode tussen haakjes weg, 'The' weg, & = and, alleen letters en cijfers */
        fun normA(n: String): String = n.lowercase(Locale.ROOT)
            .replace(Regex("\\s*\\((?:[a-z]{2,3}|[a-z]{2}/[a-z]{2})\\)\\s*"), " ")
            .replace(Regex("^the\\s+|,?\\s+the$"), "").replace("&", " and ")
            .replace(Regex("[^a-z0-9à-ÿ]+"), " ").trim()
        /* zelfde als bandsOf in de app: deel voor ' - ' of ': ', gesplitst op +, w/, with, met, x, support, feat, komma, / en | (& blijft heel) */
        fun bandsOf(title: String): List<String> {
            val head = title.split(Regex("\\s+[-–—]\\s+|:\\s+"))[0]
            return head.split(Regex("\\s+(?:\\+|w/|with|met|x|support:?|feat\\.?|ft\\.?)\\s+|\\s*[,/|]\\s+", RegexOption.IGNORE_CASE))
                .map { it.replace(Regex("\\s*\\((?:[A-Z]{2,3}|[a-z]{2})\\)\\s*$"), "").trim() }.filter { it.length > 1 }
        }
    }
}
