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
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale

/* Eén keer per week (vrijdag rond 18 uur): hoeveel concerten er de afgelopen 7 dagen nieuw zijn aangekondigd in je favoriete zalen.
   De zalen komen van de app zelf (AndroidApp.setWatch, veld 'zalen': sleutel -> naam); tikken opent de lijst 'Nieuw' in je zalen. */
class VenueWorker(ctx: Context, params: WorkerParameters) : Worker(ctx, params) {
    override fun doWork(): Result {
        val prefs = applicationContext.getSharedPreferences("bandnews", Context.MODE_PRIVATE)
        val w = try { JSONObject(prefs.getString("watch", "{}") ?: "{}") } catch (e: Exception) { return Result.success() }
        val zalen = w.optJSONObject("zalen") ?: return Result.success()
        if (zalen.length() == 0) return Result.success()
        val fmt = SimpleDateFormat("yyyy-MM-dd", Locale.US)
        val today = fmt.format(Calendar.getInstance().time)
        if (prefs.getString("zalenlast", "") == today) return Result.success()   // vandaag al gemeld
        val json = try { fetch("https://bzwijgers.github.io/Concerten/data/events.json") } catch (e: Exception) { return Result.retry() }
        val events = JSONObject(json).getJSONArray("events")
        val cut = fmt.format(Calendar.getInstance().apply { add(Calendar.DAY_OF_YEAR, -7) }.time)
        val per = LinkedHashMap<String, Int>()
        for (i in 0 until events.length()) {
            val e = events.getJSONObject(i)
            val v = e.optString("v"); val first = e.optString("first")
            if (!zalen.has(v) || first.isEmpty() || first == "base" || first < cut || e.optString("d") < today || e.optBoolean("o", false)) continue
            val label = zalen.optString(v, v)
            per[label] = (per[label] ?: 0) + 1
        }
        val total = per.values.sum()
        if (total == 0 || !canNotify()) return Result.success()
        val lines = per.entries.sortedByDescending { it.value }.map { "${it.key} ${it.value}" }
        val ctx = applicationContext
        val nm = ctx.getSystemService(NotificationManager::class.java)
        if (Build.VERSION.SDK_INT >= 26) nm.createNotificationChannel(NotificationChannel(CHANNEL, "Nieuw in je zalen (wekelijks)", NotificationManager.IMPORTANCE_DEFAULT))
        val open = PendingIntent.getActivity(ctx, 3, Intent(ctx, MainActivity::class.java).putExtra("open", "zalennieuw").addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        val title = if (total == 1) "1 nieuw concert in je zalen" else "$total nieuwe concerten in je zalen"
        val style = NotificationCompat.InboxStyle(); lines.take(7).forEach { style.addLine(it) }; if (lines.size > 7) style.setSummaryText("en nog ${lines.size - 7} zalen")
        val n = NotificationCompat.Builder(ctx, CHANNEL).setSmallIcon(android.R.drawable.ic_popup_reminder).setContentTitle(title)
            .setContentText(lines.take(3).joinToString(" · ")).setStyle(style).setContentIntent(open).setAutoCancel(true).build()
        try { NotificationManagerCompat.from(ctx).notify(44, n) } catch (e: SecurityException) { }
        prefs.edit().putString("zalenlast", today).apply()
        return Result.success()
    }

    private fun canNotify(): Boolean = Build.VERSION.SDK_INT < 33 ||
        applicationContext.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED

    private fun fetch(u: String): String {
        val c = URL(u).openConnection() as HttpURLConnection
        c.connectTimeout = 20000; c.readTimeout = 30000; c.useCaches = false
        return c.inputStream.bufferedReader().use { it.readText() }
    }

    companion object {
        const val CHANNEL = "zalennieuw"
        /* milliseconden tot de eerstvolgende vrijdag 18:00 */
        fun untilFriday(): Long {
            val now = Calendar.getInstance()
            val at = Calendar.getInstance().apply { set(Calendar.HOUR_OF_DAY, 18); set(Calendar.MINUTE, 0); set(Calendar.SECOND, 0); set(Calendar.MILLISECOND, 0) }
            while (at.get(Calendar.DAY_OF_WEEK) != Calendar.FRIDAY || !at.after(now)) at.add(Calendar.DAY_OF_YEAR, 1)
            return at.timeInMillis - now.timeInMillis
        }
    }
}
