package dev.kartpad.android

/** Non-exported chooser above SDL: Activity pause/resume retains the one runtime. */
class KartPadPausedMenuActivity : KartPadLaunchActivity() {
    override fun pausedProfile(): String? = intent.getStringExtra(
        KartPadActivity.EXTRA_RUNTIME_PROFILE,
    )?.takeIf { it == "base" || it == "retro_rewind" }
}
