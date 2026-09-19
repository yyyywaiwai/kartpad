# Racing launcher design QA

final result: passed

Scope: native iOS launcher, cold start and paused-game chooser. Approved target is the dark racing concept with the red K, stacked game rows, and dark-mode switch. This is not an Android layout acceptance report.

Evidence: `build/launcher-ui-preview/comparison.png` combines the approved concept and actual iPhone 14 simulator capture. `build/device-state/iphone-build44-launcher.png` shows the installed physical iPhone. The simulator capture matches the paused Retro state; the physical phone is at a cold-start chooser, so its actions correctly say Play Game.

- Typography: native SF text and scalable type, clear hierarchy. The initial preference button wrapped into narrow fragments; a minimum width and compression resistance fix removed that defect in the final capture. Native safe-area margins and platform switch dimensions intentionally differ from the mock.
- Layout: stacked rows, aligned actions, grouped theme controls and launch preference; safe areas preserved. Scroll container and vertical layout support constrained widths and accessibility text. Extremely large text and iPad hardware remain follow-up coverage.
- Colors: default charcoal theme, red actions, blue flag, gold rewind; warm light theme available. Text colors follow the selected theme, including Help. Reduced Motion skips the short button press animation.
- Assets: generated transparent 1024px K and matching opaque app icon, downsampled from a higher resolution original. Decorative checker raster is subtle. Standard SF Symbols replace the mock's illustrative flag/rewind shapes deliberately.
- Content: both game actions preserve the existing ready/import/setup/resume/next-launch branches. Help keeps setup/troubleshooting guides and installed version. Persistent On launch preference defaults to Ask every time; one-shot next-launch choice takes precedence. The suspended-game menu never auto-launches the preferred game.

Verification: UIKit control tests passed for default dark mode, persisted light/dark state after controller recreation, both mode callbacks, resume/next-launch labels, and preference display. Native simulator interaction verified theme toggle, persistent preference through app relaunch, Help opening/closing, and Resume callback. Full runtime compiled and relinked, signed, installed in place, launched, and was visually inspected on iPhone 14. Physical gameplay and the return/resume cycle in this new build remain user acceptance checks.

No remaining P0/P1/P2 findings in the reviewed phone layout. P3: native rewind symbol and typography are platform approximations; broader Dynamic Type/device coverage remains useful.

## Release 0.4.23 acceptance

Owner confirmed the iPhone missing-Mii repair worked and both phone interfaces/game operation were accepted without observed regressions. Android physical testing also verified identity actions, rename editor, Help, theme persistence and returning to the paused launcher. This does not establish general Android performance improvement.

iPad simulator harness using the actual launcher class: iPad mini A17 Pro and iPad Pro 13-inch M4, iPadOS 26.5 landscape, dark and light themes passed visual review and all 8 behavior checks each. Launch preference popover anchored correctly, selection persisted after reboot, and Help opened/dismissed. Choose Mii popover anchoring was source-reviewed. This is layout/interaction coverage, not full iPad IPA gameplay acceptance.
