#!/usr/bin/env python3
"""Refresh KartPad support evidence and select one engineering action.

The coordinator owns selection and evidence; this driver does not edit source,
close issues, publish builds, or request private game data. One invocation is
one context refresh. The hourly coordinator continues useful actions within the
same wake, guided by docs/SUPPORT-AGENTS.md and the living priority source.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
OWNER = "chrissotraidis"
DEFAULT_STATE = REPO / "build" / "maintenance" / "coordinator" / "loop-state.json"
DEFAULT_PRIORITIES = REPO / "docs" / "maintenance-priorities.json"
PRODUCT_OBJECTIVE = (
    "Stable gameplay and supported online play on Android and Apple builds. "
    "Track Original and Retro separately; an unimplemented online mode is not a passed gate."
)
DUPLICATE_REPORTS = {209: 208, 210: 208}
_STATE_SPEC = importlib.util.spec_from_file_location("maintenance_state", REPO / "scripts/maintenance-state.py")
STATE_IO = importlib.util.module_from_spec(_STATE_SPEC)
_STATE_SPEC.loader.exec_module(STATE_IO)

EXTERNAL_NEXT_ACTIONS = {
    196: "matching build39 iPhone 17 Pro Max/iOS27 retest failed; await the already requested new crash analytics or in-app report, preserving data; do not repeat the same IPA or simulator gate",
    135: "obtain the remaining physical A10X performance acceptance result; startup correction is already separate",
    123: "use the fresh-source private 0.4.17-android.12-wfctrace123 candidate to trace the physical Retro VS disconnect after WFC entry; inspect corrected recv_success/recv_eof/recv_eagain/recv_error events plus wait/timeout, peer-session and deferred completion events, and do not publish until a race/reconnect result is clean",
    128: "obtain the matching device/build/import state and a redacted exit/console excerpt",
    131: "obtain a matching exit/console excerpt for the post-cup Next transition in Original and Retro",
    143: "obtain exact build/profile/import completion and a matching exit/final-console excerpt",
    198: "prepare a current-code83 non-debuggable shell-profileable diagnostic with compatible signing and matching symbols; existing code73 is stale; use the already accepted private handoff to obtain a 20-second approximately 99 Hz warmed native CPU profile and classify guest, GX CPU and waits before changing source",
    167: "use the supplied Infinix Hot 60 Pro / Android 16 / Mali-G57 MC2 / 0.4.11 Original rev0 evidence; obtain a matched slow-scene profile only when this lane is selected",
    195: "obtain the matched v0.4.16 Original/Retro performance comparison on the affected Galaxy S25",
    127: "run an equivalent-scene macOS main-versus-PR comparison before attributing the two-player offsets",
    169: "obtain an ordinary-exit save-loss reproduction and bounded console evidence",
    197: "identify chooser versus in-game menu and physical-controller versus touch input path",
    199: "unlock the paired iPhone, then obtain a v0.4.16 AirPlay retest with local-screen state, transition, target and connection path",
    194: "define a signer-safe updater design and test boundary before implementation",
    100: "run wired then wireless external-display recovery tests while preserving the SDL Metal view state",
    192: "retest the online-only Retro Rewind pack download on v0.4.16",
    105: "retain the reporter-confirmed manual save/rating transfer; keep automatic synchronization and remaining Mii scope separate",
    200: "confirm public .2 and import state, then capture process-exits.json reason/status/profile and final redacted startup lines for Original and Retro separately; private .9 is source-dirty exploratory evidence, not a controlled A/B candidate",
    207: "Samsung A05 already supplied code65, both profiles and entry/return symptoms with validation off; obtain only the remaining matching process-exit classification before selecting a separate crash correction",
    208: "treat duplicate reports #209 and #210 as one HONOR launch/exit family; obtain chooser-versus-Android-home boundary, selected profile, import completion and one redacted exit result without another uninstall or data clear",
    209: "follow the canonical #208 handoff; do not request duplicate diagnostics, and reopen only if this thread adds a distinct device, build or failure boundary",
    210: "follow the canonical #208 handoff; do not request duplicate diagnostics, and reopen only if this thread adds a distinct device, build or failure boundary",
    203: "record the requested RMCE01 revision and keep NAND/cheat requests in the feature-compatibility queue; do not begin a profile/build without a verified disc revision and scope",
    205: "obtain the exact import completion, selected profile and final redacted startup/exit boundary on the Adreno 610 target",
    206: "await the already requested Wi-Fi endurance result beyond four/five races; the cellular-versus-Wi-Fi distinction is supplied and acknowledged, not proof of a carrier/runtime cause",
}

# Public issues are reports, not independent engineering projects.  These
# families are the smallest useful aggregation layer: one source hypothesis,
# one local contract, and one device/reporter gate can serve several reports.
# A new issue in a family may reopen that family only when it adds evidence.
ISSUE_FAMILY_BY_NUMBER = {
    100: "external-display-recovery",
    102: "android-renderer-geometry",
    104: "android-renderer-geometry",
    105: "save-rating-transfer",
    119: "android-input-and-system-bars",
    120: "android-renderer-geometry",
    123: "android-online-session",
    127: "macos-multiplayer-rendering",
    128: "android-cup-exit",
    131: "android-cup-exit",
    135: "ios-a10x-performance",
    137: "android-renderer-geometry",
    143: "android-launch-exit",
    166: "android-renderer-geometry",
    167: "android-performance",
    169: "android-save-lifecycle",
    184: "android-controller-input",
    192: "retro-pack-installation",
    193: "android-renderer-geometry",
    194: "retro-version-and-updater",
    195: "android-performance",
    196: "ios-aggregate-shard-crash",
    197: "android-controller-input",
    198: "android-performance",
    199: "external-display-recovery",
    200: "android-launch-exit",
    202: "android-display-projection",
    203: "feature-compatibility",
    205: "android-launch-exit",
    206: "android-online-session",
    204: "android-performance",
    207: "android-performance",
    208: "android-launch-exit",
    209: "android-launch-exit",
    210: "android-launch-exit",
    211: "android-renderer-geometry",
    90: "feature-online-compatibility",
    91: "feature-controller-input",
    92: "project-governance",
    101: "apple-display-projection",
    103: "android-performance",
    5: "cross-platform-controller-input",
}

# A report can contain several independent problems. Keep the highest-risk
# family primary without losing the remaining subcases.
RELATED_FAMILIES = {
    169: ("android-performance", "android-input-and-system-bars"),
    207: ("android-launch-exit",),
    135: ("ios-cpu-baseline-accepted",),
    194: ("feature-updater",),
    105: ("feature-save-synchronization",),
}


def issue_family(issue_number: int) -> str:
    return ISSUE_FAMILY_BY_NUMBER.get(issue_number, "unclustered")

# These rows still wait on an external device/reporter result, but the local
# gate is actionable and must remain visible in the durable checkpoint. A
# generic blocked-external label would hide that work from the next wake.
DEPENDENCY_STATES = {
    196: "matching-build39-device-retest-failed; new-report-external",
    198: "current-profileable-preparation-local; same-device-capture-external",
}


def command(*args: str) -> str:
    result = subprocess.run(
        list(args), cwd=REPO, text=True, capture_output=True, check=False
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"{' '.join(args)} failed: {detail}")
    return result.stdout


def github_connection(query: str, connection: str, **variables: Any):
    """Read every GraphQL page; errors cannot masquerade as a complete inbox."""
    cursor = None
    while True:
        args = ["gh", "api", "graphql", "-f", f"query={query}"]
        for name, value in variables.items():
            args.extend(["-F" if isinstance(value, int) else "-f", f"{name}={value}"])
        if cursor is not None:
            args.extend(["-f", f"cursor={cursor}"])
        response = json.loads(command(*args))
        if response.get("errors"):
            raise RuntimeError("GitHub returned incomplete issue/comment evidence")
        page = response["data"]["repository"]
        for part in connection.split("."):
            page = page[part]
        yield from page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            return
        next_cursor = page["pageInfo"]["endCursor"]
        if not next_cursor or next_cursor == cursor:
            raise RuntimeError("GitHub pagination did not advance; inbox is incomplete")
        cursor = next_cursor


def load_open_issues() -> list[dict[str, Any]]:
    comment_fields = "id body createdAt url author { login }"
    issue_query = """
      query($cursor: String) {
        repository(owner: "chrissotraidis", name: "kartpad") {
          issues(states: OPEN, first: 100, after: $cursor) {
            nodes {
              number title body url createdAt updatedAt author { login }
              labels(first: 100) { nodes { name } }
              comments(first: 100) {
                nodes { COMMENT_FIELDS }
                pageInfo { hasNextPage endCursor }
              }
            }
            pageInfo { hasNextPage endCursor }
          }
        }
      }
    """.replace("COMMENT_FIELDS", comment_fields)
    comment_query = """
      query($number: Int!, $cursor: String) {
        repository(owner: "chrissotraidis", name: "kartpad") {
          issue(number: $number) {
            comments(first: 100, after: $cursor) {
              nodes { COMMENT_FIELDS }
              pageInfo { hasNextPage endCursor }
            }
          }
        }
      }
    """.replace("COMMENT_FIELDS", comment_fields)
    issues = list(github_connection(issue_query, "issues"))
    for issue in issues:
        issue["author"] = issue.get("author") or {}
        issue["labels"] = issue["labels"]["nodes"]
        comments = issue["comments"]
        # Re-read long threads through their own cursor so nested pagination
        # cannot advance the outer issue connection or omit older edits.
        issue["comments"] = (
            list(github_connection(comment_query, "issue.comments", number=issue["number"]))
            if comments["pageInfo"]["hasNextPage"] else comments["nodes"]
        )
        for comment in issue["comments"]:
            comment["author"] = comment.get("author") or {}
    return issues


def parse_time(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def is_non_actionable_acknowledgement(comment: dict[str, Any]) -> bool:
    """Ignore gratitude/coordination-only replies after the maintainer answered."""
    body = " ".join((comment.get("body") or "").lower().split())
    normalized = body.strip(" !.,:;!?👍🙏")
    if normalized in {"thanks", "thank you", "thx", "ok", "okay", "got it"}:
        return True
    # Long polite replies can look like fresh activity while carrying no new
    # build/device/symptom evidence. Keep the filter narrow so a sentence such
    # as "thanks, it still crashes" remains actionable.
    gratitude = ("thank", "thanks", "appreciate", "dedication", "love this game")
    coordination = ("happy to help", "ready whenever", "take all the time", "i'll be ready")
    evidence = (
        "crash", "fps", "frame", "build", "version", "android", "ios", "iphone",
        "ipad", "device", "original", "retro", "race", "menu", "log", "diagnostic",
        "error", "close", "freeze", "stutter", "slow", "install", "launch",
    )
    signal_body = body.replace("special build", "")
    # A reporter may acknowledge a private handoff without having tested a
    # candidate.  These replies often contain words such as APK, install, or
    # device because they restate the handoff boundary; treating those words
    # as fresh evidence causes the same externally blocked issue to be
    # selected on every heartbeat.  Only suppress the coordination pattern
    # when it has no concrete result language.
    coordination_only = (
        ("wait" in body or "standing by" in body or "let me know" in body)
        and any(
            phrase in body
            for phrase in (
                "private channel",
                "private handoff",
                "approved private",
                "before installing",
                "before i install",
            )
        )
        and not any(
            token in body
            for token in (
                "still",
                "crash",
                "crashed",
                "freeze",
                "stutter",
                "fps",
                "reproduced",
                "tested",
                "installed",
                "result",
                "error",
                "log",
            )
        )
    )
    if coordination_only:
        return True
    praise_only = (
        len(body) <= 180
        and any(
            phrase in body
            for phrase in (
                "you rock",
                "you rule",
                "great work",
                "awesome work",
                "having a blast",
                "love this game",
            )
        )
        and not any(
            token in body
            for token in (
                "crash",
                "crashed",
                "freeze",
                "stutter",
                "fps",
                "reproduced",
                "tested",
                "installed",
                "result",
                "error",
                "log",
                "still fails",
                "works",
            )
        )
    )
    if praise_only:
        return True
    return (
        len(body) <= 500
        and any(token in body for token in gratitude)
        and any(token in body for token in coordination)
        and not any(token in signal_body for token in evidence)
    )


def external_activity(issue: dict[str, Any]) -> tuple[bool, str | None]:
    comments = issue.get("comments", [])
    owner_times = [
        parse_time(comment["createdAt"])
        for comment in comments
        if comment.get("author", {}).get("login") == OWNER
    ]
    external = [
        comment
        for comment in comments
        if comment.get("author", {}).get("login") not in (None, OWNER)
        and not is_non_actionable_acknowledgement(comment)
    ]
    # The issue body is itself an unanswered reporter message.  Without this
    # synthetic initial event, a brand-new issue with no comments is classified
    # as an external dependency and never reaches the reply queue.
    issue_author = issue.get("author", {}).get("login")
    if issue_author not in (None, OWNER) and issue.get("body"):
        external.append(
            {
                "createdAt": issue.get("createdAt", issue.get("updatedAt")),
                "author": {"login": issue_author},
            }
        )
    if not external:
        return False, None
    latest = max(external, key=lambda comment: comment["createdAt"])
    latest_external = parse_time(latest["createdAt"])
    answered = owner_times and max(owner_times) >= latest_external
    return not answered, latest_external.isoformat()


def score(issue: dict[str, Any], now: dt.datetime) -> tuple[int, list[str]]:
    title = issue.get("title", "")
    body = issue.get("body", "")
    text = f"{title}\n{body}".lower()
    labels = {label.get("name") for label in issue.get("labels", [])}
    points = 0
    reasons: list[str] = []

    if "bug" in labels:
        points += 25
        reasons.append("bug")
    if "enhancement" in labels and "bug" not in labels:
        points -= 20
    # A confirmed or freshly reported crash blocks all gameplay and must stay
    # ahead of a rendering symptom.  Keep this ordering explicit: the
    # coordinator should not spend the only bounded engineering slot on a
    # graphics report while an actionable crash report is waiting for its next
    # discriminator.
    if any(word in text for word in ("crash", "crashes", "crashed", "doesn't load", "cannot load", "won't start")):
        points += 65
        reasons.append("startup-or-crash blocker")
    elif any(word in title.lower() for word in ("render", "graphic", "vertex", "geometry", "texture", "eyes")):
        points += 42
        reasons.append("rendering symptom")
    elif any(word in text for word in ("freeze", "stutter", "slow", "fps", "overheat")):
        points += 38
        reasons.append("gameplay-stall or performance symptom")
    elif any(word in text for word in ("render", "graphic", "vertex", "geometry", "texture", "eyes")):
        points += 42
        reasons.append("rendering symptom")

    evidence_markers = ("android", "build", "device", "steps", "original", "retro")
    evidence_count = sum(marker in text for marker in evidence_markers)
    if evidence_count >= 4:
        points += 20
        reasons.append("specific build/device reproduction")
    elif evidence_count >= 2:
        points += 10
        reasons.append("partial reproduction details")

    age_hours = max(0.0, (now - parse_time(issue["updatedAt"])).total_seconds() / 3600)
    recency_points = max(0, min(24, int(round(24 - age_hours))))
    points += recency_points
    if age_hours < 12:
        reasons.append("updated within 12 hours")
    elif age_hours < 48:
        reasons.append("updated within 48 hours")

    needs_response, latest_external = external_activity(issue)
    if latest_external and needs_response:
        external_age = max(0.0, (now - parse_time(latest_external)).total_seconds() / 3600)
        if external_age < 48:
            points += 18
            reasons.append("fresh reporter evidence")
    if needs_response:
        points += 18
        reasons.append("new external evidence needs a decision")

    # These rows have a shipped correction or a narrowly answered compatibility
    # question; they stay open for confirmation but should not displace an
    # unresolved crash, renderer failure or gameplay stall.
    deprioritized = {105: 12, 119: 20, 123: 8, 188: 26, 192: 26, 194: 30}
    if issue["number"] in deprioritized:
        points -= deprioritized[issue["number"]]
        reasons.append("awaiting candidate/reporter confirmation")

    return points, reasons


def test_plan(issue_number: int) -> tuple[list[str] | None, str]:
    if issue_number == 123:
        # The Android-only 500 ms receive-window candidate reached the WFC
        # dashboard but still disconnected before a Retro VS race.  Re-running
        # its host contract cannot change that evidence and made the hourly
        # selector spend cycles on an externally blocked issue.  Keep #123 in
        # the queue for the required fresh-source trace and physical session,
        # but do not present obsolete local work as an executable plan.
        return None, EXTERNAL_NEXT_ACTIONS[123]
    if issue_number == 200:
        return (
            [
                "python3",
                "-B",
                "-m",
                "unittest",
                "-v",
                "tests.test_android_network_stall",
                "tests.test_active_network_calls",
            ],
            "Android #200 host contracts only; private .9 is source-dirty exploratory evidence, and imported-game device exit evidence plus a clean provenance build are required before any controlled sampler comparison",
        )
    if issue_number in {166, 193, 211}:
        return (
            [
                "python3",
                "-B",
                "-m",
                "unittest",
                "-v",
                "tests.test_draw_input_diagnostics",
                "tests.test_aurora_const_pnmtx_contract",
            ],
            "renderer-input and PNMTX source contracts; affected-device gameplay still required",
        )
    if issue_number in {102, 104, 120, 137, 166, 193}:
        return (
            ["python3", "-B", "-m", "unittest", "-v", "tests.test_draw_input_diagnostics"],
            "renderer-input contract; affected-device gameplay still required",
        )
    if issue_number == 188:
        return (["scripts/test-android-identity-host.sh"], "host identity/import regression")
    if issue_number == 119:
        return (
            ["python3", "-B", "-m", "unittest", "-v", "tests.test_android_touch_overlay_contract"],
            "Android lifecycle/touch contract; device bars still require device confirmation",
        )
    if issue_number == 184:
        return (
            [
                "python3",
                "-B",
                "-m",
                "unittest",
                "-v",
                "tests.test_android_touch_overlay_contract.AndroidTouchOverlayContractTests.test_controller_mapping_is_persisted_swapped_and_applied_natively",
            ],
            "controller mapping contract; physical Thor press/release acceptance still required",
        )
    return None, EXTERNAL_NEXT_ACTIONS.get(
        issue_number,
        "obtain the specific reporter/device evidence documented for this issue before selecting a source change",
    )


def rank_issues(issues: list[dict[str, Any]], now: dt.datetime) -> list[dict[str, Any]]:
    """Rank ready work ahead of answered reports waiting on external evidence."""
    ranked = []
    for issue in issues:
        points, reasons = score(issue, now)
        needs_response, latest_external = external_activity(issue)
        plan, purpose = test_plan(issue["number"])
        externally_blocked = plan is None and not needs_response
        if externally_blocked:
            reasons.append("waiting on external evidence")
        ranked.append(
            {
                "issue": issue,
                "family": issue_family(issue["number"]),
                "related_families": list(RELATED_FAMILIES.get(issue["number"], ())),
                "score": points,
                "reasons": reasons,
                "needs_response": needs_response,
                "latest_external": latest_external,
                "plan": plan,
                "purpose": purpose,
                "externally_blocked": externally_blocked,
            }
        )
    ranked.sort(
        key=lambda row: (
            row["externally_blocked"],
            -row["score"],
            row["issue"]["number"],
        )
    )
    return ranked


FINGERPRINT_SCOPE_PATHS: dict[str, tuple[str, ...]] = {
    "android-network-receive-window": (
        "runtime/include/kartpad/network/blocking_stream_wait.h",
        "runtime/tests/blocking_stream_wait_tests.cpp",
        "patches/wiicompiled-blocking-stream-recv-wait.patch",
        "runtime/include/kartpad/android/network_session_trace.h",
        "patches/wiicompiled-android-network-session-trace.patch",
        "android/app/src/main/cpp/CMakeLists.txt",
        "tests/test_android_network_session_trace_contract.py",
        "scripts/test-android-network-receive-window.sh",
    ),
    "android-launch-runtime": (
        "scripts/build-android-game-app.sh",
        "scripts/android-runtime-provenance.py",
        "android/app/src/main/java/dev/kartpad/android/KartPadRuntimeHealth.kt",
        "patches/wiicompiled-android-network-stall.patch",
        "scripts/prepare-android-game-runtime.sh",
        "tests/test_android_network_stall.py",
        "tests/test_active_network_calls.py",
    ),
    "android-renderer-pnmtx": (
        "runtime/include/kartpad/diagnostics/draw_inputs.h",
        "patches/aurora-draw-input-diagnostics.patch",
        "patches/aurora-android-const-pnmtx-diagnostic.patch",
        "scripts/prepare-android-game-runtime.sh",
        "tests/test_draw_input_diagnostics.py",
        "tests/test_aurora_const_pnmtx_contract.py",
    ),
    "android-touch": (
        "android/app/src/main/java/dev/kartpad/android/KartPadActivity.kt",
        "tests/test_android_touch_overlay_contract.py",
    ),
    "android-controller": (
        "android/app/src/main/java/dev/kartpad/android/KartPadControllerMapping.kt",
        "runtime/include/kartpad/android/controller_mapping.hpp",
        "runtime/tests/android_gamepad_contract_tests.cpp",
        "tests/test_android_touch_overlay_contract.py",
    ),
}

ISSUE_FINGERPRINT_SCOPE: dict[int, str] = {
    123: "android-network-receive-window",
    200: "android-launch-runtime",
    119: "android-touch",
    184: "android-controller",
    102: "android-renderer-pnmtx",
    104: "android-renderer-pnmtx",
    120: "android-renderer-pnmtx",
    137: "android-renderer-pnmtx",
    166: "android-renderer-pnmtx",
    193: "android-renderer-pnmtx",
    211: "android-renderer-pnmtx",
}


def fingerprint_scope(issue_number: int) -> str:
    return ISSUE_FINGERPRINT_SCOPE.get(issue_number, "maintenance-wide")


def test_fingerprint(issue_number: int | None = None) -> str:
    """Identify the source/test state that makes a local result reusable.

    A broad worktree digest made an unrelated Android change reopen every
    renderer contract.  Registered issue plans now use the smallest relevant
    source/test scope; unknown plans retain the broad digest.
    """
    revision = command("git", "rev-parse", "HEAD").strip()
    scope = fingerprint_scope(issue_number) if issue_number is not None else "maintenance-wide"
    paths = FINGERPRINT_SCOPE_PATHS.get(scope, ())
    # Hash actual relevant bytes, not whether they are staged/committed. A
    # support reply, docs commit, or git add cannot invalidate a native test.
    if paths:
        digest = hashlib.sha256(scope.encode())
        for relative in paths:
            path = REPO / relative
            digest.update(relative.encode() + b"\0")
            digest.update(path.read_bytes() if path.is_file() else b"<missing>")
    else:
        diff = command("git", "diff", "--no-ext-diff", "--", "android", "apple", "patches", "runtime", "scripts", "tests")
        digest = hashlib.sha256(f"{scope}\0{revision}\0{diff}".encode())
    return digest.hexdigest()


def load_loop_state(path: Path) -> dict[str, Any]:
    try:
        state = json.loads(path.read_text())
    except FileNotFoundError:
        return {}
    if not isinstance(state, dict):
        raise RuntimeError("invalid loop state; preserve it and reconcile from evidence")
    return state


def save_loop_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    STATE_IO.write_json(path, state)


def record_queue_checkpoint(
    state: dict[str, Any],
    ranked: list[dict[str, Any]],
    fingerprint: str,
    now: dt.datetime,
    continuation: str = "dependency-checkpoint",
) -> None:
    """Persist a meaningful dependency checkpoint instead of silently stopping.

    A heartbeat may have no fresh local test to run.  That is an intentional
    wait for external evidence, not completion, but it still needs a durable
    continuation record so the next heartbeat can prove what it reviewed and
    can distinguish an unchanged wait from a newly actionable queue.
    """
    # Keep every external blocker durable even when ready/repeat-guarded rows
    # outrank it.  The console ranking is intentionally short, but a
    # continuation checkpoint must not forget a high-impact device/reporter
    # dependency merely because it falls below that display slice.
    checkpoint_rows = [row for row in ranked if row.get("externally_blocked")]
    checkpoint_rows.extend(
        row
        for row in ranked
        if (row.get("repeat_blocked") or row.get("repair_required"))
        and not row.get("externally_blocked")
    )
    dependencies = []
    seen: set[int] = set()
    for row in checkpoint_rows:
        issue = row["issue"]
        if issue["number"] in seen:
            continue
        seen.add(issue["number"])
        if (
            row.get("externally_blocked")
            or row.get("repeat_blocked")
            or row.get("repair_required")
        ):
            dependencies.append(
                {
                    "issue": issue["number"],
                    "updated_at": issue.get("updatedAt"),
                    "latest_external": row.get("latest_external"),
                    "state": (
                        DEPENDENCY_STATES.get(issue["number"], "blocked-external")
                        if row.get("externally_blocked")
                        else "repair-required"
                        if row.get("repair_required")
                        else "awaiting-change"
                    ),
                    "next": row.get("repair_action", row["purpose"]),
                }
            )
    state["_meta"] = {
        "last_continuation": continuation,
        "recorded_at": now.isoformat(),
        "fingerprint": fingerprint,
        "open_issue_count": len(ranked),
        "dependencies": dependencies,
    }


def record_wait_checkpoint(
    state: dict[str, Any], ranked: list[dict[str, Any]], fingerprint: str, now: dt.datetime
) -> None:
    record_queue_checkpoint(state, ranked, fingerprint, now)


def migrate_legacy_state(state: dict[str, Any], fingerprints: dict[int, str]) -> None:
    """Index retained exact-command results without inventing their provenance."""
    for key, row in list(state.items()):
        if not key.isdigit() or not isinstance(row, dict):
            continue
        if not row.get("fingerprint_scope"):
            row["provenance"] = "legacy-unverified"
            continue
        if row.get("family") and isinstance(row.get("command"), list):
            family = state.setdefault("_family_results", {}).setdefault(row["family"], {})
            family.setdefault("results", {}).setdefault(command_identity(row["command"]), dict(row))


def apply_repeat_guard(
    ranked: list[dict[str, Any]], state: dict[str, Any], fingerprint: str | dict[int, str]
) -> None:
    """Defer a passing/failing test until evidence or source state changes."""
    for row in ranked:
        issue = row["issue"]
        previous = state.get(str(issue["number"]))
        family_record = state.get("_family_results", {}).get(row["family"], {})
        family_previous = {}
        if row["plan"] and isinstance(family_record, dict):
            records = family_record.get("results", {})
            if isinstance(records, dict):
                family_previous = records.get(command_identity(row["plan"]), {})
            if not family_previous and family_record.get("command") == row["plan"]:
                family_previous = family_record
        current_fingerprint = (
            fingerprint.get(issue["number"], "")
            if isinstance(fingerprint, dict)
            else fingerprint
        )
        row["fingerprint"] = current_fingerprint
        issue_repeat_blocked = bool(
            row["plan"]
            and previous
            and previous.get("fingerprint") == current_fingerprint
            and previous.get("command") == row["plan"]
            and previous.get("provenance") != "legacy-unverified"
            and previous.get("result") == "pass"
        )
        family_repeat_blocked = bool(
            row["plan"]
            and not issue_repeat_blocked
            and family_previous.get("fingerprint") == current_fingerprint
            and family_previous.get("result") == "pass"
            and family_previous.get("command") == row["plan"]
        )
        row["repeat_blocked"] = issue_repeat_blocked or family_repeat_blocked
        row["repair_required"] = False
        if (
            row["plan"]
            and previous
            and previous.get("fingerprint") == current_fingerprint
            and previous.get("result") == "fail"
            and previous.get("command") == row["plan"]
            and previous.get("provenance") != "legacy-unverified"
        ):
            row["repair_required"] = True
            row["repair_action"] = (
                f"repair the failing {row['family']} contract before rerunning "
                f"the unchanged command: {' '.join(row['plan'])}"
            )
            row["reasons"].append("previous local test failed; repair action required")
        elif (
            row["plan"]
            and not issue_repeat_blocked
            and family_previous.get("fingerprint") == current_fingerprint
            and family_previous.get("result") == "fail"
            and family_previous.get("command") == row["plan"]
        ):
            row["repair_required"] = True
            row["repair_action"] = (
                f"repair the failing {row['family']} contract before rerunning "
                f"the unchanged command: {' '.join(row['plan'])}"
            )
            row["reasons"].append("family contract failed; repair action required")
        if issue_repeat_blocked:
            row["reasons"].append("same local result; waiting for evidence or source change")
        elif family_repeat_blocked:
            row["reasons"].append(
                f"family {row['family']} already has the same local result; waiting for new evidence or source change"
            )
    ranked.sort(
        key=lambda row: (
            row["externally_blocked"],
            row["repeat_blocked"],
            -row["score"],
            row["issue"]["number"],
        )
    )


def ready_rows(ranked: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return only rows that can make new local progress this cycle."""
    return [
        row
        for row in ranked
        if (
            not row["externally_blocked"]
            and not row["repeat_blocked"]
            and not row.get("repair_required")
        )
    ]


