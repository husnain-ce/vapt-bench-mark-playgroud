# iOS targets

**11 targets** (`ios/aq-ios-ben01` … `aq-ios-ben11`).

These are **Xcode / SwiftUI source projects**, not containers. Building and
running them requires macOS with Xcode — `bench` lists them
(`./bench list --all`) but does not host them.

## Build & run

Each target lives under `ios/aq-ios-benN/src` as an `.xcodeproj` with a
`README.md` describing the vulnerability class (hardcoded secrets, insecure
data storage, weak crypto, etc.). Some targets include an `exploit/` folder.

```bash
open ios/aq-ios-ben01/src/FinanceTracker/FinanceTracker.xcodeproj
# In Xcode: select a simulator (or a provisioned device) and Run.
```

## Testing tips

- The simulator is enough for source-level and most runtime analysis; a
  jailbroken device is only needed for exercises that specify it.
- Inspect the app bundle and on-device storage for the planted secrets/flags
  described in each target's `README.md`.
