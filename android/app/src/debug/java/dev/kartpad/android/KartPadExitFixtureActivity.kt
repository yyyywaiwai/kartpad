package dev.kartpad.android

import android.app.Activity
import android.net.Uri
import android.os.Bundle
import android.util.Log
import org.json.JSONObject
import java.io.File
import java.util.zip.ZipFile

/** Debug-only: exercise the real OS history and production exporter in an empty test install. */
internal class KartPadExitFixtureActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        KartPadExitDiagnostics.mark(this, "base")
        if (!intent.getBooleanExtra("export", false)) return
        Thread {
            runCatching {
                val destination = File(cacheDir, "exit-fixture.zip")
                KartPadDiagnosticExport.write(this, Uri.fromFile(destination))
                ZipFile(destination).use { zip ->
                    val report = JSONObject(zip.getInputStream(zip.getEntry("process-exits.json"))
                        .bufferedReader().readText())
                    check(report.getString("availability") == "available")
                    val exits = report.getJSONArray("exits")
                    check(exits.length() in 1..8)
                    check((0 until exits.length()).any {
                        val exit = exits.getJSONObject(it)
                        exit.optInt("version_code") == BuildConfig.VERSION_CODE &&
                            exit.optString("last_profile") == "base" &&
                            exit.getString("reason") == "user_requested"
                    }) { "Expected prior test process force-stop with build/profile attribution" }
                    for (i in 0 until exits.length()) {
                        val keys = exits.getJSONObject(i).keys().asSequence().toSet()
                        check(keys == setOf("timestamp_ms", "reason_code", "reason", "status", "importance",
                            "pss_kib", "rss_kib", "version_code", "last_profile"))
                    }
                }
                destination.delete()
            }.onSuccess { Log.i("KartPadExitFixture", "PASS: OS force-stop attribution and bounded exported metadata") }
                .onFailure { Log.e("KartPadExitFixture", "FAIL: exit diagnostics", it) }
            runOnUiThread { finish() }
        }.start()
    }
}