def run_test(plan: list[str]) -> tuple[bool, str]:
    result = subprocess.run(plan, cwd=REPO, text=True, capture_output=True, check=False)
    output = (result.stdout + result.stderr).strip()
    tail = "\n".join(output.splitlines()[-12:])
    return result.returncode == 0, tail


def command_identity(plan: list[str]) -> str:
    return json.dumps(plan, ensure_ascii=False, separators=(",", ":"))


def record_family_result(
    state: dict[str, Any],
    family: str,
    result: dict[str, Any],
) -> None:
    family_record = state.setdefault("_family_results", {}).setdefault(family, {})
    family_record.update(result)
    plan = result.get("command")
    if isinstance(plan, list):
        family_record.setdefault("results", {})[command_identity(plan)] = dict(result)


def load_priorities(path: Path) -> list[dict[str, Any]]:
    document = json.loads(path.read_text())
    if not isinstance(document, dict) or document.get("schema") != 1 or not isinstance(document.get("work"), list):
        raise RuntimeError("invalid priority queue schema")
    seen = set()
    for work in document["work"]:
        if not isinstance(work, dict) or not all(work.get(k) for k in ("id", "issues", "state", "next_action", "acceptance", "checkpoint")):
            raise RuntimeError("priority work must have an identity, issues, next action, checkpoint and acceptance gate")
        if work["id"] in seen or type(work.get("priority")) is not int or work["priority"] < 0:
            raise RuntimeError("duplicate work identity or invalid priority")
        seen.add(work["id"])
        if work["state"] not in {"ready-local", "awaiting-device", "awaiting-reporter", "awaiting-owner", "accepted", "deferred"}:
            raise RuntimeError("invalid priority state")
        if not all(type(n) is int and n > 0 for n in work["issues"]):
            raise RuntimeError("invalid priority issue numbers")
        if not (REPO / work["checkpoint"]).is_file():
            raise RuntimeError(f"missing checkpoint for {work['id']}")
        if work["state"].startswith("awaiting-"):
            dependency = work.get("dependency", {})
            if not dependency.get("owner") or not dependency.get("needs"):
                raise RuntimeError("external work requires a named owner and exact missing action")
    return sorted(document["work"], key=lambda w: (w["priority"], w["id"]))


