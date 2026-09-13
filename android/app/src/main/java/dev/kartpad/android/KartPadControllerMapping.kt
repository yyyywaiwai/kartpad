package dev.kartpad.android

import android.content.Context

/** Persisted one-to-one controller mapping for game buttons and D-pad Up. */
internal object KartPadControllerMapping {
    val gameButtonNames = arrayOf("A", "B", "X", "Y", "Z", "R", "D-pad Up")
    val physicalButtonNames = arrayOf(
        "A", "B", "X", "Y", "Left Shoulder", "Right Shoulder", "D-pad Up",
    )
    private val defaults = intArrayOf(0, 1, 2, 3, 4, 5, 6)
    private const val PREFERENCES = "kartpad_controller_mapping_v2"
    private const val LEGACY_PREFERENCES = "kartpad_controller_mapping_v1"

    fun load(context: Context): IntArray {
        val preferences = context.getSharedPreferences(PREFERENCES, Context.MODE_PRIVATE)
        if (defaults.indices.none { preferences.contains("game_$it") }) {
            val legacy = context.getSharedPreferences(LEGACY_PREFERENCES, Context.MODE_PRIVATE)
            val mapping = defaults.copyOf()
            for (index in 0 until 5) mapping[index] = legacy.getInt("game_$index", defaults[index])
            if (!isValid(mapping)) {
                defaults.copyInto(mapping)
            }
            save(context, mapping)
            return mapping
        }
        val mapping = IntArray(defaults.size) { index ->
            preferences.getInt("game_$index", defaults[index])
        }
        return if (isValid(mapping)) mapping else defaults.copyOf()
    }

    fun assign(context: Context, game: Int, physical: Int): IntArray {
        val mapping = load(context)
        if (game !in mapping.indices || physical !in mapping.indices) return mapping
        val other = mapping.indexOf(physical)
        val previous = mapping[game]
        mapping[game] = physical
        if (other >= 0 && other != game) mapping[other] = previous
        save(context, mapping)
        return mapping
    }

    fun reset(context: Context): IntArray {
        // Persist the reset so a later load cannot re-import legacy assignments.
        save(context, defaults)
        return defaults.copyOf()
    }

    private fun save(context: Context, mapping: IntArray) {
        if (!isValid(mapping)) return
        context.getSharedPreferences(PREFERENCES, Context.MODE_PRIVATE).edit().apply {
            mapping.forEachIndexed { index, physical -> putInt("game_$index", physical) }
        }.apply()
    }

    private fun isValid(mapping: IntArray): Boolean =
        mapping.size == defaults.size && mapping.toSet() == defaults.toSet()
}
