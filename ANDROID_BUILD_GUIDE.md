
# Building the Break Tracker Android App

This guide will help you build an Android APK from your Break Tracker app.

## Prerequisites

The build process will require:
- Python 3.7 or higher
- Internet connection
- Patience (the first build can take some time as it downloads Android SDK components)

## Steps to Build

1. Ensure you have all required files:
   - `mobile_app.py` - The Kivy application
   - `buildozer.spec` - The configuration for Buildozer
   - `sheets_service.py` - Your Google Sheets integration
   - `.env` file with your Google Sheets credentials

2. Run the build script:
   ```
   ./build_apk.sh
   ```

3. Wait for the build process to complete. This can take 10-20 minutes on the first run.

4. Once complete, the APK will be available in the `./bin` directory.

## Installing on Android

1. Transfer the APK to your Android device
2. On your Android device, navigate to the APK file and tap to install
3. You may need to enable "Install from unknown sources" in your device settings

## Troubleshooting

If you encounter issues during the build:

1. Ensure all dependencies are installed
2. Check the buildozer logs for specific errors
3. Make sure your Google Sheets service account JSON is properly configured in your .env file

## Note on Google Sheets Integration

The app requires internet connectivity to log breaks to Google Sheets. The same service account credentials used in the web app are used in the Android app.
