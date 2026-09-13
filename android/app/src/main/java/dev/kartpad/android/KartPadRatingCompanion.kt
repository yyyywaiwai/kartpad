package dev.kartpad.android

import java.nio.ByteBuffer
import java.nio.ByteOrder

/** Pure RRRating.pul validation/merge prerequisite. Does not read or write app data. */
internal object KartPadRatingCompanion {
    private const val CAPACITY = 100
    private const val HEADER = 8
    private const val ENTRY = 16
    // RatingSave.cpp's writer includes a 32-byte tail after its 100 entries.
    const val FILE_BYTES = HEADER + CAPACITY * ENTRY + 32

    private fun buffer(bytes: ByteArray) = ByteBuffer.wrap(bytes).order(ByteOrder.BIG_ENDIAN)
    private fun usable(id: Int) = id in 1 until 1_000_000_000

    private fun entries(bytes: ByteArray): Map<Int, Int> {
        require(bytes.size == FILE_BYTES) { "Unsupported rating file length." }
        val data = buffer(bytes)
        require(data.getInt(0) == 0x52525254 && data.getShort(4).toInt() == 1 &&
            data.getShort(6).toInt() == CAPACITY) { "Unsupported rating file format." }
        val result = linkedMapOf<Int, Int>()
        repeat(CAPACITY) { index ->
            val offset = HEADER + index * ENTRY
            val flags = data.getInt(offset + 12)
            require(flags == 0 || flags == 1) { "Unsupported rating entry flags." }
            if (flags == 1) {
                val id = data.getInt(offset)
                require(usable(id)) { "Invalid rating profile." }
                for (field in listOf(offset + 4, offset + 8)) {
                    val rating = data.getFloat(field)
                    // A newly allocated record can have one not-yet-set rating equal to zero.
                    require(rating.isFinite() && rating >= 0f && rating <= 10000f) {
                        "Invalid rating value."
                    }
                }
                require(result.put(id, offset) == null) { "Duplicate rating profile." }
            }
        }
        return result
    }

    fun validate(bytes: ByteArray) { entries(bytes) }

    /**
     * Caller must obtain selected IDs from validated matching save licenses, never slot numbers
     * or friend-code text. This does not establish save identity or perform server synchronization.
     * A later stopped-game transaction must back up and publish the returned bytes recoverably.
     */
    fun merge(source: ByteArray, destination: ByteArray?, selectedProfileIds: Set<Int>): ByteArray {
        require(selectedProfileIds.isNotEmpty() && selectedProfileIds.size <= 4 &&
            selectedProfileIds.all(::usable)) { "Select one to four valid save profiles." }
        val sourceEntries = entries(source)
        require(sourceEntries.keys.containsAll(selectedProfileIds)) { "A selected profile has no source rating." }
        val output = destination?.copyOf() ?: ByteArray(FILE_BYTES).also {
            buffer(it).putInt(0, 0x52525254).putShort(4, 1).putShort(6, CAPACITY.toShort())
        }
        val destinationEntries = entries(output)
        val data = buffer(output)
        val free = (0 until CAPACITY).map { HEADER + it * ENTRY }
            .filter { data.getInt(it + 12) == 0 }.iterator()
        require(selectedProfileIds.count { it !in destinationEntries } <=
            CAPACITY - destinationEntries.size) { "The destination rating file is full." }
        for (id in selectedProfileIds.sorted()) {
            val target = destinationEntries[id] ?: free.next()
            val origin = sourceEntries.getValue(id)
            source.copyInto(output, target, origin, origin + ENTRY)
        }
        return output
    }
}
