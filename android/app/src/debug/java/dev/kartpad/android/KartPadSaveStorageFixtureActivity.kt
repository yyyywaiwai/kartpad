package dev.kartpad.android

import android.app.Activity
import android.os.Bundle
import android.util.Log
import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.zip.CRC32

/** Debug-only, synthetic validation of save export/stage/apply/backup storage. */
internal class KartPadSaveStorageFixtureActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (savedInstanceState != null) return
        Thread {
            val root = File(cacheDir, "save-storage-fixture")
            runCatching { runFixture(root) }
                .onSuccess {
                    Log.i(
                        TAG,
                        "A6 save storage passed export=validated restore=staged " +
                            "active=replaced backup=preserved corrupt=rejected",
                    )
                }
                .onFailure { Log.e(TAG, "A6 save storage failed", it) }
            root.deleteRecursively()
            runOnUiThread { finish() }
        }.start()
    }

    private fun runFixture(root: File) {
        check(!root.exists() || root.deleteRecursively()) { "fixture cleanup failed" }
        val original = validSave(0x31)
        val replacement = validSave(0x72)
        val active = KartPadSaveStorage.active(root)
        check(active.parentFile?.mkdirs() == true) { "active save directory unavailable" }
        active.writeBytes(original)

        check(KartPadSaveStorage.readActive(root).contentEquals(original)) {
            "validated export did not return the active save"
        }
        KartPadSaveStorage.writePending(root, replacement)
        check(KartPadSaveStorage.hasPending(root)) { "restore was not staged" }
        check(KartPadSaveStorage.applyPending(root) == null) { "staged restore failed" }
        check(!KartPadSaveStorage.hasPending(root)) { "staged restore was not finalized" }
        check(KartPadSaveStorage.readActive(root).contentEquals(replacement)) {
            "replacement did not become active"
        }

        val backups = File(root, "KartPad/SaveBackups").listFiles()?.toList().orEmpty()
        check(backups.size == 1 && backups.single().readBytes().contentEquals(original)) {
            "prior active save was not retained exactly once"
        }
        val corrupt = replacement.copyOf().also { it[0x100] = (it[0x100].toInt() xor 1).toByte() }
        check(runCatching { KartPadSaveStorage.validate(corrupt) }.isFailure) {
            "checksum-corrupt save was accepted"
        }
        // Exercise Android's real AtomicFile with all three target profiles.
        for (profile in KartPadSaveStorage.profiles) {
            KartPadSaveStorage.active(root, profile).apply {
                parentFile?.mkdirs()
                writeBytes(original)
            }
        }
        for (profile in KartPadSaveStorage.profiles) {
            val before = KartPadSaveStorage.profiles.associateWith {
                KartPadSaveStorage.readActive(root, it)
            }
            KartPadSaveStorage.writePending(root, replacement, profile)
            check(KartPadSaveStorage.applyPending(root) == null)
            check(KartPadSaveStorage.readActive(root, profile).contentEquals(replacement))
            for (other in KartPadSaveStorage.profiles - profile) {
                check(KartPadSaveStorage.readActive(root, other).contentEquals(before.getValue(other)))
            }
        }
        runRatingFixture(root)
    }

    private fun runRatingFixture(root: File) {
        fun buffer(bytes: ByteArray) = ByteBuffer.wrap(bytes).order(ByteOrder.BIG_ENDIAN)
        val save = validSave(0).also { bytes ->
            buffer(bytes).putInt(8, 0x524b5044).putInt(8 + 0x5c, 10)
                .putInt(0x27ffc, CRC32().apply { update(bytes, 0, 0x27ffc) }.value.toInt())
        }
        val source = ByteArray(1640).also { bytes ->
            buffer(bytes).putInt(0, 0x52525254).putShort(4, 1).putShort(6, 100)
                .putInt(8, 10).putFloat(12, 90.5f).putFloat(16, 25f).putInt(20, 1)
        }
        val previous = source.copyOf().also { buffer(it).putInt(8, 20) }
        val target = File(root, "KartPad/NAND/shared2/Pulsar/RetroRewind6/RRRating.pul")
        target.parentFile?.mkdirs()
        for (profile in listOf("retro_rewind", "retro_rewind_separate")) {
            KartPadSaveStorage.active(root, profile).writeBytes(save)
            target.writeBytes(previous)
            KartPadRatingStorage.stage(root, profile, source)
            check(target.readBytes().contentEquals(previous))
            check(KartPadSaveStorage.applyPending(root) == null)
            check(!KartPadSaveStorage.hasPending(root))
            check(target.readBytes().contentEquals(KartPadRatingCompanion.merge(source, previous, setOf(10))))
            check(File(root, "KartPad/SaveBackups").listFiles().orEmpty().any {
                it.extension == "pul" && it.readBytes().contentEquals(previous)
            })
        }
        Log.i(TAG, "Rating storage passed profiles=2 backup=preserved unrelated=preserved pending=cleared")
    }

    private fun validSave(marker: Int): ByteArray {
        val data = ByteArray(KartPadSaveStorage.SAVE_BYTES)
        "RKSD0006".toByteArray(Charsets.US_ASCII).copyInto(data)
        data[0x100] = marker.toByte()
        val crcOffset = 0x27ffc
        val crc = CRC32().apply { update(data, 0, crcOffset) }.value
        data[crcOffset] = (crc ushr 24).toByte()
        data[crcOffset + 1] = (crc ushr 16).toByte()
        data[crcOffset + 2] = (crc ushr 8).toByte()
        data[crcOffset + 3] = crc.toByte()
        return data
    }

    private companion object {
        const val TAG = "KartPadFixture"
    }
}
