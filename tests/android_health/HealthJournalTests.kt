package dev.kartpad.android

import java.io.File
import java.nio.file.Files

fun main() {
    val root = Files.createTempDirectory("kartpad-health-test").toFile()
    val file = File(root, "Logs/android-health.log")
    val journal = KartPadHealthJournal(file, 64)
    journal.append("first")
    journal.append("second")
    check(file.readText() == "first\nsecond\n")
    KartPadHealthJournal(file, 64).append("persisted")
    check(file.readText().endsWith("persisted\n"))
    repeat(1000) { journal.append("sample=$it") }
    check(file.length() <= 64)
    check(file.readText().endsWith("sample=999\n"))
    val retained = file.readBytes()
    check(runCatching { journal.append("x".repeat(64)) }.isFailure)
    check(file.readBytes().contentEquals(retained))
    journal.append("é")
    check(file.readText().endsWith("é\n"))
    // Only the disposable test directory created above is removed.
    check(root.deleteRecursively())
    println("PASS: bounded health history, persistence, UTF-8 and oversized-record rejection")
}
