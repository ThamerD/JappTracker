# Gmail API Setup Guide

This guide will walk you through setting up Gmail API access for JappTracker.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "JappTracker")
5. Click "Create"

## Step 2: Enable Gmail API

1. In your project, go to "APIs & Services" > "Library"
2. Search for "Gmail API"
3. Click on "Gmail API"
4. Click "Enable"

## Step 3: Configure OAuth Consent Screen

This is **critical** - you must add yourself as a test user!

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" (unless you have a Google Workspace account, then choose "Internal")
3. Fill in the required information:
   - **App name**: JappTracker
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
4. Click "Save and Continue"
5. On the "Scopes" page, click "Save and Continue" (no need to add scopes manually)
6. **IMPORTANT - Test Users Page**:
   - Click "+ ADD USERS"
   - Enter **your Gmail email address** (the one you'll use with JappTracker)
   - Click "Add"
   - This step is essential! Without it, you'll get an "access_denied" error
7. Click "Save and Continue"
8. Review and go back to dashboard

## Step 4: Create OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "+ CREATE CREDENTIALS" > "OAuth client ID"
3. If prompted, configure the consent screen (you should have done this in Step 3)
4. Choose application type: **"Desktop app"**
5. Name it: "JappTracker Desktop Client" (or any name)
6. Click "Create"
7. A dialog will appear with your client ID and secret
8. Click "DOWNLOAD JSON"
9. Save the file as `credentials.json` in your JappTracker directory

## Step 5: Verify Setup

Your `credentials.json` file should look like this:

```json
{
  "installed": {
    "client_id": "your-client-id.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "your-client-secret",
    "redirect_uris": ["http://localhost"]
  }
}
```

## Troubleshooting

### Error: "access_denied" or "app is being tested"

**Solution**: You need to add your email as a test user:
1. Go to "APIs & Services" > "OAuth consent screen"
2. Scroll to "Test users" section
3. Click "+ ADD USERS"
4. Add your Gmail address
5. Save and try again

### Error: "redirect_uri_mismatch"

**Solution**: Make sure you downloaded the credentials file correctly and it's in the same directory as the script.

### Error: "invalid_client"

**Solution**: 
- Verify your `credentials.json` file is correct
- Make sure you selected "Desktop app" as the application type
- Re-download the credentials if needed

## Security Notes

- Keep `credentials.json` and `token.json` secure - never commit them to version control
- The `token.json` file will be created automatically after first authentication
- If you need to re-authenticate, delete `token.json` and run the script again

## Publishing Your App (Optional)

If you want to use JappTracker without test user restrictions:

1. Go to "OAuth consent screen"
2. Click "PUBLISH APP"
3. Note: This requires verification for sensitive scopes (Gmail access)
4. For personal use, keeping it in testing mode with test users is recommended