def reporter_revision(issue: dict[str, Any]) -> str:
    """Content identity catches edited bodies and older edited comments too."""
    comments = [
        {k: c.get(k) for k in ("id", "createdAt", "body")}
        for c in issue.get("comments", [])
        if c.get("author", {}).get("login") not in (None, OWNER)
        and not is_non_actionable_acknowledgement(c)
    ]
    content = {"body": issue.get("body", ""), "comments": comments}
    return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()


def support_queue(issues: list[dict[str, Any]], state: dict[str, Any], now: dt.datetime) -> list[dict[str, Any]]:
    reviewed = state.get("_support_reviews", {})
    pending = [i for i in issues if reviewed.get(str(i["number"]), {}).get("revision") != reporter_revision(i)]
    # Data-loss classification comes first; report intake does not run tests.
    return sorted(pending, key=lambda i: (i["number"] != 169, -score(i, now)[0], i["number"]))


def select_work(work: list[dict[str, Any]], issues: list[dict[str, Any]], state: dict[str, Any]) -> dict[str, Any] | None:
    open_numbers = {i["number"] for i in issues}
    ready = sorted((w for w in work if w["state"] == "ready-local" and open_numbers.intersection(w["issues"])), key=lambda w: (w["priority"], w["id"]))
    if not ready:
        return None
    active = next((w for w in ready if w["id"] == (state.get("_active_work") or {}).get("id")), None)
    # Keep working to the next gate. Only a newly ready critical data-loss,
    # startup or online blocker can preempt an active lower-priority family.
    if active and not (ready[0]["priority"] <= 2 and ready[0]["priority"] < active["priority"]):
        return active
    return ready[0]


