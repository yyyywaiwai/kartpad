# iPad build57 owner handoff — September 20

The owner requested the latest candidate on the attached iPad, preservation of
its game image, license, saves and configuration, and release notes for
publication after their testing and confirmation.

The physical iPad Pro (12.9-inch, sixth generation) had KartPad 0.4.19/build42,
bundle identifier `dev.kartpad.app`. The audited build57 app was copied from the
coordinated candidate and signed with a valid development identity and a profile
covering this iPad. Deep/strict signature verification passed. Its compiled UUID
remains `A0424517-BFE3-30A2-92FF-3409084951D7`. No app rebuild was performed.

Before installation, a private backup captured Documents (including the
2,778,726,400-byte WBFS), preferences, NAND including the license/save file,
save backups, Mii backups, configuration, and console identity. The update used
the same bundle identifier in place, with no uninstall or container reset.

The installed app reports **0.5.0/build57**. Before first launch, all 33 backed-up
files were read back and compared by size and SHA-256: **zero mismatches**.
The data remained in the updated app's container; no restore or duplicate upload
was necessary. Required extracted game files and the existing Retro Rewind
directory were also found after installation.

Normal foreground launch succeeded and a subsequent process inventory confirmed
KartPad was running. The legacy screenshot service was unavailable, so no visual
startup or gameplay acceptance is claimed. The app was left running for the
owner. Backup, readback, signing and deployment evidence remain private under
`work/ipad-build57-20260920/` in the integration worktree.

Android code133 remains installed on the owner Pixel. Release notes are in
`docs/releases/v0.5.0.md`. No release was published; owner testing and confirmation
remain the publication gate. This handoff does not reopen broader performance
or affected-hardware research.
