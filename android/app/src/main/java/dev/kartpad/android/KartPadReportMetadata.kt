package dev.kartpad.android

/** For the app-generated technical context only, never raw logs or selected files. */
internal object KartPadReportMetadata {
    private const val MAX_CONTEXT_CHARS = 1500

    fun summary(technicalContext: String): String = buildString {
        appendLine("Report origin: KartPad Android (downstream of WiiCompiled).")
        appendLine("This report does not establish whether the problem is upstream.")
        if (technicalContext.isBlank()) {
            append("Technical context unavailable.")
        } else {
            append(technicalContext.take(MAX_CONTEXT_CHARS))
            if (technicalContext.length > MAX_CONTEXT_CHARS) append("\n[Technical context truncated]")
        }
    }
}
