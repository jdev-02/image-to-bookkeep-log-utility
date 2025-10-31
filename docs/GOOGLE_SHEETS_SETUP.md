# Detailed Google Sheets Setup Guide

This guide walks you through setting up Google Sheets integration step-by-step, including troubleshooting common OAuth errors.

## Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "image-to-bookkeeping-log")
5. Click "Create"
6. Wait for the project to be created, then select it

### Step 2: Enable APIs

1. Go to "APIs & Services" > "Library" (or "Enabled APIs and services")
2. Search for "Google Sheets API"
3. Click on it and click "Enable"
4. (Optional) Search for "Google Drive API" and enable it too (if you need to create new sheets)

### Step 3: Configure OAuth Consent Screen

**This is crucial - skipping or misconfiguring this step causes "Error 403: access_denied"**

1. Go to "APIs & Services" > "OAuth consent screen"

2. **Choose User Type:**
   - If you have a Google Workspace (business) account: Choose "Internal" (only users in your organization)
   - Otherwise: Choose "External" (any Google user)

3. **Fill in App Information:**
   - App name: "Image-to-Bookkeeping-Log" (or any name)
   - User support email: Select your email
   - App logo: (Optional - skip for now)
   - App domain: (Optional - skip for now)
   - Developer contact information: Your email
   - Click "Save and Continue"

4. **Configure Scopes:**
   - Click "Add or Remove Scopes"
   - In the filter, search for "spreadsheets"
   - Check the box for `https://www.googleapis.com/auth/spreadsheets`
   - Click "Update" then "Save and Continue"

5. **Add Test Users** (IMPORTANT for Testing mode):
   - You'll see "Test users" section
   - Click "ADD USERS"
   - Enter your Google account email address (the one you'll sign in with)
   - You can add multiple test users if needed
   - Click "Add"
   - Click "Save and Continue"

6. **Review and Summary:**
   - Review your settings
   - Click "Back to Dashboard"

**Important**: Your app is now in "Testing" mode. In this mode:
- Only test users you added can sign in
- You'll see a warning when signing in (this is normal)
- No Google verification required
- Perfect for personal use!

### Step 4: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"

2. Click "Create Credentials" > "OAuth 2.0 Client ID"

3. If prompted, configure the consent screen (you already did this, so click through)

4. **Application type**: Select "Desktop app"

5. **Name**: "Image-to-Bookkeeping-Log Client" (or any name)

6. Click "Create"

7. A popup will appear showing your Client ID and Client Secret
   - Click "Download JSON" button
   - This downloads a file (usually named something like `client_secret_xxxxx.json`)

8. Save this file as `credentials.json` in one of these locations:
   - **Windows**: `C:\Users\YourUsername\.config\itbl\credentials.json`
   - **macOS/Linux**: `~/.config/itbl/credentials.json`
   - Or your current working directory

### Step 5: First Authentication

1. Run your itbl command:
   ```bash
   itbl parse ./inbox --target google-sheets --sheet-id YOUR_SHEET_ID
   ```

2. A browser window will open asking you to sign in
   - **Important**: Sign in with the SAME Google account you added as a test user
   - You may see a warning: "Google hasn't verified this app" - click "Advanced" then "Go to Image-to-Bookkeeping-Log (unsafe)" - this is normal for testing apps

3. Click "Allow" to grant permissions

4. The browser will show "The authentication flow has completed"

5. Close the browser and return to your terminal - the tool should continue processing

6. A `token.json` file will be saved in the same directory as `credentials.json` - this stores your authentication so you don't have to sign in every time

## Troubleshooting

### Error 403: access_denied

**Problem**: "This app is being tested and can only be accessed by developer-approved test users"

**Solution**: 
1. Go to Google Cloud Console → "APIs & Services" → "OAuth consent screen"
2. Scroll to "Test users" section
3. Click "ADD USERS"
4. Add your Google account email (the one you're trying to sign in with)
5. Save and try again

### "Credentials file not found"

See the main README.md troubleshooting section for solutions including:
- Auto-detection of common filenames
- Using `--credentials` flag
- Setting `GOOGLE_APPLICATION_CREDENTIALS` environment variable

### Wrong account signed in

Make sure you're signing in with the same Google account you added as a test user. If you signed in with a different account:
1. Remove the `token.json` file from `~/.config/itbl/` (or wherever it's stored)
2. Add the correct account as a test user
3. Try again

### "This app isn't verified"

This warning appears for all apps in Testing mode. It's safe to proceed:
1. Click "Advanced"
2. Click "Go to [Your App Name] (unsafe)"
3. Continue with authentication

For production use, you'd need to verify your app with Google, but for personal use, Testing mode is fine.

## Publishing Your App (Optional)

If you want to make your app available to anyone (not just test users), you'd need to:
1. Go through Google's app verification process
2. Provide privacy policy and terms of service URLs
3. This is typically only needed for public-facing apps

For personal use or sharing with a few people, Testing mode with test users is perfectly fine and requires no verification.

