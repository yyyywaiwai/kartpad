package dev.kartpad.android

import android.util.AtomicFile
import org.json.JSONObject
import org.json.JSONArray
import java.io.File
import java.security.MessageDigest
import java.util.UUID

/** Stage one intent, then apply to the latest save at cold launch, with recoverable backups. */
internal object KartPadIdentityStorage {
    val paths = linkedMapOf(
        "original" to "NAND/title/00010004/524d4350/data/rksys.dat",
        "retro_rewind" to "RetroRewind/riivolution/save/RetroWFC/RMCP/rksys.dat",
        "retro_rewind_separate" to "RetroRewind/riivolution/save/RetroWFC2/RMCP/rksys.dat",
        "mii" to "NAND/shared2/menu/FaceLib/RFL_DB.dat",
    )
    val titles = mapOf("original" to "Original Mario Kart Wii", "retro_rewind" to "Retro Rewind",
        "retro_rewind_separate" to "Retro Rewind (Separate Save)", "mii" to "Mii")
    private fun root(files: File) = File(files, "KartPad")
    private fun journal(files: File) = File(root(files), "PendingAndroidIdentity.json")
    private fun pointer(files: File) = File(root(files), "PendingAndroidIdentityTransaction")
    private fun target(files: File, profile: String) = File(root(files), paths.getValue(profile))
    private fun readTarget(files: File, profile: String): ByteArray {
        val file = target(files, profile)
        require(file.length() == if (profile == "mii") 779968L else KartPadSaveStorage.SAVE_BYTES.toLong()) {
            "Identity data has an unexpected size."
        }
        return file.readBytes()
    }
    private fun write(file: File, bytes: ByteArray) {
        file.parentFile?.mkdirs()
        val atomic = AtomicFile(file)
        val stream = atomic.startWrite()
        try { stream.write(bytes); atomic.finishWrite(stream) }
        catch (error: Throwable) { atomic.failWrite(stream); throw error }
    }
    private fun hash(bytes: ByteArray) = MessageDigest.getInstance("SHA-256").digest(bytes)
    fun hasPending(files: File) = journal(files).isFile || pointer(files).isFile
    data class Record(val profile: String, val slot: Int, val name: String, val createId: String)
    fun records(files: File, miis: Boolean): List<Record> = paths.keys
        .filter { (it == "mii") == miis && target(files, it).isFile }
        .flatMap { profile ->
            nativeRecords(readTarget(files, profile), miis).toList().chunked(3).map {
                Record(profile, it[0].toInt(), it[1], it[2])
            }
        }
    fun stage(files: File, record: Record, delete: Boolean, name: String) {
        require(!hasPending(files)) { "Apply the pending identity change by fully closing and reopening KartPad before editing again." }
        require(!KartPadSaveStorage.hasPending(files) && !KartPadMiiStorage.hasPending(files)) {
            "Apply the pending save or Mii import first."
        }
        require(!delete || record.profile != "mii") { "Use the appearance manager for unused Miis." }
        val request = JSONObject().put("profile", record.profile).put("slot", record.slot)
            .put("createId", record.createId).put("delete", delete).put("name", name)
        // Validate immediately, but never stage an old whole-save snapshot.
        replacements(files, request)
        write(journal(files), request.toString().toByteArray())
    }
    private fun replacements(files: File, request: JSONObject): Map<String, ByteArray> {
        val profile = request.getString("profile")
        require(paths.containsKey(profile)) { "Unknown identity profile." }
        val id = request.getString("createId")
        val slot = request.getInt("slot")
        val name = request.getString("name").toByteArray(Charsets.UTF_16BE)
        val delete = request.getBoolean("delete")
        val result = linkedMapOf(profile to nativeEdit(readTarget(files, profile),
            if (profile == "mii") 2 else if (delete) 1 else 0, slot, id, name))
        if (profile == "mii") paths.keys.filter { it != "mii" && target(files, it).isFile }.forEach {
            result[it] = nativeEdit(readTarget(files, it), 3, slot, id, name)
        }
        else if (!delete && target(files, "mii").isFile) {
            // Match Apple's license rename: keep the selected license and its Mii
            // in sync, without directly rewriting other profiles' saves.
            val database = readTarget(files, "mii")
            val matching = nativeRecords(database, true).toList().chunked(3)
                .firstOrNull { it[2] == id }
            if (matching != null) result["mii"] = nativeEdit(database, 2, matching[0].toInt(), id, name)
        }
        return result
    }
    /** Called before SDL starts. Interrupted multi-file edits finish before guest writes resume. */
    fun applyPending(files: File): String? = runCatching {
        if (!hasPending(files)) return null
        if (!pointer(files).isFile) {
            require(journal(files).length() in 1..4096) { "Invalid pending identity request." }
            val changes = replacements(files, JSONObject(journal(files).readText()))
            val name = UUID.randomUUID().toString()
            val backup = File(root(files), "IdentityBackups/$name")
            val profiles = JSONArray()
            changes.forEach { (profile, bytes) ->
                write(File(backup, "$profile.before"), readTarget(files, profile))
                write(File(backup, "$profile.after"), bytes)
                profiles.put(profile)
            }
            write(File(backup, "profiles.json"), profiles.toString().toByteArray())
            write(pointer(files), name.toByteArray())
        }
        val name = pointer(files).readText()
        require(runCatching { UUID.fromString(name).toString() == name }.getOrDefault(false))
        val backup = File(root(files), "IdentityBackups/$name")
        val profiles = JSONArray(File(backup, "profiles.json").readText())
        val writes = (0 until profiles.length()).associate { index ->
            val profile = profiles.getString(index)
            require(paths.containsKey(profile))
            val before = File(backup, "$profile.before").readBytes()
            val after = File(backup, "$profile.after").readBytes()
            val current = readTarget(files, profile)
            require(hash(current).contentEquals(hash(before)) || hash(current).contentEquals(hash(after))) {
                "Identity data changed during recovery; backups were preserved."
            }
            if (profile == "mii") require(KartPadMiiStorage.isValidDatabase(after))
            else KartPadSaveStorage.validate(after)
            profile to after
        }
        writes.forEach { (profile, bytes) -> write(target(files, profile), bytes) }
        if (journal(files).exists()) check(journal(files).delete())
        check(pointer(files).delete()) // Keep both snapshots as private recovery backups.
        null
    }.getOrElse { "Pending identity changes could not be applied safely. Existing backups are retained." }

    private external fun nativeRecords(data: ByteArray, mii: Boolean): Array<String>
    private external fun nativeEdit(data: ByteArray, operation: Int, slot: Int, createId: String, name: ByteArray): ByteArray
}
