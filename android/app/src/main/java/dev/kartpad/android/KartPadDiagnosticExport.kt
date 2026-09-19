package dev.kartpad.android

import android.content.Context
import android.net.Uri
import java.io.File
import java.io.RandomAccessFile
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

/** Explicit local export, available even when the game cannot finish booting. */
internal object KartPadDiagnosticExport {
    private const val MAX_FILE_BYTES = 4L * 1024 * 1024
    private const val MAX_FILES = 12

    data class Session(val id: String, val modified: Long)

    private fun logsRoot(context: Context): File {
        val root = File(context.filesDir.canonicalFile, "KartPad/Logs")
        require(root.absoluteFile == root.canonicalFile) { "The log directory must not be a symbolic link." }
        return root
    }

    fun sessions(context: Context): List<Session> {
        val root = logsRoot(context)
        return root.listFiles().orEmpty().filter { directory ->
            directory.isDirectory && directory.absoluteFile == directory.canonicalFile &&
                File(directory, "console.log").let { it.isFile && it.absoluteFile == it.canonicalFile }
        }.map { Session(it.name, File(it, "console.log").lastModified()) }
            .sortedByDescending { it.modified }
    }

    /** One attachable text file; only the selected runtime session, never saves or identity files. */
    fun writeText(context: Context, destination: Uri, sessionId: String) {
        val root = logsRoot(context)
        val session = sessions(context).firstOrNull { it.id == sessionId }
            ?: error("The selected game session is no longer available. Choose it again.")
        val directory = File(root, session.id)
        val files = directory.listFiles().orEmpty().filter {
            it.isFile && it.absoluteFile == it.canonicalFile &&
                (it.name == "console.log" || (it.name.startsWith("crash_") && it.extension == "txt"))
        }.sortedWith(compareByDescending<File> { it.name == "console.log" }.thenByDescending { it.lastModified() })
            .take(MAX_FILES)
        val output = context.contentResolver.openOutputStream(destination, "w")
            ?: error("The chosen destination could not be opened.")
        output.buffered().use { out ->
            out.write(buildString {
                appendLine("KartPad diagnostic log — modified WiiCompiled build")
                appendLine("Review before attaching on GitHub. Nothing was uploaded.")
                appendLine("Export-time app: ${BuildConfig.VERSION_NAME} (${BuildConfig.VERSION_CODE})")
                appendLine("Export-time device: ${android.os.Build.MANUFACTURER} ${android.os.Build.MODEL}; API ${android.os.Build.VERSION.SDK_INT}")
                appendLine("Selected session: ${session.id}; console last written (Unix ms): ${session.modified}")
                appendLine("Older session version must be read from its console header; otherwise unknown.")
                appendLine("Only console.log and crash text from this session follow. Each is capped at 256 KiB.")
            }.toByteArray())
            for (file in files) {
                out.write("\n--- ${file.name} ---\n".toByteArray())
                RandomAccessFile(file, "r").use { input ->
                    val size = input.length()
                    val cap = 256 * 1024
                    if (size <= cap) {
                        val bytes = ByteArray(size.toInt())
                        input.readFully(bytes)
                        out.write(bytes)
                    } else {
                        val header = ByteArray(16 * 1024)
                        input.readFully(header)
                        out.write(header)
                        val marker = "\n[KartPad: middle omitted; recent tail follows]\n".toByteArray()
                        out.write(marker)
                        val tail = ByteArray(cap - header.size - marker.size)
                        input.seek(size - tail.size)
                        input.readFully(tail)
                        out.write(tail)
                    }
                }
            }
        }
    }

    fun write(context: Context, destination: Uri, sessionId: String? = null) {
        val root = logsRoot(context)
        val available = sessions(context)
        val session = if (sessionId == null) available.firstOrNull()
            else available.firstOrNull { it.id == sessionId }
                ?: error("The selected game session is no longer available. Choose it again.")
        val directory = session?.let { File(root, it.id).canonicalFile }
        // One game session only. Root-level health history may cover unrelated runs.
        val files = directory?.listFiles().orEmpty()
            .filter { it.isFile && (it.name == "console.log" || (it.name.startsWith("crash_") && it.extension == "txt")) }
            .filter { it.absoluteFile == it.canonicalFile }
            .sortedWith(compareByDescending<File> { it.name == "console.log" }.thenByDescending { it.lastModified() })
            .take(MAX_FILES)
        val output = context.contentResolver.openOutputStream(destination, "w")
            ?: error("The chosen destination could not be opened.")
        ZipOutputStream(output.buffered()).use { zip ->
            zip.putNextEntry(ZipEntry("README.txt"))
            zip.write(buildString {
                appendLine("Private KartPad diagnostics from a modified WiiCompiled build. Review before sharing.")
                appendLine("Export-time app version (not necessarily this session): ${BuildConfig.VERSION_NAME} (${BuildConfig.VERSION_CODE})")
                appendLine("Export-time device: ${android.os.Build.MANUFACTURER} ${android.os.Build.MODEL}; API ${android.os.Build.VERSION.SDK_INT}")
                appendLine("report-context.json describes export time, not the source/version of older logs.")
                appendLine("The selected console.log header is retained. If it has no version, the session runtime version is unknown.")
                appendLine("Selected game session: ${session?.id ?: "none available"}")
                appendLine("Session console last-written time (Unix ms): ${session?.modified ?: "unavailable"}")
                appendLine("Read Logs/${session?.id ?: "<no session>"}/console.log and any crash text from the same folder.")
                appendLine("Runtime logs are from this session. OS-exits separately contains up to three recent app ANR/native-crash traces and their timestamps, when Android retains them.")
                appendLine("Each log contains at most $MAX_FILE_BYTES bytes: its original header and recent tail, with an explicit gap marker if shortened.")
                appendLine("Files may contain private details. Share only reviewed relevant text, never this entire private ZIP or game data.")
                appendLine("Log files: ${files.size}")
            }.toByteArray())
            zip.closeEntry()
            zip.putNextEntry(ZipEntry("report-context.json"))
            zip.write(KartPadReportContext.snapshot(context, null).toString(2).toByteArray())
            zip.closeEntry()
            KartPadExitTraces.write(context, zip)
            val buffer = ByteArray(32 * 1024)
            for (file in files) {
                zip.putNextEntry(ZipEntry("Logs/" + file.relativeTo(root).invariantSeparatorsPath))
                RandomAccessFile(file, "r").use { input ->
                    val size = input.length()
                    var remaining = size
                    if (size > MAX_FILE_BYTES) {
                        val header = ByteArray(16 * 1024)
                        input.readFully(header)
                        zip.write(header)
                        val marker = "\n\n[KartPad export: middle of log omitted; recent tail follows]\n\n".toByteArray()
                        zip.write(marker)
                        remaining = MAX_FILE_BYTES - header.size - marker.size
                        input.seek(size - remaining)
                    }
                    while (remaining > 0) {
                        val count = input.read(buffer, 0, minOf(buffer.size.toLong(), remaining).toInt())
                        if (count < 0) break
                        zip.write(buffer, 0, count)
                        remaining -= count
                    }
                }
                zip.closeEntry()
            }
        }
    }
}
