package dev.kartpad.android

import android.content.Context
import android.net.Uri
import java.io.File
import java.nio.file.Files
import java.util.zip.ZipFile

fun main() {
    val root = Files.createTempDirectory("kartpad-report-export-").toFile()
    try {
        val files = File(root, "files").apply { mkdirs() }
        val logs = File(files, "KartPad/Logs/session").apply { mkdirs() }
        File(logs, "console.log").writeText("[runtime] WiiCompiled vTEST\ncurrent session")
        val older = File(files, "KartPad/Logs/older").apply { mkdirs() }
        File(older, "console.log").apply { writeText("OTHER_SESSION"); setLastModified(1) }
        File(files, "KartPad/Logs/android-health.log").writeText("UNRELATED_HEALTH")
        val privateSave = File(files, "KartPad/NAND/private.txt").apply {
            parentFile.mkdirs(); writeText("PRIVATE_NAND_MUST_NOT_EXPORT")
        }
        Files.createSymbolicLink(File(logs, "crash_linked-save.txt").toPath(), privateSave.toPath())
        Files.createSymbolicLink(File(files, "KartPad/Logs/session-alias").toPath(), logs.toPath())
        check(KartPadDiagnosticExport.sessions(Context(files)).none { it.id == "session-alias" })
        File(logs, "memory.bin").writeText("PRIVATE_MEMORY_MUST_NOT_EXPORT")
        for (i in 0..12) File(logs, "crash_$i.txt").apply {
            writeText("sample-$i"); setLastModified(100000L + i)
        }
        val large = File(logs, "crash_large.txt")
        large.outputStream().use { out ->
            out.write("VERSION_HEADER_MUST_REMAIN".toByteArray())
            val chunk = ByteArray(1024 * 1024) { 'x'.code.toByte() }
            repeat(5) { out.write(chunk) }
        }
        large.setLastModified(200000)
        val zipFile = File(root, "export.zip")
        KartPadDiagnosticExport.write(Context(files), Uri(zipFile))
        ZipFile(zipFile).use { zip ->
            val entries = zip.entries().asSequence().toList()
            check(entries.size == 14) // 12 bounded logs and 2 export-time metadata entries
            check(entries.none { "linked-save" in it.name || "memory.bin" in it.name || "NAND" in it.name })
            check(entries.none { "older" in it.name || "android-health" in it.name })
            check(zip.getEntry("Logs/session/crash_0.txt") == null)
            check(zip.getEntry("Logs/session/crash_1.txt") == null)
            check(zip.getEntry("Logs/session/crash_large.txt").size == 4L * 1024 * 1024)
            for (entry in entries) {
                val text = zip.getInputStream(entry).bufferedReader().readText()
                check(!text.contains("PRIVATE_NAND") && !text.contains("PRIVATE_MEMORY") && !text.contains("OTHER_SESSION"))
            }
            val shortened = zip.getInputStream(zip.getEntry("Logs/session/crash_large.txt")).bufferedReader().readText()
            check(shortened.startsWith("VERSION_HEADER_MUST_REMAIN"))
            check(shortened.contains("middle of log omitted"))
        }
        KartPadDiagnosticExport.write(Context(files), Uri(zipFile), "older")
        ZipFile(zipFile).use { zip ->
            check(zip.getEntry("Logs/older/console.log") != null)
            check(zip.getEntry("Logs/session/console.log") == null)
        }
        check(runCatching { KartPadDiagnosticExport.write(Context(files), Uri(zipFile), "../NAND") }.isFailure)
        val textFile = File(root, "diagnostics.txt")
        KartPadDiagnosticExport.writeText(Context(files), Uri(textFile), "session")
        val text = textFile.readText()
        check(text.contains("VERSION_HEADER_MUST_REMAIN") && text.contains("middle omitted"))
        check(text.contains("[runtime] WiiCompiled vTEST"))
        check(textFile.length() < 4L * 1024 * 1024)
        check(listOf("PRIVATE_NAND", "PRIVATE_MEMORY", "OTHER_SESSION", "UNRELATED_HEALTH").none { it in text })
        KartPadDiagnosticExport.writeText(Context(files), Uri(textFile), "older")
        check(textFile.readText().contains("OTHER_SESSION"))
        check(!textFile.readText().contains("VERSION_HEADER_MUST_REMAIN"))
        check(runCatching { KartPadDiagnosticExport.writeText(Context(files), Uri(textFile), "../NAND") }.isFailure)
        val emptyFiles = File(root, "empty").apply { mkdirs() }
        KartPadDiagnosticExport.write(Context(emptyFiles), Uri(zipFile))
        ZipFile(zipFile).use { check(it.size() == 2) }
        val aliasFiles = File(root, "alias-files").apply { mkdirs() }
        File(aliasFiles, "KartPad").mkdirs()
        Files.createSymbolicLink(File(aliasFiles, "KartPad/Logs").toPath(), logs.parentFile.toPath())
        check(runCatching { KartPadDiagnosticExport.sessions(Context(aliasFiles)) }.isFailure)
        println("PASS: selected session, header and tail bounds, symlink/save/history exclusion, unavailable session and empty logs")
    } finally { root.deleteRecursively() }
}
