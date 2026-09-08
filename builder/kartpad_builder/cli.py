from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .bootstrap import prepare_dependencies
from .pipeline import BuildError, _validate_extraction, build, extract
from .profiles import ProfileError, load_profiles, select_profile, sha256_file


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        prog="kartpad-builder",
        description="Create a private unsigned KartPad IPA from a supported user-owned disc image.",
    )
    result.add_argument("--version", action="version", version=__version__)
    result.add_argument("--profiles-dir", type=Path, default=repo_root() / "builder/profiles")
    sub = result.add_subparsers(dest="command", required=True)
    sub.add_parser("profiles", help="List profiles and their verified capability status")
    doctor = sub.add_parser("doctor", help="Verify tools and pinned Builder dependencies")
    doctor.add_argument("--profile", default="mkwii-rmcp01-rev0")
    bootstrap = sub.add_parser("bootstrap", help="Fetch and verify pinned Builder dependencies")
    bootstrap.add_argument("--profile", default="mkwii-rmcp01-rev0")
    inspect = sub.add_parser("inspect", help="Identify a disc image without extracting it")
    inspect.add_argument("image", type=Path)
    inspect.add_argument("--profile", default="auto")
    inspect.add_argument("--extracted-data", type=Path, help="Also validate an existing DATA partition, read-only")
    prepare = sub.add_parser("prepare", help="Validate/reuse a DATA partition or extract a supported image")
    prepare.add_argument("image", type=Path)
    prepare.add_argument("--profile", default="auto")
    prepare.add_argument("--extracted-data", type=Path, help="Use this existing DATA partition without copying or modifying it")
    prepare.add_argument("--output", type=Path, help="New extraction directory (mutually exclusive with --extracted-data)")
    audit = sub.add_parser("audit-region", help="Report region-port coverage without claiming runtime compatibility")
    audit.add_argument("--profile", required=True)
    audit.add_argument("--extracted-data", type=Path, required=True)
    audit.add_argument("--output", type=Path, required=True, help="JSON audit report, not a translator manifest")
    build_parser = sub.add_parser("build", help="Build a private unsigned IPA")
    build_parser.add_argument("image", type=Path)
    build_parser.add_argument("--profile", default="auto")
    build_parser.add_argument("--extracted-data", type=Path, help="Reuse a validated DATA partition read-only")
    build_parser.add_argument("--output", type=Path, default=repo_root() / "artifacts/KartPad-personal-unsigned.ipa")
    build_parser.add_argument("--work-root", type=Path, default=repo_root() / "private/builder")
    build_parser.add_argument("--jobs", type=int, choices=range(1, 9), default=2)
    build_parser.add_argument("--translation-root", type=Path, help=argparse.SUPPRESS)
    build_parser.add_argument("--app", type=Path, help=argparse.SUPPRESS)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        profiles = load_profiles(args.profiles_dir)
        if args.command == "profiles":
            for profile in profiles:
                formats = ", ".join(profile.data["containers"]["extensions"])
                print(f"{profile.id}\t{profile.display_name}\t{formats}\t{profile.status}")
            return 0
        if args.command == "audit-region":
            from .region_audit import audit_region

            profile = next((item for item in profiles if item.id == args.profile), None)
            if profile is None:
                raise ProfileError(f"unknown profile: {args.profile}")
            report = audit_region(repo_root(), profile, args.extracted_data.resolve())
            output = args.output.resolve()
            if output.exists() or output == args.extracted_data.resolve() or args.extracted_data.resolve() in output.parents:
                raise ProfileError("audit output must be a new file outside the supplied DATA partition")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(report, indent=2) + "\n")
            print(json.dumps(report["summary"], indent=2))
            print(f"Region-port audit: {output}")
            return 0
        if args.command in ("doctor", "bootstrap"):
            profile = next((item for item in profiles if item.id == args.profile), None)
            if profile is None:
                raise ProfileError(f"unknown profile: {args.profile}")
            dependencies = prepare_dependencies(repo_root(), profile, install=args.command == "bootstrap")
            print(f"Builder dependencies verified for {profile.id}: {', '.join(dependencies)}")
            return 0
        if not args.image.is_file():
            raise ProfileError(f"disc image does not exist: {args.image}")
        suffix = args.image.suffix.lower().removeprefix(".")
        image_sha256 = sha256_file(args.image)
        profile = select_profile(profiles, image_sha256, args.profile)
        if suffix not in profile.data["containers"]["extensions"]:
            raise ProfileError(f"unsupported disc-image extension for {profile.id}: .{suffix}")
        extracted = args.extracted_data.resolve() if args.extracted_data else None
        if extracted is not None:
            _validate_extraction(profile, extracted)
        if args.command == "inspect":
            print(json.dumps({"imageSHA256": image_sha256, "profileId": profile.id, "displayName": profile.display_name,
                              "status": profile.status, "buildEnabled": profile.build_enabled,
                              "extractedDataValidated": extracted is not None}, indent=2))
            return 0
        if args.command == "prepare":
            if extracted is not None and args.output is not None:
                raise ProfileError("--output and --extracted-data are mutually exclusive")
            if extracted is None:
                extracted = (args.output or repo_root() / "private/builder" / profile.id / "inputs" / image_sha256 / "disc").resolve()
                extract(profile, args.image.resolve(), extracted)
            print(json.dumps({"profileId": profile.id, "status": profile.status,
                              "buildEnabled": profile.build_enabled, "extraction": str(extracted),
                              "imageSHA256": image_sha256, "executables": profile.data["extraction"]["executables"]}, indent=2))
            return 0
        profile.require_build_support()
        prepare_dependencies(repo_root(), profile, install=False)
        result = build(
            repo=repo_root(),
            profile=profile,
            image=args.image.resolve(),
            image_sha256=image_sha256,
            output=args.output.resolve(),
            work_root=args.work_root.resolve(),
            jobs=args.jobs,
            translation_override=args.translation_root.resolve() if args.translation_root else None,
            app_override=args.app.resolve() if args.app else None,
            extraction_override=extracted,
        )
        print(f"Built private unsigned IPA: {result.ipa}")
        print(f"SHA-256: {result.ipa_sha256}")
        print("Game-code redistribution rights are not cleared; GPL-covered software remains redistributable under GPLv3.")
        return 0
    except (ProfileError, BuildError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
