package dev.kartpad.android

import android.util.AtomicFile
import java.io.File
import java.nio.file.Files
import java.util.zip.CRC32

/** Exercises real save storage on synthetic files, including interrupted writes. */
fun testSaveProfiles(fixtures: File) {
    val root = Files.createTempDirectory("kartpad-save-profiles-").toFile()
    val sample = File(fixtures, "save.dat").readBytes()
    fun save(marker: Int) = sample.copyOf().apply saveBytes@{
        this[0x100] = marker.toByte()
        val crc = CRC32().apply { update(this@saveBytes, 0, 0x27ffc) }.value
        repeat(4) { this[0x27ffc + it] = (crc shr (24 - it * 8)).toByte() }
    }
    fun seed(profile: String, bytes: ByteArray) {
        KartPadSaveStorage.active(root, profile).apply { parentFile.mkdirs(); writeBytes(bytes) }
    }
    fun snapshots() = KartPadSaveStorage.profiles.associateWith { KartPadSaveStorage.readActive(root, it) }
    fun backups() = File(root, "KartPad/SaveBackups").listFiles().orEmpty().toList()
    try {
        val mii = File(root, "KartPad/${KartPadIdentityStorage.paths.getValue("mii")}")
        mii.parentFile.mkdirs()
        File(fixtures, "mii.dat").copyTo(mii)
        val originalMii = mii.readBytes()
        KartPadSaveStorage.profiles.forEachIndexed { index, profile -> seed(profile, save(index)) }
        for ((index, profile) in KartPadSaveStorage.profiles.withIndex()) {
            val before = snapshots()
            val oldBackups = backups().toSet()
            val replacement = save(20 + index)
            KartPadSaveStorage.writePending(root, replacement, profile)
            check(KartPadSaveStorage.hasPending(root))
            check(KartPadSaveStorage.hasPending(root, profile))
            check(runCatching { KartPadSaveStorage.writePending(root, save(90), profile) }.isFailure)
            check(snapshots().all { (key, bytes) -> bytes.contentEquals(before.getValue(key)) })
            // Identity edits must see restores for every profile, including Retro.
            val record = KartPadIdentityStorage.records(root, false).first()
            check(runCatching { KartPadIdentityStorage.stage(root, record, false, "Blocked") }.isFailure)
            check(KartPadSaveStorage.applyPending(root) == null)
            check(!KartPadSaveStorage.hasPending(root))
            check(KartPadSaveStorage.readActive(root, profile).contentEquals(replacement))
            for (other in KartPadSaveStorage.profiles - profile)
                check(KartPadSaveStorage.readActive(root, other).contentEquals(before.getValue(other)))
            val newBackup = (backups().toSet() - oldBackups).single()
            check(newBackup.readBytes().contentEquals(before.getValue(profile)))
            check(mii.readBytes().contentEquals(originalMii))
        }
        val before = snapshots()
        for (invalid in listOf(sample.copyOf(10), sample + byteArrayOf(0),
            sample.copyOf().apply { this[0] = 0 }, sample.copyOf().apply { this[0x100] = 99 })) {
            check(runCatching { KartPadSaveStorage.writePending(root, invalid, "retro_rewind") }.isFailure)
            check(!KartPadSaveStorage.hasPending(root))
        }
        for (invalidProfile in listOf("mii", "../original", "base", "")) {
            check(runCatching { KartPadSaveStorage.active(root, invalidProfile) }.isFailure)
            check(runCatching { KartPadSaveStorage.writePending(root, sample, invalidProfile) }.isFailure)
        }
        // A pre-upgrade pending file must still apply to Original only.
        File(root, "KartPad/PendingSaves/rksys.dat").apply { parentFile.mkdirs(); writeBytes(save(40)) }
        check(KartPadSaveStorage.applyPending(root) == null)
        check(KartPadSaveStorage.readActive(root).contentEquals(save(40)))
        check(KartPadSaveStorage.readActive(root, "retro_rewind").contentEquals(before.getValue("retro_rewind")))
        val record = KartPadIdentityStorage.records(root, false).first()
        KartPadIdentityStorage.stage(root, record, false, "Racer")
        check(runCatching { KartPadSaveStorage.writePending(root, sample, "retro_rewind") }.isFailure)
        check(KartPadIdentityStorage.applyPending(root) == null)
        // Failed publication retains the old target, staged replacement and backup.
        val oldRetro = KartPadSaveStorage.readActive(root, "retro_rewind")
        KartPadSaveStorage.writePending(root, save(50), "retro_rewind")
        AtomicFile.failSuffix = "/RetroWFC/RMCP/rksys.dat"
        check(KartPadSaveStorage.applyPending(root) != null)
        check(KartPadSaveStorage.hasPending(root, "retro_rewind"))
        check(KartPadSaveStorage.readActive(root, "retro_rewind").contentEquals(oldRetro))
        check(backups().any { it.readBytes().contentEquals(oldRetro) })
        AtomicFile.failSuffix = null
        check(KartPadSaveStorage.applyPending(root) == null)
        check(KartPadSaveStorage.readActive(root, "retro_rewind").contentEquals(save(50)))
        // First import into a profile with no existing save is supported.
        check(KartPadSaveStorage.active(root, "retro_rewind_separate").delete())
        KartPadSaveStorage.writePending(root, save(60), "retro_rewind_separate")
        check(KartPadSaveStorage.applyPending(root) == null)
        check(KartPadSaveStorage.readActive(root, "retro_rewind_separate").contentEquals(save(60)))
        // Corruption after staging must stop application and preserve every target.
        val beforeCorrupt = snapshots()
        KartPadSaveStorage.writePending(root, save(70), "retro_rewind")
        val pending = File(root, "KartPad/PendingSaves/retro_rewind.dat")
        pending.writeBytes(byteArrayOf(1, 2, 3))
        check(KartPadSaveStorage.applyPending(root) != null)
        check(KartPadSaveStorage.hasPending(root))
        check(snapshots().all { (key, bytes) -> bytes.contentEquals(beforeCorrupt.getValue(key)) })
        pending.writeBytes(save(70))
        KartPadSaveStorage.writePending(root, save(71), "retro_rewind_separate")
        check(KartPadSaveStorage.applyPending(root) == null)
        check(!KartPadSaveStorage.hasPending(root))
        check(KartPadSaveStorage.readActive(root, "retro_rewind").contentEquals(save(70)))
        check(KartPadSaveStorage.readActive(root, "retro_rewind_separate").contentEquals(save(71)))
        println("Android save profiles passed: all three targets, isolated export/restore, backups, legacy pending, invalid inputs, identity conflicts, interrupted publication, first import")
    } finally {
        AtomicFile.failSuffix = null
        root.deleteRecursively()
    }
}
