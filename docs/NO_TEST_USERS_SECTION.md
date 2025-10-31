# I Don't See "Test Users" Section - What Do I Do?

If you can't find the "Test users" section on the OAuth consent screen page, here's how to fix it.

## Problem: App is in "Production" Mode

The "Test users" section only appears when your app is in **"Testing"** mode. If it's in "Production" or "Published" mode, that section won't show.

## Solution: Switch Back to Testing Mode

### Step 1: Check Your Publishing Status

1. Go to the OAuth consent screen: https://console.cloud.google.com/apis/credentials/consent
2. Look at the **top of the page** - you should see something like:
   - "Publishing status: Testing" ✅ (Good - you should see Test users)
   - "Publishing status: In production" ❌ (Bad - this is why you don't see Test users)
   - "App is published" ❌ (Bad - switch to testing)

### Step 2: Switch to Testing Mode

**Option A: Using the Publishing Status Section**
1. On the OAuth consent screen page, scroll to the very top
2. Look for a section called "Publishing status" or "App verification"
3. If it says "In production" or "Published":
   - Look for a button like "BACK TO TESTING", "UNPUBLISH", or "Reset publishing status"
   - Click that button
   - Confirm if prompted

**Option B: Using the Left Sidebar**
1. In Google Cloud Console, go to "APIs & Services" → "OAuth consent screen"
2. Look in the left sidebar for sections like:
   - "Publishing status"
   - "App verification"
3. Click on that section
4. Look for options to revert to testing or unpublish

**Option C: Create a New Project (Last Resort)**
If you can't find the option to switch back to testing:
1. Create a NEW Google Cloud project
2. When configuring the OAuth consent screen, make sure to:
   - Choose "External" user type
   - Fill in required fields
   - Click "Save and Continue" through all steps
   - **STOP before publishing** - keep it in Testing mode
   - Add yourself as a test user BEFORE doing anything else
3. Create new OAuth credentials for this new project
4. Download the new credentials.json file

## Alternative: Use Internal User Type (If You Have Google Workspace)

If you have a Google Workspace account:
1. On the OAuth consent screen, you might see "User type: Internal"
2. Internal apps don't need test users - anyone in your organization can access them
3. But this only works if you have Google Workspace (business account)

## Visual Guide: What You Should See

**CORRECT - Testing Mode (You should see this):**
```
┌─────────────────────────────────────┐
│ OAuth consent screen                │
│ Publishing status: Testing ✅       │
├─────────────────────────────────────┤
│ ... app details ...                 │
│                                     │
│ Test users ← YOU SHOULD SEE THIS!  │
│ ┌───────────────────────────────┐ │
│ │ No test users added yet        │ │
│ │ [+ ADD USERS]                  │ │
│ └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

**WRONG - Production Mode (You WON'T see Test users):**
```
┌─────────────────────────────────────┐
│ OAuth consent screen                │
│ Publishing status: In production ❌ │
│ [BACK TO TESTING] ← CLICK THIS!    │
├─────────────────────────────────────┤
│ ... app details ...                 │
│                                     │
│ (No Test users section here)        │
└─────────────────────────────────────┘
```

## Still Can't Find It?

If you've tried everything and still can't see the Test users section:

1. **Take a screenshot** of your OAuth consent screen page (especially the top part)
2. **Check the exact URL** - make sure you're at:
   - `https://console.cloud.google.com/apis/credentials/consent`
   - Not a different page
3. **Try a different browser** or incognito mode
4. **Check if you're in the right project** - the project dropdown at the top

## Quick Workaround: Publish and Verify (Not Recommended)

If you absolutely cannot get Testing mode to work, you could publish the app, but this requires:
- Google's verification process (can take days/weeks)
- Privacy policy URL
- Terms of service URL
- Website URL
- Not recommended for personal use!

## Best Solution: Start Fresh

If switching to Testing mode is too complicated:
1. Create a new Google Cloud project
2. This time, **don't publish it** - keep it in Testing mode
3. Add yourself as a test user FIRST
4. Then create credentials

This is often faster than trying to fix a misconfigured project.

