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

/* Concertdag: om 9 uur 's ochtends een melding voor je concert(en) met kaartje van vandaag.
   De kaartjes komen van de app zelf (AndroidApp.setWatch, veld 'tix'); MainActivity plant per datum één taak. */
class DayWorker(ctx: Context, params: WorkerParameters) : Worker(ctx, params) {
    override fun doWork(): Result {
        val d = inputData.getString("d") ?: return Result.success()
        val prefs = applicationContext.getSharedPreferences("bandnews", Context.MODE_PRIVATE)
        val told = HashSet(prefs.getStringSet("daytold", emptySet()) ?: emptySet())
        if (d in told) return Result.success()
        val tix = try { JSONObject(prefs.getString("watch", "{}") ?: "{}").optJSONArray("tix") } catch (e: Exception) { null } ?: return Result.success()
        val lines = ArrayList<Pair<String, String>>()   // artiest, zaal + tijd (+ reistijd)
        var note = ""
        for (i in 0 until tix.length()) {
            val o = tix.getJSONObject(i)
            if (o.optString("d") != d) continue   // kaartje inmiddels weg of verzet: geen melding
            val t = o.optString("t"); val rt = o.optString("rt")
            lines.add(o.optString("n") to (o.optString("w") + (if (t.isNotEmpty()) " · $t" else "") + (if (rt.isNotEmpty()) " · $rt" else "")))
            if (note.isEmpty()) note = o.optString("note")
        }
        if (lines.isEmpty() || !canNotify()) return Result.success()
        val ctx = applicationContext
        val nm = ctx.getSystemService(NotificationManager::class.java)
        if (Build.VERSION.SDK_INT >= 26) nm.createNotificationChannel(NotificationChannel(CHANNEL, "Concertdag", NotificationManager.IMPORTANCE_HIGH))
        val open = PendingIntent.getActivity(ctx, 2, Intent(ctx, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        val title = if (lines.size == 1) "Vandaag: " + lines[0].first else "Vandaag: ${lines.size} concerten"
        val b = NotificationCompat.Builder(ctx, CHANNEL).setSmallIcon(android.R.drawable.ic_popup_reminder).setContentTitle(title)
            .setContentText(if (lines.size == 1) lines[0].second else lines.joinToString(" · ") { it.first }).setContentIntent(open).setAutoCancel(true)
        if (lines.size > 1) { val st = NotificationCompat.InboxStyle(); lines.forEach { st.addLine(it.first + " — " + it.second) }; b.setStyle(st) }
        else if (note.isNotEmpty()) b.setStyle(NotificationCompat.BigTextStyle().bigText(lines[0].second + "\n✎ " + note))   // je notitie (parkeren, trein, met wie)
        try { NotificationManagerCompat.from(ctx).notify(43, b.build()) } catch (e: SecurityException) { }
        told.add(d)
        prefs.edit().putStringSet("daytold", told.filter { it >= d.take(4) + "-01-01" }.toSet()).apply()
        return Result.success()
    }

    private fun canNotify(): Boolean = Build.VERSION.SDK_INT < 33 ||
        applicationContext.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED

    companion object { const val CHANNEL = "concertdag" }
}
