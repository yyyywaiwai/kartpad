# Applying this migration to another project

Use KartPad's method only after inspecting that project's actual dependency layout. Do not assume every port has the same patch-stack problem.

1. Preserve the existing repository, history, issues, release URLs, bundle IDs and signing identity. Back up the dirty checkout, Git history, shipped binaries and device data; rehearse restoration.
2. Identify each upstream, pinned revision and license. Verify actual GitHub fork relationships for maintained dependencies. Preserve existing attribution and link the relevant upstream tracker; platform issues stay with the port. Do not recreate the user's repository merely to obtain a fork badge.
3. Prepare the old source and record hashes. Import the exact prepared modifications as ordinary tracked source or a maintained upstream fork with pinned commits. Keep platform differences separate if merging them would change behavior. Do not upgrade upstream at the same time.
4. Compare all prepared source and generated outputs before retiring patches. Keep private game inputs and generated game code out of public source snapshots. Update build, cache, provenance and recursive source-delivery paths.
5. Rehearse the reverse migration in a disposable checkout and restore the source archive offline. Record the exact commands and commits for rollback.
6. Build and audit exact artifacts, then install in place on the accepted hardware without clearing data. Compare identity and save data. Let the owner define gameplay acceptance scope and report untested scenarios separately. Reproduce suspected regressions on the preserved old build when possible.
7. Publish versioned packages and matching source/notices/checksums from clean commits. Verify hosted downloads. Keep unrelated features separate, and roll back code or issue a higher-version correction rather than deleting user data.

A save-only export is not a complete installation recovery backup. Include the port's persisted console identity and related profile data for full recovery; do not silently overwrite another installation's identity. A server-side registration mismatch may persist through updates and require service support.
