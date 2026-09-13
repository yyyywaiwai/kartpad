package dev.kartpad.android

import android.util.AtomicFile
import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.file.Files
import java.util.zip.CRC32

fun testRatingStorage() {
    var checks = 0
    fun verify(value: Boolean) { check(value); checks++ }
    fun reject(block: () -> Unit) { verify(runCatching(block).isFailure) }
    fun view(bytes: ByteArray) = ByteBuffer.wrap(bytes).order(ByteOrder.BIG_ENDIAN)
    fun save(vararg ids: Int) = ByteArray(KartPadSaveStorage.SAVE_BYTES).also { bytes ->
        "RKSD0006".toByteArray().copyInto(bytes)
        ids.forEachIndexed { slot, id ->
            view(bytes).putInt(8 + slot * 0x8cc0, 0x524b5044)
                .putInt(8 + slot * 0x8cc0 + 0x5c, id)
        }
        view(bytes).putInt(0x27ffc, CRC32().apply { update(bytes, 0, 0x27ffc) }.value.toInt())
    }
    fun ratings(vararg ids: Int) = ByteArray(1640).also { bytes ->
        val b = view(bytes)
        b.putInt(0, 0x52525254).putShort(4, 1).putShort(6, 100)
        ids.forEachIndexed { slot, id ->
            b.putInt(8 + slot * 16, id).putFloat(12 + slot * 16, 99.25f)
                .putFloat(16 + slot * 16, 20f).putInt(20 + slot * 16, 1)
        }
    }
    verify(KartPadRatingStorage.profileIds(save(10, 0, 20)) == setOf(10, 20))
    for (bytes in listOf(save(), save(10, 10), save(-1), save(1_000_000_000),
        save(10).apply { this[200] = 1 })) reject { KartPadRatingStorage.profileIds(bytes) }
    for (profile in listOf("retro_rewind", "retro_rewind_separate")) {
        val root = Files.createTempDirectory("kartpad-rating-storage-").toFile()
        try {
            val activeSave = KartPadSaveStorage.active(root, profile).apply { parentFile.mkdirs(); writeBytes(save(10)) }
            val rating = File(root, "KartPad/NAND/shared2/Pulsar/RetroRewind6/RRRating.pul")
            val prior = ratings(20)
            rating.parentFile.mkdirs(); rating.writeBytes(prior)
            val source = ratings(10, 30)
            reject { KartPadRatingStorage.stage(root, "original", source) }
            reject { KartPadRatingStorage.stage(root, profile, ratings(99)) }
            val identity = File(root, "KartPad/PendingAndroidIdentity.json")
            identity.writeText("{}")
            reject { KartPadRatingStorage.stage(root, profile, source) }
            identity.delete()
            AtomicFile.silentFailSuffix = "/PendingRating.json"
            reject { KartPadRatingStorage.stage(root, profile, source) }
            verify(!KartPadRatingStorage.hasPending(root))
            verify(rating.readBytes().contentEquals(prior))
            AtomicFile.silentFailSuffix = null
            KartPadRatingStorage.stage(root, profile, source)
            identity.writeText("{}")
            verify(KartPadSaveStorage.applyPending(root) != null)
            verify(rating.readBytes().contentEquals(prior))
            identity.delete()
            verify(KartPadSaveStorage.hasPending(root))
            verify(rating.readBytes().contentEquals(prior))
            reject { KartPadRatingStorage.stage(root, profile, source) }
            reject { KartPadSaveStorage.writePending(root, save(10), profile) }
            // Change online identity after staging: fail closed, leaving the source and live bytes.
            activeSave.writeBytes(save(11))
            verify(KartPadSaveStorage.applyPending(root) != null)
            verify(rating.readBytes().contentEquals(prior))
            activeSave.writeBytes(save(10))
            AtomicFile.failSuffix = ".pul" // Fail the backup itself: active publication must not begin.
            verify(KartPadSaveStorage.applyPending(root) != null)
            verify(rating.readBytes().contentEquals(prior))
            verify(File(root, "KartPad/SaveBackups").listFiles().orEmpty().isEmpty())
            AtomicFile.failSuffix = "/RRRating.pul"
            verify(KartPadSaveStorage.applyPending(root) != null)
            verify(rating.readBytes().contentEquals(prior))
            verify(KartPadSaveStorage.hasPending(root))
            AtomicFile.failSuffix = null
            // Nonthrowing AtomicFile publication failures must not consume the request.
            for (suffix in listOf(".pul", "/RRRating.pul", "backup-only")) {
                val beforeBackups = File(root, "KartPad/SaveBackups").listFiles().orEmpty().size
                AtomicFile.silentBackupOnly = suffix == "backup-only"
                AtomicFile.silentFailSuffix = suffix.takeUnless { AtomicFile.silentBackupOnly }
                verify(KartPadSaveStorage.applyPending(root) != null)
                verify(KartPadSaveStorage.hasPending(root))
                verify(rating.readBytes().contentEquals(prior))
                if (suffix != "/RRRating.pul") verify(File(root, "KartPad/SaveBackups").listFiles().orEmpty().size == beforeBackups)
            }
            AtomicFile.silentBackupOnly = false
            AtomicFile.silentFailSuffix = null
            // Checked data/directory sync failures stop before publishing live ratings.
            for (suffix in listOf(".pul", "/RRRating.pul", "/SaveBackups", "/KartPad")) {
                android.system.Os.failSyncSuffix = suffix
                verify(KartPadSaveStorage.applyPending(root) != null)
                verify(KartPadSaveStorage.hasPending(root))
                verify(rating.readBytes().contentEquals(prior))
            }
            android.system.Os.failSyncSuffix = "/RetroRewind6"
            verify(KartPadSaveStorage.applyPending(root) != null)
            verify(KartPadSaveStorage.hasPending(root))
            verify(File(root, "KartPad/SaveBackups").listFiles().orEmpty().any { it.readBytes().contentEquals(prior) })
            // Simulated publication happened but directory sync failed: no gameplay or request deletion.
            verify(rating.readBytes().contentEquals(KartPadRatingCompanion.merge(source, prior, setOf(10))))
            android.system.Os.failSyncSuffix = null
            rating.writeBytes(prior)
            // Preserve an unrelated record written after the initial staging.
            val latest = ratings(20, 40)
            rating.writeBytes(latest)
            // A logged failure of AtomicFile's redundant sync is safe only because
            // the checked fsync above already succeeded before finishWrite.
            AtomicFile.silentSyncFailureSuffix = ".pul"
            verify(KartPadSaveStorage.applyPending(root) == null)
            AtomicFile.silentSyncFailureSuffix = null
            verify(!KartPadSaveStorage.hasPending(root))
            verify(activeSave.readBytes().contentEquals(save(10)))
            verify(rating.readBytes().contentEquals(KartPadRatingCompanion.merge(source, latest, setOf(10))))
            val backups = File(root, "KartPad/SaveBackups").listFiles()!!
            verify(backups.any { it.readBytes().contentEquals(prior) })
            verify(backups.any { it.readBytes().contentEquals(latest) })
            KartPadSaveStorage.writePending(root, save(10), profile)
            reject { KartPadRatingStorage.stage(root, profile, source) }
            verify(KartPadSaveStorage.applyPending(root) == null)
            File(root, "KartPad/Config.toml").writeText("[paths]\nnand_root = \"elsewhere\"\n")
            reject { KartPadRatingStorage.stage(root, profile, source) }
            val config = File(root, "KartPad/Config.toml")
            for (text in listOf(
                "[paths]\n\"nand_root\" = \"elsewhere\"",
                "[paths]\n'nand_root' = 'elsewhere'",
                "paths.nand_root = \"elsewhere\"",
                "\"paths\".\"nand_root\" = \"elsewhere\"",
                "paths = { nand_root = \"elsewhere\" }",
                "paths = { \"nand_root\" = \"elsewhere\" }",
                "[\"paths\"]\nnand_root = \"elsewhere\"",
                "[paths]\n\"na\\u006ed_root\" = \"elsewhere\""
            )) {
                config.writeText(text)
                reject { KartPadRatingStorage.stage(root, profile, source) }
                verify(!KartPadRatingStorage.hasPending(root))
                verify(rating.readBytes().contentEquals(KartPadRatingCompanion.merge(source, latest, setOf(10))))
            }
            config.writeText("# nand_root = \"unused\"\n[paths]\ndvd_root = \"GameData\" # normal config\n[video]\nresolution_scale = 1.0\n")
            KartPadRatingStorage.stage(root, profile, source)
            config.writeText("paths = { nand_root = \"elsewhere\" }")
            val beforeRefusal = rating.readBytes()
            verify(KartPadRatingStorage.applyPending(root) != null)
            verify(KartPadRatingStorage.hasPending(root))
            verify(rating.readBytes().contentEquals(beforeRefusal))
            config.delete()
            KartPadRatingStorage.cancelPending(root)
            KartPadRatingStorage.stage(root, profile, source)
            val beforeCancel = rating.readBytes()
            KartPadRatingStorage.cancelPending(root)
            verify(!KartPadSaveStorage.hasPending(root))
            verify(rating.readBytes().contentEquals(beforeCancel))
            KartPadRatingStorage.cancelPending(root)
            // Completion/cancellation terminal markers survive restart without replay.
            for (cancel in listOf(false, true)) {
                KartPadRatingStorage.stage(root, profile, source)
                android.system.Os.failSyncSuffix = "/KartPad"
                android.system.Os.failSyncSkip = if (cancel) 0 else 1
                if (cancel) reject { KartPadRatingStorage.cancelPending(root) }
                else verify(KartPadRatingStorage.applyPending(root) != null)
                val terminal = File(root, "KartPad/PendingRating.json")
                verify(terminal.readText() == "{\"finalized\":true}")
                // Restart with barrier still failing must stop, keeping terminal record.
                verify(KartPadRatingStorage.applyPending(root) != null)
                verify(terminal.isFile)
                android.system.Os.failSyncSuffix = null
                val newer = ratings(10, 40).also { view(it).putFloat(12, 123.5f) }
                rating.writeBytes(newer)
                verify(KartPadRatingStorage.applyPending(root) == null)
                verify(rating.readBytes().contentEquals(newer))
                verify(!KartPadRatingStorage.hasPending(root))
                // A later restart still cannot replay the original source.
                verify(KartPadRatingStorage.applyPending(root) == null)
                verify(rating.readBytes().contentEquals(newer))
            }
            rating.delete()
            reject { KartPadRatingStorage.stage(root, profile, source) }
        } finally { AtomicFile.failSuffix = null; AtomicFile.silentFailSuffix = null; AtomicFile.silentBackupOnly = false; AtomicFile.silentSyncFailureSuffix = null; android.system.Os.failSyncSuffix = null; root.deleteRecursively() }
    }
    println("Android rating storage passed: $checks checks (synthetic files only)")
}