def record_work_selection(state: dict[str, Any], work: dict[str, Any] | None, now: dt.datetime) -> None:
    if work is None:
        state["_active_work"] = None
        return
    previous = state.get("_active_work") or {}
    same_gate = previous.get("id") == work["id"] and previous.get("next_action") == work["next_action"] and previous.get("checkpoint") == work["checkpoint"]
    # Reloading context after a worker returns is not another failed attempt.
    # Count at most one unchanged-gate observation per hourly wake window.
    window = now.strftime("%Y-%m-%dT%H")
    attempts = previous.get("cycles_at_gate", 0) + int(previous.get("wake_window") != window) if same_gate else 1
    state["_active_work"] = {"id": work["id"], "next_action": work["next_action"], "checkpoint": work["checkpoint"], "cycles_at_gate": attempts, "wake_window": window, "requires_decision": attempts > 2, "selected_at": now.isoformat()}


def priority_evidence(work: dict[str, Any], issues: list[dict[str, Any]], pending: list[dict[str, Any]]) -> dict[str, Any]:
    reports = [i for i in issues if i["number"] in work["issues"]]
    authors = {i.get("author", {}).get("login") for i in reports}
    authors = {a for a in authors if a and a != OWNER and not a.endswith("[bot]")}
    return {
        "open_threads": len(reports),
        "distinct_cases": len({DUPLICATE_REPORTS.get(i["number"], i["number"]) for i in reports}),
        "distinct_issue_authors": len(authors),
        "pending_review": [i["number"] for i in pending if i["number"] in work["issues"]],
    }


