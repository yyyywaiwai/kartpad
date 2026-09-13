package dev.kartpad.android

import java.nio.ByteBuffer
import java.nio.ByteOrder

fun testRatingCompanion() {
    var assertions = 0
    fun verify(value: Boolean) { check(value); assertions++ }
    fun rejected(block: () -> Unit) { verify(runCatching(block).exceptionOrNull() is IllegalArgumentException) }
    fun view(bytes: ByteArray) = ByteBuffer.wrap(bytes).order(ByteOrder.BIG_ENDIAN)
    fun fixture(vararg ids: Int): ByteArray = ByteArray(1640).also { bytes ->
        val b = view(bytes)
        b.putInt(0, 0x52525254).putShort(4, 1).putShort(6, 100)
        ids.forEachIndexed { slot, id ->
            val offset = 8 + slot * 16
            b.putInt(offset, id).putFloat(offset + 4, 83.25f + slot)
                .putFloat(offset + 8, 0f).putInt(offset + 12, 1)
        }
    }
    val source = fixture(10, 20, 30)
    val destination = fixture(40, 20).apply { this[lastIndex] = 77 }
    val beforeSource = source.copyOf()
    val beforeDestination = destination.copyOf()
    val merged = KartPadRatingCompanion.merge(source, destination, setOf(20, 10))
    verify(merged.copyOfRange(8, 24).contentEquals(destination.copyOfRange(8, 24)))
    verify(merged.copyOfRange(24, 40).contentEquals(source.copyOfRange(24, 40)))
    verify(merged.copyOfRange(40, 56).contentEquals(source.copyOfRange(8, 24)))
    verify(merged.copyOfRange(56, 1640).contentEquals(destination.copyOfRange(56, 1640)))
    verify(source.contentEquals(beforeSource) && destination.contentEquals(beforeDestination))
    verify(KartPadRatingCompanion.merge(source, merged, setOf(10, 20)).contentEquals(merged))
    val fresh = KartPadRatingCompanion.merge(source, null, setOf(30))
    verify(view(fresh).getInt(8) == 30 && view(fresh).getInt(36) == 0)
    KartPadRatingCompanion.validate(fresh)
    for (ids in listOf(emptySet(), setOf(99), setOf(0), setOf(-1), setOf(1_000_000_000),
        setOf(1, 2, 3, 4, 5))) rejected { KartPadRatingCompanion.merge(source, destination, ids) }
    for (size in listOf(0, 8, 1608, 1639, 1641)) rejected {
        KartPadRatingCompanion.validate(source.copyOf(size))
    }
    for ((offset, value) in listOf(0 to 0, 4 to 0x00020064, 4 to 0x00010063,
        8 to 0, 8 to -1, 8 to 1_000_000_000, 20 to 2, 24 to 10)) {
        val corrupt = source.copyOf().also { view(it).putInt(offset, value) }
        rejected { KartPadRatingCompanion.merge(corrupt, destination, setOf(10)) }
        rejected { KartPadRatingCompanion.merge(source, corrupt, setOf(10)) }
    }
    for (rating in listOf(Float.NaN, Float.POSITIVE_INFINITY, Float.NEGATIVE_INFINITY, -1f, 10001f)) {
        for (offset in listOf(12, 16)) rejected {
            KartPadRatingCompanion.validate(source.copyOf().also { view(it).putFloat(offset, rating) })
        }
    }
    for (rating in listOf(0f, 0.5f, 1f, 10000f)) {
        KartPadRatingCompanion.validate(source.copyOf().also { view(it).putFloat(12, rating) })
        assertions++
    }
    val full = fixture(*(1..100).toList().toIntArray())
    val fullBefore = full.copyOf()
    rejected { KartPadRatingCompanion.merge(fixture(101), full, setOf(101)) }
    verify(full.contentEquals(fullBefore))
    verify(KartPadRatingCompanion.merge(source, full, setOf(10)).size == 1640)
    // Inactive records are opaque and preserved unless selected as a free slot.
    val inactive = fixture().apply { view(this).putInt(8, -1).putFloat(12, Float.NaN) }
    KartPadRatingCompanion.validate(inactive)
    verify(KartPadRatingCompanion.merge(source, inactive, setOf(10))
        .copyOfRange(8, 24).contentEquals(source.copyOfRange(8, 24)))
    println("Android rating companion passed: $assertions checks (synthetic bytes only)")
}
