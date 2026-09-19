package dev.kartpad.android

fun main() {
    fun blocked(e: KartPadReportEvidence) {
        check(e.validationError() != null)
        check(runCatching { e.summary(false) }.isFailure)
        check(runCatching { e.summary(true) }.isFailure)
    }
    blocked(KartPadReportEvidence())
    blocked(KartPadReportEvidence("", true, true))
    blocked(KartPadReportEvidence("logs", false, true))
    blocked(KartPadReportEvidence("logs", true, false))
    blocked(KartPadReportEvidence("unavailable", true, true, " \n\t"))
    blocked(KartPadReportEvidence("unexpected", true, true, "reason"))
    for (evidence in listOf(KartPadReportEvidence(), KartPadReportEvidence("logs", false, false), KartPadReportEvidence("unavailable"))) {
        check(evidence.browserSummary().contains("Nothing was uploaded"))
        check(evidence.browserSummary().contains("Logs not included yet"))
        check(evidence.validationError() != null) // Still blocked when sharing an unreviewed/missing file.
    }
    val reviewed = KartPadReportEvidence("logs", true, true)
    check(reviewed.validationError() == null)
    check(reviewed.summary(true).contains("attach it manually"))
    check(reviewed.summary(false).contains("selected"))
    check(!reviewed.summary(false).contains("received"))
    val unavailable = KartPadReportEvidence("unavailable", true, true, "  App stops before logging.  ")
    check(unavailable.validationError() == null)
    check(unavailable.summary(false) == "Logs unavailable: App stops before logging.")
    check(unavailable.summary(false) == unavailable.summary(true))
    check(!unavailable.summary(false).contains("selected"))
    check(KartPadReportEvidence("unavailable", reason="x".repeat(500)).summary(false).count { it == 'x' } == 300)
    val technical = "Version: 0.4.19\nRuntime profile: retro_rewind\nRetro version state: version_mismatch\nKartPad source revision: ${"a".repeat(40)}"
    val metadata = KartPadReportMetadata.summary(technical)
    check(metadata.endsWith(technical))
    check(metadata.contains("Report origin: KartPad Android"))
    check(metadata.contains("does not establish whether the problem is upstream"))
    check(KartPadReportMetadata.summary("").contains("Technical context unavailable."))
    val oversized = KartPadReportMetadata.summary("x".repeat(9000))
    check(oversized.contains("x".repeat(1500)))
    check(!oversized.contains("x".repeat(1501)))
    check(oversized.endsWith("[Technical context truncated]"))
    for (kind in KartPadUpstreamReport.kinds.indices) {
        val fields = KartPadUpstreamReport.fields(kind, "Glitch", "Track", "Sometimes", metadata, reviewed.summary(true))
        check("preflight" !in fields)
        check(fields.getValue("version").startsWith("Modified KartPad build"))
        check(fields.getValue("logs").contains(metadata))
        check(fields.getValue("doing").contains("Track"))
        check(fields.getValue("template").endsWith(".yml"))
    }
    println("PASS: explicit evidence choice, reviewed file, unavailable reason, honest handoff status")
}
