# Android targets

**19 targets** (`android/aq-android-ben01` … `aq-android-ben19`).

These are **Android Studio / Gradle source projects**, not containers. They are
built to an APK and run on an emulator or device — `bench` lists them
(`./bench list --all`) but does not host them.

## Build & run

Each target lives under `android/aq-android-benN/src` with a standard Gradle
project and a `README.md` describing the vulnerability class (WebView JS
injection, open redirect, insecure storage, exported components, etc.).

```bash
cd android/aq-android-ben01/src

# Option A: Android Studio -- Open the project, let Gradle sync, Run on an
#   emulator or device (compileSdk >= 35 recommended).

# Option B: command line
./gradlew assembleDebug
# APK -> app/build/outputs/apk/debug/app-debug.apk
adb install app/build/outputs/apk/debug/app-debug.apk
```

## Testing tips

- Use an emulator with a writable system for dynamic instrumentation (Frida,
  objection) where the exercise calls for it.
- Read the per-target `README.md` for the exact vulnerable component and the
  intended exploitation path.
- Build artifacts (`build/`, `.gradle/`) and `*.apk` are gitignored — do not
  commit them.