def priority_context(work: list[dict[str, Any]], issues: list[dict[str, Any]], pending: list[dict[str, Any]], selected: dict[str, Any] | None) -> str:
    """The complete small priority sheet is injected on every selection."""
    lines = ["# Current KartPad priorities", "", PRODUCT_OBJECTIVE, "",
             "Operating manual: docs/SUPPORT-AGENTS.md. Source of truth: docs/maintenance-priorities.json. Dated audits are background evidence.", "",
             "| Priority | Work | State | Cases | Issue authors | New evidence to review |",
             "| --- | --- | --- | --- | --- | --- |"]
    for item in work:
        facts = priority_evidence(item, issues, pending)
        reviews = ", ".join(f"#{n}" for n in facts["pending_review"]) or "none"
        lines.append(f"| {item['priority']} | {item['id']} | {item['state']} | {facts['distinct_cases']} | {facts['distinct_issue_authors']} | {reviews} |")
    lines.extend(["", "Counts are per work group, exclude maintainer/bot issue authors, and collapse known duplicate reports. Comment-only corroborators remain in reviewed issue/device evidence; these counts are not total affected users and must not be added across groups.", "",
                  "Changed evidence triggers a priority review, not automatic promotion by comment volume. Compare severity, independent affected targets, reproducibility, evidence confidence and the next feasible closure gate; record the reason for a changed order.", ""])
    for item in work:
        lines.extend([f"## {item['id']} ({item['state']})", f"Next: {item['next_action']}", f"Accept when: {item['acceptance']}", f"Evidence: {item['checkpoint']}"])
        if item.get("priority_reason"):
            lines.append(f"Priority reason: {item['priority_reason']}")
        if item["state"].startswith("awaiting-"):
            lines.append(f"External owner: {item['dependency']['owner']}; needs: {item['dependency']['needs']}")
        lines.append("")
    uncovered = [i["number"] for i in pending if not any(i["number"] in w["issues"] for w in work)]
    if uncovered:
        lines.append("Unmapped/deferred fresh reports requiring classification: " + ", ".join(f"#{n}" for n in uncovered))
    lines.extend(["", f"Active objective: {selected['id'] if selected else 'none; dependencies remain'}.",
                  "Continue useful steps within this wake. Reload this context after each result, intake batch, priority edit or context compaction. Stop only at a real dependency or a checkpointed execution/resource limit, not because one selector call finished."])
    return "\n".join(lines) + "\n"


