package dev.kartpad.android

/** Current upstream form fields; preflight answers must always be supplied by the reporter. */
internal object KartPadUpstreamReport {
    val kinds = listOf("In-game bug", "Crash or freeze", "Performance problem")
    fun fields(kind: Int, problem: String, area: String, frequency: String, metadata: String, evidence: String): Map<String, String> {
        require(kind in kinds.indices)
        val template = listOf("2-bug-report.yml", "1-crash-report.yml", "4-performance.yml")[kind]
        val result = linkedMapOf(
            "template" to template,
            "title" to "[KartPad modified build] ${problem.ifBlank { kinds[kind] }.take(100)}",
            "version" to "Modified KartPad build; upstream runtime version must be read from the selected console.log header.",
            "os" to "Android (KartPad port; not Windows)",
            "doing" to "$problem\n\n$area\nFrequency: $frequency",
            "logs" to "$evidence\n\n$metadata",
        )
        if (kind == 0) result["what"] = problem
        return result
    }
}
