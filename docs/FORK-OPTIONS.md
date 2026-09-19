# GitHub fork connection: options checked 14 September 2026

KartPad is currently a standalone GitHub repository (`fork: false`, no parent).
Its root commit `7875e82012385dbe93c739263426245f0a57cddc` is an independent
upload. Credits, a Git remote, and GitHub's fork-network relationship are
different things. Adding an upstream remote does not attach this repository.

## Available paths

1. **Keep the repository and implement direct runtime reporting.** This changes
   where future reports go without relocating code, downloads or discussions.
   This is the immediate recommendation, independently of the fork decision.
2. **Ask GitHub Support whether an in-place attachment is available.** There
   is no documented conversion parameter in the public repository API. Do not
   promise Support can do this: a June 2026 community report quotes Support
   rejecting attachment where no fork relationship previously existed. That is
   secondhand support evidence, not published GitHub policy. No request sent.
3. **Create a real WiiCompiled fork and migrate development.** GitHub supports
   creating a new fork under a chosen name. Prepare and validate KartPad there
   before any cutover; preserve the existing repository as history. A new fork
   does not automatically inherit KartPad's stars, releases, PRs, discussions,
   configuration or its existing fork network. Source migration and runtime
   validation remain real work, not a cosmetic metadata toggle.

At inspection KartPad had 506 stars and 28 forks. These counts can change.
Renaming it and creating a new fork at `chrissotraidis/kartpad` would stop the
old-name redirects. Existing `/issues/N` or release URLs would then address a
different repository, not automatically find the archived history. Do not
delete/recreate the repository or reuse its name as a shortcut.

If migration is chosen: inventory releases/assets, open issues/PRs, branches,
CI settings and all public URLs; prepare the fork under a temporary name;
verify reproducible builds and report destinations; then review a concrete
cutover plan. Old downloads and discussion history need explicit preservation.
Do not create a decorative fork that the real build does not use.

GitHub issue transfer is also not a cross-owner forwarding solution: documented
transfers require the same owning user/organization and write access to both.
KartPad and patchzyy's tracker have different owners.

## Sources

- [Create a fork](https://docs.github.com/en/pull-requests/how-tos/work-with-forks/fork-a-repo)
- [Repository API](https://docs.github.com/en/rest/repos/repos#update-a-repository)
- [Renaming and redirect warning](https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository)
- [Issue transfer restrictions](https://docs.github.com/en/issues/tracking-your-work-with-issues/administering-issues/transferring-an-issue-to-another-repository)
- [Community report quoting Support; not official policy](https://github.com/orgs/community/discussions/167393)
