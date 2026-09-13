// SPDX-License-Identifier: GPL-3.0-only
package dev.kartpad.rendererprobe;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

public final class ProbeActivity extends Activity {
    static { System.loadLibrary("kartpad_renderer_probe"); }
    private native String runProbe();
    private String report;

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
        LinearLayout content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        int pad = Math.round(24 * getResources().getDisplayMetrics().density);
        content.setPadding(pad, pad, pad, pad);
        TextView explanation = new TextView(this);
        explanation.setText("KartPad Renderer Check\n\nTests synthetic packed data, indexed draws, matrix layouts, textures, and queued buffer updates. This separate app does not read KartPad, game files, saves, or identifiers. A pass does not prove gameplay works.\n");
        content.addView(explanation);
        Button run = new Button(this); run.setText("Run GPU Check"); content.addView(run);
        Button share = new Button(this); share.setText("Share Results"); share.setEnabled(false); content.addView(share);
        TextView result = new TextView(this); result.setTextIsSelectable(true); content.addView(result);
        ScrollView scroll = new ScrollView(this); scroll.addView(content); setContentView(scroll);
        getWindow().getDecorView().setOnApplyWindowInsetsListener((view, insets) -> {
            content.setPadding(pad, pad + insets.getSystemWindowInsetTop(), pad, pad + insets.getSystemWindowInsetBottom());
            return insets;
        });
        if (saved != null) report = saved.getString("report");
        if (report != null) { result.setText(report); share.setEnabled(true); }
        run.setOnClickListener(view -> {
            run.setEnabled(false); share.setEnabled(false);
            result.setText("Checking Vulkan… This can take up to a minute. Keep this app open.");
            new Thread(() -> {
                String text;
                try { text = runProbe(); }
                catch (Throwable error) { text = "GPU check could not complete: " + error.getClass().getSimpleName(); }
                final String completed = text;
                runOnUiThread(() -> {
                    if (isFinishing() || isDestroyed()) return;
                    report = completed; result.setText(report); share.setEnabled(true); run.setEnabled(true);
                });
            }, "KartPad GPU check").start();
        });
        share.setOnClickListener(view -> startActivity(Intent.createChooser(new Intent(Intent.ACTION_SEND)
            .setType("text/plain").putExtra(Intent.EXTRA_TEXT, report), "Share reviewed results")));
    }
    @Override public void onSaveInstanceState(Bundle state) {
        super.onSaveInstanceState(state); if (report != null) state.putString("report", report);
    }
}
