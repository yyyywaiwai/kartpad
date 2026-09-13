package dev.kartpad.android

import android.util.AtomicFile
import android.system.Os
import android.system.OsConstants
import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.Base64
import java.util.UUID
import org.json.JSONObject

/** Manual companion restore to an existing Retro save; publication happens before SDL starts. */
internal object KartPadRatingStorage {
    private fun pending(files: File) = File(files, "KartPad/PendingRating.json")
    // Keep a durable terminal record rather than unlinking the request: an
    // interrupted directory sync must never resurrect a completed restore.
    private val finalized = "{\"finalized\":true}".toByteArray()
    private fun isFinalized(file: File) = file.isFile &&
        file.length() == finalized.size.toLong() && file.readBytes().contentEquals(finalized)
    fun hasPending(files: File) = pending(files).let { it.isFile && !isFinalized(it) }

    /** Chooser-only cancellation while no game is paused; preserves current ratings and backups. */
    fun cancelPending(files: File) {
        val file = pending(files)
        if (file.exists()) write(file, finalized)
    }

    fun profileIds(save: ByteArray): Set<Int> {
        KartPadSaveStorage.validate(save)
        val data = ByteBuffer.wrap(save).order(ByteOrder.BIG_ENDIAN)
        val ids = linkedSetOf<Int>()
        repeat(4) { slot ->
            val license = 8 + slot * 0x8cc0
            if (data.getInt(license) == 0x524b5044) {
                val id = data.getInt(license + 0x40 + 0x1c)
                if (id != 0) {
                    require(id in 1 until 1_000_000_000 && ids.add(id)) {
                        "The save has an unsupported or duplicate online profile."
                    }
                }
            }
        }
        require(ids.isNotEmpty()) { "This save has no online profile to match ratings to." }
        return ids
    }

    private fun saveIds(files: File, profile: String): Set<Int> {
        require(profile == "retro_rewind" || profile == "retro_rewind_separate") {
            "Rating restore requires a Retro Rewind save profile."
        }
        return profileIds(KartPadSaveStorage.readActive(files, profile))
    }

    private fun target(files: File): File {
        val config = File(files, "KartPad/Config.toml")
        // This is deliberately a restricted syntax check, not a second TOML parser.
        // Accept the shell's simple scalar configuration only. Quoted/dotted keys,
        // inline tables and multiline values require the runtime parser to resolve
        // safely; refuse them instead of guessing at the default NAND.
        if (config.isFile) {
            require(config.length() <= 256 * 1024) { "Unsupported rating restore configuration." }
            val scalar = Regex("""(?:"(?:[^"\\\r\n]|\\[^\r\n])*"|'[^'\r\n]*'|true|false|[+-]?[0-9][0-9_.eE+-]*)\s*(?:#.*)?""")
            for (line in config.readLines()) {
                val text = line.trim()
                if (text.isEmpty() || text.startsWith("#")) continue
                if (Regex("""\[[A-Za-z0-9_-]+]\s*(?:#.*)?""").matches(text)) continue
                val assignment = Regex("""([A-Za-z0-9_-]+)\s*=\s*(.*)""").matchEntire(text)
                require(assignment != null && assignment.groupValues[1] != "nand_root" &&
                    scalar.matches(assignment.groupValues[2])) {
                    "Rating restore requires the default NAND and a simple configuration. Custom NAND or advanced TOML syntax is not supported; your configuration is unchanged."
                }
            }
        }
        return File(files, "KartPad/NAND/shared2/Pulsar/RetroRewind6/RRRating.pul").also {
            require(it.isFile) { "Start Retro Rewind with this save and close it before importing ratings; no local rating file exists yet." }
        }
    }

    private fun readRating(file: File): ByteArray {
        require(file.length() == KartPadRatingCompanion.FILE_BYTES.toLong()) { "Unsupported rating file length." }
        return file.readBytes().also(KartPadRatingCompanion::validate)
    }

    fun stage(files: File, profile: String, source: ByteArray) {
        require(!KartPadSaveStorage.hasPending(files) && !KartPadIdentityStorage.hasPending(files)) {
            "Restart to apply pending save, rating or identity changes first."
        }
        val ids = saveIds(files, profile)
        // Validate the proposed merge now, but merge again against the latest destination at startup.
        KartPadRatingCompanion.merge(source, readRating(target(files)), ids)
        val request = JSONObject().put("profile", profile)
            .put("ids", ids.sorted().joinToString(","))
            .put("source", Base64.getEncoder().encodeToString(source))
        write(pending(files), request.toString().toByteArray())
    }

    fun applyPending(files: File): String? {
        val requestFile = pending(files)
        if (!requestFile.isFile) return null
        return runCatching {
            if (isFinalized(requestFile)) {
                // Retry the checked barrier even if the previous terminal write
                // became visible but failed before durability was established.
                write(requestFile, finalized)
                return@runCatching
            }
            check(!KartPadIdentityStorage.hasPending(files))
            require(requestFile.length() <= 4096) { "Invalid pending rating restore." }
            val request = JSONObject(requestFile.readText())
            val ids = saveIds(files, request.getString("profile"))
            require(ids.sorted().joinToString(",") == request.getString("ids")) {
                "The save's online profiles changed after staging."
            }
            val source = Base64.getDecoder().decode(request.getString("source"))
            val active = target(files)
            val current = readRating(active)
            val replacement = KartPadRatingCompanion.merge(source, current, ids)
            val backup = File(files, "KartPad/SaveBackups/ratings-${UUID.randomUUID()}.pul")
            write(backup, current)
            write(active, replacement)
            write(requestFile, finalized)
        }.exceptionOrNull()?.let {
            "The pending rating restore could not be completed. Gameplay is stopped; the request or completion record and any backups are retained."
        }
    }

    private fun write(file: File, bytes: ByteArray) {
        val parent = checkNotNull(file.parentFile)
        check(parent.isDirectory || parent.mkdir())
        // Persist a newly created SaveBackups directory as well as its contents.
        // Repeat this barrier on retry even if a preceding mkdir already succeeded.
        syncDirectory(checkNotNull(parent.parentFile))
        val atomic = AtomicFile(file)
        val stream = atomic.startWrite()
        try {
            stream.write(bytes)
            // AtomicFile.finishWrite can only log sync/rename failures. A checked
            // sync and publication verification must precede request deletion.
            Os.fsync(stream.fd)
            atomic.finishWrite(stream)
            check(!File(file.path + ".new").exists() && !File(file.path + ".bak").exists() && file.isFile &&
                file.length() == bytes.size.toLong() && file.readBytes().contentEquals(bytes)) {
                "Rating restore publication did not complete."
            }
            syncDirectory(parent)
        } catch (error: Throwable) { atomic.failWrite(stream); throw error }
    }

    private fun syncDirectory(file: File) {
        check(file.isDirectory)
        val directory = Os.open(file.path, OsConstants.O_RDONLY, 0)
        try { Os.fsync(directory) } finally { Os.close(directory) }
    }
}