def run_selected_contract(number: int, hypothesis: str, issues: list[dict[str, Any]], state: dict[str, Any], now: dt.datetime) -> int:
    target = next((i for i in issues if i["number"] == number), None)
    if target is None:
        raise RuntimeError("selected contract issue is not open")
    plan, purpose = test_plan(number)
    if not plan:
        raise RuntimeError("no registered contract for selected issue; execute the chosen engineering gate instead")
    rows = rank_issues([target], now)
    fingerprint = test_fingerprint(number)
    apply_repeat_guard(rows, state, {number: fingerprint})
    row = rows[0]
    if row.get("repeat_blocked") or row.get("repair_required"):
        print("test=not-run reason=unchanged-result; finish candidate/acceptance or repair the recorded failure")
        return 0
    print(f"hypothesis={hypothesis}\ncontract=#{number} {purpose}")
    passed, output = run_test(plan)
    result = {"fingerprint": fingerprint, "fingerprint_scope": fingerprint_scope(number), "family": row["family"], "latest_external": row["latest_external"], "result": "pass" if passed else "fail", "command": plan, "issue": number, "recorded_at": now.isoformat(), "hypothesis": hypothesis}
    state[str(number)] = result
    record_family_result(state, row["family"], result)
    print(f"test={result['result']}\n{output}")
    print("acceptance=unchanged; a contract result does not complete the work item")
    return 0 if passed else 1


