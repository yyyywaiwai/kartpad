#!/usr/bin/env bash
set -euo pipefail
repo="$(git rev-parse --show-toplevel)"
jdk="${KARTPAD_TEST_JDK:-$repo/.android-bootstrap/jdk-17.0.20.1+1/Contents/Home}"
cache="$HOME/.gradle/caches/modules-2/files-2.1"
jar() { rg --files --hidden --no-ignore "$cache/$1" | awk '/\.jar$/ {print; exit}'; }
compiler="$(jar org.jetbrains.kotlin/kotlin-compiler-embeddable/2.2.21)"
stdlib="$(jar org.jetbrains.kotlin/kotlin-stdlib/2.2.21)"
annotations="$(jar org.jetbrains/annotations/13.0)"
reflect="$(jar org.jetbrains.kotlin/kotlin-reflect/2.2.0)"
coroutines="$(jar org.jetbrains.kotlinx/kotlinx-coroutines-core-jvm/1.8.0)"
out="$(mktemp -d "${TMPDIR:-/tmp}/kartpad-controller-mapping.XXXXXX")"
trap 'rm -rf "$out"' EXIT
"$jdk/bin/java" -cp "$compiler:$stdlib:$annotations:$coroutines:$reflect" org.jetbrains.kotlin.cli.jvm.K2JVMCompiler \
  -no-stdlib -no-reflect -jvm-target 17 -classpath "$stdlib" -d "$out/tests.jar" \
  "$repo/tests/android_controller_mapping/Context.kt" \
  "$repo/tests/android_controller_mapping/ControllerMappingTests.kt" \
  "$repo/android/app/src/main/java/dev/kartpad/android/KartPadControllerMapping.kt"
"$jdk/bin/java" -cp "$out/tests.jar:$stdlib" dev.kartpad.android.ControllerMappingTestsKt
