# Fixing "Error 403: access_denied" - Step by Step

## The Problem
You're seeing this error when trying to sign in:
```
image-to-bookkeeping-sheet has not completed the Google verification process. 
The app is currently being tested, and can only be accessed by developer-approved testers.
Error 403: access_denied
```

This happens because **your Google account is not added as a test user**.

## The Solution (5 Minutes)

### Step 1: Open Google Cloud Console
1. Go to https://console.cloud.google.com/
2. Make sure you're signed in with the same Google account that created the project
3. Select your project from the dropdown at the top

### Step 2: Navigate to OAuth Consent Screen
1. In the left sidebar, click **"APIs & Services"**
2. Click **"OAuth consent screen"** (it's in the submenu)

### Step 3: Find Test Users Section
1. You'll see several sections: "App information", "Scopes", "Test users", etc.
2. **Scroll down** - the "Test users" section is near the bottom of the page
3. It should show "No test users added yet" if you haven't added any

### Step 4: Add Your Email
1. Click the blue **"ADD USERS"** button
2. A dialog box will appear
3. Enter your **exact Google email address** (the one you're trying to sign in with)
   - Example: `yourname@gmail.com`
   - Make sure it's spelled correctly - check for typos!
4. Click **"Add"**
5. Your email should now appear in the test users list

### Step 5: Save
1. Scroll all the way to the bottom of the page
2. Click the **"SAVE AND CONTINUE"** or **"SAVE"** button
3. Wait for the confirmation that settings are saved

### Step 6: Try Again
1. Go back to your terminal
2. Run your `itbl` command again
3. When the browser opens to sign in, use the **exact same email** you just added
4. It should work now!

## Still Not Working?

### Check 1: Is the email correct?
- Double-check the email you added matches exactly what you're signing in with
- Check for typos, capital letters, etc.
- Gmail addresses are case-insensitive, but be consistent

### Check 2: Did you save?
- Make sure you clicked "Save" at the bottom of the OAuth consent screen page
- Refresh the page and verify your email is still in the test users list

### Check 3: Is the app in Testing mode?
- At the top of the OAuth consent screen, look for "Publishing status"
- It should say **"Testing"** (not "In production" or "Published")
- **If you don't see "Test users" section, your app might be in Production mode**
- To switch to Testing mode:
  1. On the OAuth consent screen page, look at the top
  2. If you see a banner that says "App is published" or "In production"
  3. Look for a button or link that says "Back to testing" or "Unpublish" or "Reset publishing status"
  4. OR: In some cases, you may need to go to the "Publishing status" section and click a button to revert to testing
  5. Once back in Testing mode, the "Test users" section should appear

### Check 4: Wait a few seconds
- Sometimes Google takes 10-30 seconds to update the test users list
- Wait a moment after saving, then try again

### Check 5: Clear your browser cache
- Sometimes browsers cache the "access denied" page
- Try:
  - Using an incognito/private window
  - Clearing browser cache
  - Using a different browser

## Visual Guide

The OAuth consent screen page should look like this:

```
┌─────────────────────────────────────────┐
│ OAuth consent screen                   │
├─────────────────────────────────────────┤
│ Publishing status: Testing              │
│                                         │
│ App information                         │
│ [Your app details]                      │
│                                         │
│ Scopes                                  │
│ [Google Sheets API scope]               │
│                                         │
│ Test users ← LOOK FOR THIS SECTION!    │
│ ┌───────────────────────────────────┐ │
│ │ No test users added yet            │ │
│ │ [+ ADD USERS] ← CLICK THIS!       │ │
│ └───────────────────────────────────┘ │
│                                         │
│ [SAVE AND CONTINUE] ← CLICK THIS TOO!  │
└─────────────────────────────────────────┘
```

## Multiple Users?

If you need to add multiple Google accounts:
1. Click "ADD USERS"
2. Enter one email, click "Add"
3. Click "ADD USERS" again
4. Enter the next email, click "Add"
5. Repeat as needed
6. Click "Save" when done

## Need More Help?

If you're still stuck:
1. Make sure you're in the correct Google Cloud project
2. Verify the OAuth consent screen is configured (see Step 3 in main README)
3. Check that the credentials.json file is in the right location
4. Try using the `--credentials` flag to specify the exact path to your credentials file

