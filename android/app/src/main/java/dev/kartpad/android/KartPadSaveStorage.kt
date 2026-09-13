package dev.kartpad.android

import android.util.AtomicFile
import java.io.File
import java.util.UUID
import java.util.zip.CRC32

/** Validates and stages exact Mario Kart Wii RKSYS backup/restore operations. */
internal object KartPadSaveStorage {
    const val SAVE_BYTES = 0x2bc000
    private const val CORE_CRC_OFFSET = 0x27ffc
    private val magic = "RKSD0006".toByteArray(Charsets.US_ASCII)

    val profiles = listOf("original", "retro_rewind", "retro_rewind_separate")

    fun title(profile: String): String {
        require(profile in profiles) { "Unknown save profile." }
        return KartPadIdentityStorage.titles.getValue(profile)
    }

    fun active(filesDir: File, profile: String = "original"): File {
        require(profile in profiles) { "Unknown save profile." }
        return File(filesDir, "KartPad/${KartPadIdentityStorage.paths.getValue(profile)}")
    }

    private fun pending(filesDir: File, profile: String): File {
        title(profile)
        // Keep the original filename so pre-upgrade restores retain their target.
        val name = if (profile == "original") "rksys.dat" else "$profile.dat"
        return File(filesDir, "KartPad/PendingSaves/$name")
    }

    fun hasPending(filesDir: File): Boolean = KartPadRatingStorage.hasPending(filesDir) || profiles.any { hasPending(filesDir, it) }

    fun hasPending(filesDir: File, profile: String): Boolean = pending(filesDir, profile).isFile

    fun readActive(filesDir: File, profile: String = "original"): ByteArray {
        val file = active(filesDir, profile)
        require(file.isFile) { "No ${title(profile)} save exists yet." }
        return readExact(file).also(::validate)
    }

    fun writePending(filesDir: File, data: ByteArray, profile: String = "original") {
        require(!KartPadIdentityStorage.hasPending(filesDir)) { "Apply pending identity edits before restoring a save." }
        require(!hasPending(filesDir, profile)) { "Restart to apply this profile's pending restore first." }
        require(!KartPadRatingStorage.hasPending(filesDir)) { "Restart to apply the pending rating restore first." }
        validate(data)
        val file = pending(filesDir, profile)
        check(file.parentFile?.let { it.isDirectory || it.mkdirs() } == true) {
            "Save staging is unavailable."
        }
        writeAtomic(file, data)
    }

    /** Applies a validated restore before SDL starts and retains the prior save. */
    fun applyPending(filesDir: File): String? {
        for (profile in profiles) {
            applyPending(filesDir, profile)?.let { return it }
        }
        return KartPadRatingStorage.applyPending(filesDir)
    }

    private fun applyPending(filesDir: File, profile: String): String? {
        val pending = pending(filesDir, profile)
        if (!pending.isFile) return null
        return runCatching {
            check(!KartPadIdentityStorage.hasPending(filesDir))
            val replacement = readExact(pending).also(::validate)
            val active = active(filesDir, profile)
            check(active.parentFile?.let { it.isDirectory || it.mkdirs() } == true) {
                "Save storage is unavailable."
            }
            if (active.isFile) {
                val current = readExact(active).also(::validate)
                val backups = File(filesDir, "KartPad/SaveBackups")
                check(backups.isDirectory || backups.mkdirs()) { "Save backup storage is unavailable." }
                val prefix = if (profile == "original") "rksys" else profile
                val backup = File(backups, "$prefix-${System.currentTimeMillis()}-${UUID.randomUUID()}.dat")
                writeAtomic(backup, current)
            }
            writeAtomic(active, replacement)
            check(pending.delete()) { "The pending save restore could not be finalized." }
            pending.parentFile?.delete()
        }.exceptionOrNull()?.let { "The pending ${title(profile)} save restore could not be applied safely. It remains staged; your existing save and any backups have been retained." }
    }

    fun validate(data: ByteArray) {
        require(data.size == SAVE_BYTES) { "A Mario Kart Wii save must be exactly $SAVE_BYTES bytes." }
        require(data.copyOfRange(0, magic.size).contentEquals(magic)) {
            "The selected file is not a supported Mario Kart Wii RKSYS save."
        }
        val stored = ((data[CORE_CRC_OFFSET].toLong() and 0xff) shl 24) or
            ((data[CORE_CRC_OFFSET + 1].toLong() and 0xff) shl 16) or
            ((data[CORE_CRC_OFFSET + 2].toLong() and 0xff) shl 8) or
            (data[CORE_CRC_OFFSET + 3].toLong() and 0xff)
        val crc = CRC32().apply { update(data, 0, CORE_CRC_OFFSET) }.value
        require(stored == crc) { "The selected Mario Kart Wii save has an invalid checksum." }
    }

    private fun readExact(file: File): ByteArray {
        require(file.length() == SAVE_BYTES.toLong()) {
            "A Mario Kart Wii save must be exactly $SAVE_BYTES bytes."
        }
        return file.readBytes()
    }

    private fun writeAtomic(file: File, data: ByteArray) {
        val atomic = AtomicFile(file)
        val output = atomic.startWrite()
        try {
            output.write(data)
            atomic.finishWrite(output)
        } catch (error: Throwable) {
            atomic.failWrite(output)
            throw error
        }
    }
}
