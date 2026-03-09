# Building the SmartShield AI Android APK

This guide explains how to build the SmartShield AI Android APK from the Capacitor-wrapped React frontend.

## Prerequisites

- **Node.js** >= 18
- **npm** >= 9
- **Java JDK** 17 (OpenJDK recommended)
- **Android SDK** with:
  - Platform SDK 34
  - Build Tools 34.0.0+
  - Command-line tools
- **Gradle** 8.2+

Set the required environment variables:

```bash
export ANDROID_HOME=/path/to/android/sdk
export ANDROID_SDK_ROOT=$ANDROID_HOME
```

## Build Steps

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Build the React Web App

```bash
npm run build
```

### 3. Sync Web Assets to Android

```bash
npx cap sync android
```

### 4. Build the Debug APK

```bash
cd android
./gradlew assembleDebug
```

The debug APK will be at:

```
android/app/build/outputs/apk/debug/app-debug.apk
```

### 5. Build the Release APK (Optional)

For a signed release build, first create a keystore:

```bash
keytool -genkey -v -keystore smartshield.keystore -alias smartshield -keyalg RSA -keysize 2048 -validity 10000
```

Then build the release APK:

```bash
cd android
./gradlew assembleRelease
```

The release APK will be at:

```
android/app/build/outputs/apk/release/app-release.apk
```

## Quick One-Liner

Build everything from the frontend directory:

```bash
cd frontend && npm run build && npx cap sync android && cd android && ./gradlew assembleDebug
```

## Opening in Android Studio

To open the project in Android Studio for development:

```bash
npx cap open android
```

## Configuring the Backend URL

By default the app connects to `http://localhost:8000`. To point it at a remote backend, set the environment variable before building:

```bash
REACT_APP_API_URL=https://your-backend.example.com npm run build
npx cap sync android
cd android && ./gradlew assembleDebug
```

## Project Structure

```
frontend/
  capacitor.config.ts     # Capacitor configuration
  android/                # Native Android project
    app/
      src/main/
        AndroidManifest.xml
        java/com/smartshield/ai/MainActivity.java
        res/values/
          colors.xml      # Dark glassmorphic theme colors
          styles.xml      # App theme (dark, no action bar)
          strings.xml     # App name and package
```

## Troubleshooting

**Gradle fails to download dependencies**
Ensure you have internet access and `ANDROID_HOME` is set correctly.

**App shows white screen**
Run `npx cap sync android` to copy the latest web build into the Android project.

**Backend unreachable from device**
Use a publicly accessible backend URL or configure your device to reach the development server on your local network.
