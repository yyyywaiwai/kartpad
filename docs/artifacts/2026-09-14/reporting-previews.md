# Reporting prerelease verification — 14 September 2026

Source change PR #279 merged as `b9c1e2f221e1353747436a27601073694448e456`.
Both candidates identify clean compilation source
`13c937820751367db0d486a5190d50816b21064c`.

| Candidate | Artifact SHA-256 | Scope |
| --- | --- | --- |
| iPhone/iPad 0.4.20/build42 | `caf3dc81e069ae6f0de35ef067d02171cc65ae2d28712a92e549a6beb1a19db3` | Fresh preparation and full iPhoneOS build; unsigned IPA |
| Android 0.4.20-reporting.1/code90 | `a681b81fff6ffbe9aee177561a93c9279a6fc0186888aa80a7008277b47b3bce` | Release application build; unchanged public85 native libraries |

Apple prepared-runtime hash:
`f772844adbffa953d1db90ab83d76b6668336629f79575d9f474f77215be0a71`.
Translation hash:
`f5b67171325d4b98ccee74752268d689952d054f78f001b9083e42507dff8e0b`.
Unsigned executable hash:
`c6123229df4ca65b8a05629df045622ad159b3ce7995d3afedc7a154f125de8e`.

Android public certificate SHA-256 remains
`c1dbe0a0d72d830a5779476b346a750d0a37515adef992cad2f3863058f7f2f2`.
All four libraries match public85 and are recorded in embedded build metadata.
There is no claim of a new Android native rebuild. Application source archive
hash: `20ff71a41c67ec3005281b633d1f884d298bd512a7a798ee5d2e78d5cd0cba5b`.
Its 1,240 entries were checked against the manifest. Unchanged native source is
linked from code85; the new snapshot alone is not complete native source delivery.

Android report/export behavior tests and 35 overlay contracts passed. Apple
report routing, report context and Mac report helper checks passed; iPhoneOS
adapter and fresh full native builds passed. Both package derivations were
repeated with identical bytes. AAB/APK, Apple app, archive integrity, signing
identity or unsigned state, and content/provenance checks passed. Hosted assets
were fetched anonymously and matched local bytes; hosted Android package audit
and Apple executable/provenance checks were repeated.

These are prereleases with stable downloads retained. **Physical report-flow
and gameplay acceptance of these exact builds remain pending.** No new Mac
package or complete four-platform UI acceptance is claimed. Mac source changes
are merged. Prior private hardware installations are separate from these
published packages; users must preserve signing identity and data when updating.

- [Android release](https://github.com/chrissotraidis/kartpad/releases/tag/v0.4.20-android-reporting.1)
- [iPhone/iPad release](https://github.com/chrissotraidis/kartpad/releases/tag/v0.4.20-ios-reporting.1)
