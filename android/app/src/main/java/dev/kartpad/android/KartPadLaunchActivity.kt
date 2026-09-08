package dev.kartpad.android

import android.app.Activity
import android.app.AlertDialog
import android.content.Intent
import android.content.res.ColorStateList
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.graphics.drawable.StateListDrawable
import android.os.Bundle
import android.util.Log
import android.view.Gravity
import android.view.View
import android.widget.Button
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.ScrollView
import android.widget.TextView
import java.util.concurrent.Executors

/** Production owner for choosing the immutable runtime profile before SDL starts. */
open class KartPadLaunchActivity : Activity() {
    protected open fun pausedProfile(): String? = null
    private fun requestedProfileFile() = java.io.File(filesDir, "KartPad/RequestedRuntimeProfile")
    private lateinit var status: TextView
    private lateinit var original: ModeButton
    private lateinit var retro: ModeButton
    private lateinit var progress: ProgressBar
    private val validator = Executors.newSingleThreadExecutor()
    private var validationGeneration = 0
    private var retroInstalled = false
    private var gameDataReady = false
    private var pendingProfile: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(buildContent())
        original.setOnClickListener { selectMode("base") }
        retro.setOnClickListener { selectMode("retro_rewind") }
    }

    override fun onResume() {
        super.onResume()
        pausedProfile()?.let { current ->
            progress.visibility = View.GONE
            original.isEnabled = true
            retro.isEnabled = true
            setModeText(original, if (current == "base") "Resume Mario Kart Wii" else "Mario Kart Wii",
                if (current == "base") "Current game • Paused" else "Switch on next launch")
            setModeText(retro, if (current == "retro_rewind") "Resume Retro Rewind" else "Retro Rewind",
                if (current == "retro_rewind") "Current game • Paused" else "Switch on next launch")
            hideStatus("Current game paused")
            return
        }
        if (pendingProfile == null) {
            pendingProfile = runCatching { requestedProfileFile().readText() }.getOrNull()
                ?.takeIf { it == "base" || it == "retro_rewind" }
        }
        validateRetroRewind()
    }

    override fun onDestroy() {
        validationGeneration += 1
        validator.shutdownNow()
        super.onDestroy()
    }

    private fun validateRetroRewind() {
        val generation = ++validationGeneration
        val forceNotInstalled = BuildConfig.DEBUG &&
            intent.getBooleanExtra(EXTRA_DEBUG_RETRO_NOT_INSTALLED, false)
        val forceGameDataValid = BuildConfig.DEBUG && !BuildConfig.GAME_RUNTIME &&
            intent.getBooleanExtra(EXTRA_DEBUG_GAME_DATA_VALID, false)
        retroInstalled = false
        showStatus("Checking game data and Retro Rewind ${RetroRewindRelease.VERSION}…")
        progress.visibility = View.VISIBLE
        original.isEnabled = false
        retro.isEnabled = false
        validator.execute {
            val removalError = KartPadGameDataStorage.applyScheduledRemoval(filesDir)
            val gameDataError = when {
                forceGameDataValid -> null
                removalError != null -> removalError
                else -> KartPadGameDataStorage.validationError(filesDir) ?: runCatching {
                    KartPadGameDataStorage.ensureRuntimePath(filesDir)
                }.exceptionOrNull()?.let {
                    "Validated game data could not be configured for the runtime."
                }
            }
            val gameDataValid = gameDataError == null
            val valid = !forceNotInstalled && runCatching {
                RetroRewindInstallStorage.recover(filesDir)
                RetroRewindInstallValidator.validate(
                    RetroRewindInstallStorage.installedRoot(filesDir)
                        .resolve(RetroRewindRelease.ROOT),
                    RetroRewindInstallValidator.productionContract(),
                ).isValid.also { installed ->
                    if (installed) {
                        KartPadRuntimePathConfig.ensureRetroRewindRoot(filesDir)
                    }
                }
            }.getOrDefault(false)
            runOnUiThread {
                if (generation != validationGeneration || isFinishing || isDestroyed) {
                    return@runOnUiThread
                }
                retroInstalled = valid
                progress.visibility = View.GONE
                gameDataReady = gameDataValid
                original.isEnabled = true
                retro.isEnabled = true
                setModeText(
                    retro,
                    "Retro Rewind",
                    if (valid) {
                        "Installed ${RetroRewindRelease.VERSION} • Extra content + Retro WFC"
                    } else {
                        "Download ${RetroRewindRelease.VERSION} • Extra content + Retro WFC"
                    },
                )
                if (gameDataError != null) {
                    showStatus(gameDataError)
                } else if (!gameDataValid) {
                    hideStatus("Game data is required. Choose a mode to import it.")
                } else if (valid) {
                    hideStatus("Original and Retro Rewind ${RetroRewindRelease.VERSION} are ready")
                } else {
                    hideStatus("Original is ready; Retro Rewind is optional")
                }
                Log.i(LOG_TAG, "A3 mode chooser retro-installed=$valid")
                pendingProfile?.takeIf { gameDataReady }?.let { profile ->
                    pendingProfile = null
                    continueSelectedMode(profile)
                }
            }
        }
    }

    private fun selectMode(profile: String) {
        pausedProfile()?.let { current ->
            if (profile == current) {
                finish()
            } else {
                AlertDialog.Builder(this)
                    .setTitle("Switch on Next Launch")
                    .setMessage("Fully close KartPad from Recents and reopen it to switch games. Saved progress and controls are kept; unsaved race progress is not carried over. Resume does not apply pending changes.")
                    .setNegativeButton("Cancel", null)
                    .setPositiveButton("Use on Next Launch") { _, _ ->
                        val file = android.util.AtomicFile(requestedProfileFile())
                        requestedProfileFile().parentFile?.mkdirs()
                        runCatching {
                            val output = file.startWrite()
                            try { output.write(profile.toByteArray()); file.finishWrite(output) }
                            catch (error: Throwable) { file.failWrite(output); throw error }
                        }.onFailure { showStatus("The next-launch choice could not be saved.") }
                    }.show()
            }
            return
        }
        if (!gameDataReady) {
            pendingProfile = profile
            startActivityForResult(
                Intent(this, KartPadGameDataActivity::class.java),
                REQUEST_GAME_DATA,
            )
            return
        }
        continueSelectedMode(profile)
    }

    private fun continueSelectedMode(profile: String) {
        if (profile == "retro_rewind" && !retroInstalled) {
            startActivity(Intent(this, RetroRewindInstallActivity::class.java))
        } else {
            launch(profile)
        }
    }

    private fun launch(profile: String) {
        requestedProfileFile().delete()
        Log.i(LOG_TAG, "A3 mode chooser selected=$profile")
        startActivity(
            Intent(this, KartPadActivity::class.java)
                .putExtra(KartPadActivity.EXTRA_RUNTIME_PROFILE, profile),
        )
        // The translated runtime is process-global and is not restartable in
        // place. Do not leave the chooser behind the SDL activity where Back
        // could imply that another profile can be selected in this process.
        finish()
    }

    private fun buildContent(): View {
        val density = resources.displayMetrics.density
        fun dp(value: Int) = (value * density + 0.5f).toInt()
        fun label(text: String, size: Float, color: Int): TextView = TextView(this).apply {
            this.text = text
            textSize = size
            setTextColor(color)
            gravity = Gravity.CENTER
        }
        fun layout(bottom: Int) = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT,
        ).apply { bottomMargin = bottom }

        fun roundedButton(normal: Int, pressed: Int): StateListDrawable = StateListDrawable().apply {
            fun fill(color: Int) = GradientDrawable().apply {
                shape = GradientDrawable.RECTANGLE
                cornerRadius = dp(18).toFloat()
                setColor(color)
            }
            addState(intArrayOf(android.R.attr.state_pressed), fill(pressed))
            addState(intArrayOf(-android.R.attr.state_enabled), fill(Color.rgb(62, 62, 72)))
            addState(intArrayOf(), fill(normal))
        }
        fun styleModeButton(button: ModeButton, color: Int, pressed: Int, icon: Int) {
            button.apply {
                minimumHeight = dp(96)
                setPadding(dp(28), dp(24), dp(28), dp(24))
                background = roundedButton(color, pressed)
                backgroundTintList = null
                elevation = 0f
                stateListAnimator = null
                setIcon(icon, dp(20), dp(12))
            }
        }

        val background = GradientDrawable(
            GradientDrawable.Orientation.TL_BR,
            intArrayOf(
                Color.rgb(6, 19, 38),
                Color.rgb(26, 14, 46),
                Color.rgb(46, 11, 20),
            ),
        )
        val column = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            translationY = -dp(18).toFloat()
        }
        column.addView(ImageView(this).apply {
            setImageResource(R.drawable.ic_kartpad_steering_wheel)
            imageTintList = ColorStateList.valueOf(Color.rgb(255, 107, 46))
            contentDescription = "KartPad"
            scaleType = ImageView.ScaleType.CENTER_INSIDE
        }, LinearLayout.LayoutParams(dp(48), dp(48)).apply {
            gravity = Gravity.CENTER_HORIZONTAL
            bottomMargin = dp(12)
        })
        column.addView(label("KartPad", 34f, Color.WHITE).apply {
            setTypeface(typeface, Typeface.BOLD)
            includeFontPadding = false
        }, layout(dp(12)))
        column.addView(
            label("Choose your way to race", 20f, Color.argb(224, 255, 255, 255)).apply {
                setTypeface(typeface, Typeface.BOLD)
                includeFontPadding = false
            },
            layout(dp(12)),
        )
        column.addView(
            label(
                if (pausedProfile() != null) "Your current game is paused. Resume below. Switching games requires fully closing and reopening KartPad."
                else "Your own RMCP01 disc image or extracted game data is required before play.",
                17f,
                Color.argb(158, 255, 255, 255),
            ),
            layout(dp(24)),
        )
        original = ModeButton(this).apply {
            id = R.id.kartpad_mode_original
            styleModeButton(
                this,
                Color.rgb(8, 125, 255),
                Color.rgb(4, 99, 214),
                R.drawable.ic_kartpad_checkered_flag,
            )
            setModeText(this, "Mario Kart Wii", "Original game")
        }
        retro = ModeButton(this).apply {
            id = R.id.kartpad_mode_retro_rewind
            styleModeButton(
                this,
                Color.rgb(245, 56, 99),
                Color.rgb(207, 38, 78),
                R.drawable.ic_kartpad_gobackward,
            )
            setModeText(this, "Retro Rewind", "Checking installation…")
            isEnabled = false
        }
        val choices = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER
            addView(
                original,
                LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
                    .apply { marginEnd = dp(9) },
            )
            addView(
                retro,
                LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
                    .apply { marginStart = dp(9) },
            )
        }
        column.addView(choices, layout(dp(10)))
        progress = ProgressBar(this).apply {
            isIndeterminate = true
        }
        column.addView(progress, LinearLayout.LayoutParams(dp(28), dp(28)).apply {
            gravity = Gravity.CENTER_HORIZONTAL
            bottomMargin = dp(2)
        })
        status = label(
            "Checking game data and Retro Rewind ${RetroRewindRelease.VERSION}…",
            13f,
            Color.argb(184, 255, 255, 255),
        )
        status.id = R.id.kartpad_mode_status
        status.accessibilityLiveRegion = View.ACCESSIBILITY_LIVE_REGION_POLITE
        column.addView(status, layout(0))
        column.addView(Button(this).apply {
            text = "Export Private Diagnostics…"
            isAllCaps = false
            setTextColor(Color.argb(184, 255, 255, 255))
            setBackgroundColor(Color.TRANSPARENT)
            setOnClickListener {
                AlertDialog.Builder(this@KartPadLaunchActivity)
                    .setTitle("Export Private Diagnostics")
                    .setMessage("Save recent runtime logs to a location you choose. Logs may contain local paths or personal details. No game images, saves, profiles, or signing material are copied. Keep this file private and review it before sharing.")
                    .setNegativeButton("Cancel", null)
                    .setPositiveButton("Save Locally…") { _, _ ->
                        startActivityForResult(Intent(Intent.ACTION_CREATE_DOCUMENT).apply {
                            addCategory(Intent.CATEGORY_OPENABLE)
                            type = "application/zip"
                            putExtra(Intent.EXTRA_TITLE, "KartPad-private-diagnostics.zip")
                        }, REQUEST_DIAGNOSTICS)
                    }.show()
            }
        }, layout(0))

        val availableWidthDp = (resources.displayMetrics.widthPixels / density).toInt() - 64
        val contentWidth = dp(minOf(760, maxOf(320, availableWidthDp)))
        val scroll = ScrollView(this).apply {
            isFillViewport = true
            clipToPadding = false
            addView(column, FrameLayout.LayoutParams(
                contentWidth,
                FrameLayout.LayoutParams.WRAP_CONTENT,
                Gravity.CENTER,
            ))
        }
        return FrameLayout(this).apply {
            this.background = background
            setPadding(dp(32), 0, dp(32), 0)
            addView(scroll, FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT,
            ))
        }
    }

    private fun setModeText(button: ModeButton, title: String, subtitle: String) {
        button.setModeText(title, subtitle)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode != REQUEST_DIAGNOSTICS || resultCode != RESULT_OK) return
        val destination = data?.data ?: return
        showStatus("Exporting private diagnostics…")
        validator.execute {
            val succeeded = runCatching {
                KartPadDiagnosticExport.write(applicationContext, destination)
            }.isSuccess
            runOnUiThread {
                if (!isFinishing && !isDestroyed) showStatus(
                    if (succeeded) "Private diagnostics saved. Nothing was uploaded."
                    else "Diagnostics export failed. The destination may contain an incomplete archive.",
                )
            }
        }
    }

    private fun showStatus(message: String) {
        status.text = message
        status.visibility = View.VISIBLE
    }

    private fun hideStatus(accessibilityMessage: String) {
        status.text = accessibilityMessage
        status.visibility = View.GONE
        status.announceForAccessibility(accessibilityMessage)
    }

    companion object {
        private const val LOG_TAG = "KartPadLauncher"
        private const val EXTRA_DEBUG_RETRO_NOT_INSTALLED =
            "dev.kartpad.android.TEST_MODE_CHOOSER_RETRO_NOT_INSTALLED"
        private const val EXTRA_DEBUG_GAME_DATA_VALID =
            "dev.kartpad.android.TEST_MODE_CHOOSER_GAME_DATA_VALID"
        private const val REQUEST_GAME_DATA = 4_303
        private const val REQUEST_DIAGNOSTICS = 4_304
    }

    /** Centers the icon and two-line label as one unit, matching UIButton.Configuration. */
    private class ModeButton(context: android.content.Context) : LinearLayout(context) {
        private val icon = ImageView(context)
        private val title = TextView(context).apply {
            textSize = 18f
            setTextColor(Color.WHITE)
            setTypeface(typeface, Typeface.BOLD)
            includeFontPadding = false
            gravity = Gravity.CENTER
        }
        private val subtitle = TextView(context).apply {
            textSize = 14f
            setTextColor(Color.argb(205, 255, 255, 255))
            includeFontPadding = false
            gravity = Gravity.CENTER
        }
        private val labels = LinearLayout(context).apply {
            orientation = VERTICAL
            gravity = Gravity.CENTER
            addView(title, LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT))
            addView(subtitle, LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT))
        }

        init {
            orientation = HORIZONTAL
            gravity = Gravity.CENTER
            isClickable = true
            isFocusable = true
            importantForAccessibility = IMPORTANT_FOR_ACCESSIBILITY_YES
            addView(icon)
            addView(labels)
        }

        override fun getAccessibilityClassName(): CharSequence = Button::class.java.name

        fun setIcon(resource: Int, size: Int, spacing: Int) {
            icon.setImageResource(resource)
            icon.imageTintList = ColorStateList.valueOf(Color.WHITE)
            icon.layoutParams = LayoutParams(size, size).apply { marginEnd = spacing }
        }

        fun setModeText(title: String, subtitle: String) {
            this.title.text = title
            this.subtitle.text = subtitle
            contentDescription = "$title\n$subtitle"
        }
    }
}