def main() -> int:
    from contextlib import nullcontext
    parser = argparse.ArgumentParser(description="Select one persistent engineering objective and a separate support inbox.")
    parser.add_argument("--max-iterations", type=int, default=1)
    parser.add_argument("--state-file", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--priorities-file", type=Path, default=DEFAULT_PRIORITIES)
    parser.add_argument("--preview", action="store_true", help="read only; do not update checkpoints or run tests")
    parser.add_argument("--execute-tests", action="store_true")
    parser.add_argument("--issue", type=int, help="explicit contract issue; never selected from a support reply")
    parser.add_argument("--hypothesis", help="new source/evidence reason and the decision this contract changes")
    parser.add_argument("--review-issue", type=int)
    parser.add_argument("--review-revision")
    parser.add_argument("--review-evidence", help="actual response URL or local disposition/evidence path")
    args = parser.parse_args()
    if args.max_iterations != 1:
        parser.error("one engineering objective per invocation; continue useful steps within the wake")
    if args.execute_tests and (not args.issue or not args.hypothesis or not args.hypothesis.strip()):
        parser.error("--execute-tests requires --issue and --hypothesis; normal selection never runs tests")
    if args.preview and (args.execute_tests or args.review_issue):
        parser.error("--preview cannot execute tests or record reviews")
    if args.review_issue and not (args.review_revision and args.review_evidence):
        parser.error("review requires the displayed revision and evidence/disposition")
    now = dt.datetime.now(dt.timezone.utc)
    issues = load_open_issues()
    work = load_priorities(args.priorities_file)
    path = args.state_file.resolve()
    with nullcontext() if args.preview else STATE_IO.locked(path.parent, create=True):
        state = load_loop_state(path)
        if args.review_issue:
            target = next((i for i in issues if i["number"] == args.review_issue), None)
            if target is None or reporter_revision(target) != args.review_revision:
                raise RuntimeError("reporter content changed; inspect it before acknowledging this revision")
            state.setdefault("_support_reviews", {})[str(args.review_issue)] = {"revision": args.review_revision, "evidence": args.review_evidence, "reviewed_at": now.isoformat()}
        pending = support_queue(issues, state, now)
        print(f"support_pending={len(pending)} open_issues={len(issues)}; support review never runs a host test")
        for item in pending[:8]:
            print(f"  review=#{item['number']} family={issue_family(item['number'])} revision={reporter_revision(item)}")
        selected = select_work(work, issues, state)
        context = priority_context(work, issues, pending, selected)
        print(context)
        if selected:
            print(f"engineering={selected['id']} priority={selected['priority']} issues={selected['issues']}")
            print(f"next={selected['next_action']}\nacceptance={selected['acceptance']}\ncheckpoint={selected['checkpoint']}")
        else:
            print("engineering=none; explicit dependencies remain, not product completion")
        for item in work:
            if item["state"].startswith("awaiting-"):
                print(f"parked={item['id']} owner={item['dependency']['owner']} needs={item['dependency']['needs']}")
        if not args.preview:
            if not args.review_issue and not args.execute_tests:
                record_work_selection(state, selected, now)
            state["_support_pending"] = [{"issue": i["number"], "revision": reporter_revision(i)} for i in pending]
            state["_priority_evidence"] = {w["id"]: priority_evidence(w, issues, pending) for w in work}
            state["_meta"] = {
                "recorded_at": now.isoformat(), "open_issue_count": len(issues),
                "last_continuation": "engineering-selected" if selected else "dependency-checkpoint",
                "selected_work": selected["id"] if selected else None,
                "dependencies": [
                    {"work": w["id"], "state": w["state"], **w["dependency"]}
                    for w in work if w["state"].startswith("awaiting-")
                ],
            }
            if (state.get("_active_work") or {}).get("requires_decision"):
                print("stalled-gate=finish the named action or record the exact external owner/dependency; no further general audit or unchanged test")
            code = run_selected_contract(args.issue, args.hypothesis, issues, state, now) if args.execute_tests else 0
            save_loop_state(path, state)
            # Derived context only; JSON priorities remain the sole editable
            # work order. The loop lock serializes this local mirror.
            (path.parent / "PRIORITIES.md").write_text(context)
            return code
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, json.JSONDecodeError, KeyError, OSError) as error:
        print(f"maintenance-loop error: {error}", file=sys.stderr)
        raise SystemExit(2)
