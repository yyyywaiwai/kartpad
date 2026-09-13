package dev.kartpad.android

import android.util.AtomicFile
import java.io.File
import java.nio.file.Files

fun main() {
    val root = Files.createTempDirectory("kartpad-preferred-game-").toFile()
    try {
        check(KartPadPreferredGame.read(root) == "ask")
        KartPadPreferredGame.write(root, "base")
        check(KartPadPreferredGame.read(root) == "base")
        KartPadPreferredGame.write(root, "retro_rewind")
        check(KartPadPreferredGame.read(root) == "retro_rewind")
        // A fresh read observes another process's committed choice.
        File(root, "KartPad/PreferredGame").writeText("base")
        check(KartPadPreferredGame.read(root) == "base")
        File(root, "KartPad/PreferredGame").writeText("corrupted")
        check(KartPadPreferredGame.read(root) == "ask")
        File(root, "KartPad/PreferredGame").writeText("")
        check(KartPadPreferredGame.read(root) == "ask")
        File(root, "KartPad/PreferredGame").writeText("base" + "x".repeat(64))
        check(KartPadPreferredGame.read(root) == "ask")
        KartPadPreferredGame.write(root, "base")
        AtomicFile.failSuffix = "PreferredGame"
        check(runCatching { KartPadPreferredGame.write(root, "retro_rewind") }.isFailure)
        check(KartPadPreferredGame.read(root) == "base")
        AtomicFile.failSuffix = null
        AtomicFile.silentFailSuffix = "PreferredGame"
        check(runCatching { KartPadPreferredGame.write(root, "retro_rewind") }.isFailure)
        check(KartPadPreferredGame.read(root) == "base")
        AtomicFile.silentFailSuffix = null
        check(runCatching { KartPadPreferredGame.write(root, "other") }.isFailure)

        fun choose(value: String, game: Boolean = true, retro: Boolean = true,
                   explicit: String? = null) = KartPadPreferredLaunch().choose(value, game, retro, explicit)
        check(choose("ask") == null)
        check(choose("bad") == null)
        check(choose("base") == "base")
        check(choose("retro_rewind") == "retro_rewind")
        check(choose("base", game = false) == null)
        check(choose("retro_rewind", retro = false) == null)
        check(choose("retro_rewind", explicit = "base") == null)
        check(choose("base", explicit = "retro_rewind") == null)
        val lifecycle = KartPadPreferredLaunch()
        check(lifecycle.choose("base", true, true, null) == "base")
        check(lifecycle.choose("base", true, true, null) == null)
        val recreated = KartPadPreferredLaunch(lifecycle.consumed)
        check(recreated.choose("base", true, true, null) == null)
        val setup = KartPadPreferredLaunch()
        check(setup.choose("retro_rewind", true, false, null) == null)
        check(setup.choose("retro_rewind", true, true, null) == null)
        // The activity consumes the opportunity for paused/explicit-return menus
        // and when the user opens settings or chooses a card during validation.
        check(KartPadPreferredLaunch(true).choose("base", true, true, null) == null)
        println("Preferred game storage and lifecycle checks passed")
    } finally {
        AtomicFile.failSuffix = null
        AtomicFile.silentFailSuffix = null
        root.deleteRecursively()
    }
}
