# Notion Database Setup Guide

This guide will help you set up your Notion database for JappTracker.

## Step 1: Create a Database

1. Open Notion and create a new page or go to an existing page
2. Type `/database` and select "Table - Inline" or "Table - Full page"
3. Give your database a name (e.g., "Job Applications")

## Step 2: Add Required Properties

Your database needs the following properties. Here's how to add each one:

### 1. Number (Number type)
- Click the "+" button in the table header to add a new property
- Name it: **Number**
- Type: **Number**
- This will auto-populate with sequential IDs

### 2. Role (Title type)
- Add a new property
- Name it: **Role**
- Type: **Title** (this is typically the default first column)
- This stores the job title/position name

### 3. Organization (Rich Text type)
- Add a new property
- Name it: **Organization**
- Type: **Text** (or Rich Text)
- This stores the company/organization name

### 4. Job description (URL type)
- Add a new property
- Name it: **Job description** (exact name with space)
- Type: **URL**
- This stores the link to the job posting

### 5. Status (Select type)
- Add a new property
- Name it: **Status**
- Type: **Select**
- Add these three options exactly as shown:
  - `Applied`
  - `Interview`
  - `Rejected`

### 6. Date (Date type)
- Add a new property
- Name it: **Date**
- Type: **Date**
- This stores the application date

### 7. Notes (Rich Text type)
- Add a new property
- Name it: **Notes**
- Type: **Text** (or Rich Text)
- This can be left empty and filled manually when needed

## Step 3: Create Notion Integration

1. Go to https://www.notion.so/my-integrations
2. Click **"+ New integration"**
3. Fill in:
   - **Name**: JappTracker (or any name you prefer)
   - **Associated workspace**: Select your workspace
   - **Type**: Internal (recommended)
   - **Capabilities**: 
     - ✅ Read content
     - ✅ Insert content
     - ✅ Update content
4. Click **"Submit"**
5. Copy the **Internal Integration Token** (starts with `secret_`)
   - This is your `NOTION_API_KEY` for the `.env` file

## Step 4: Connect Integration to Database

1. Open your Job Applications database in Notion
2. Click the "..." (three dots) menu in the top right
3. Select **"Connections"** or **"Add connections"**
4. Find and select your integration (e.g., "JappTracker")
5. Click **"Confirm"**

## Step 5: Get Database ID

1. Open your database in a web browser (not the desktop app)
2. Look at the URL - it will look like:
   ```
   https://www.notion.so/workspace/abc123def456ghi789jkl012mno345pq?v=...
   ```
3. The Database ID is the long string between the last `/` and `?v=`
   - In the example above: `abc123def456ghi789jkl012mno345pq`
   - Remove any hyphens if present in the URL
4. Copy this ID - this is your `NOTION_DATABASE_ID` for the `.env` file

## Verification

Your database should look something like this:

| Number | Role | Organization | Job description | Status | Date | Notes |
|--------|------|--------------|-----------------|--------|------|-------|
| 1 | ... | ... | ... | Applied | ... | ... |

Make sure:
- ✅ Property names match exactly (case-sensitive)
- ✅ Property types are correct
- ✅ Status select has exactly three options: Applied, Interview, Rejected
- ✅ Integration is connected to the database
- ✅ You have the Integration Token and Database ID

## Troubleshooting

**Property name mismatch**: The script looks for exact property names. Make sure:
- "Job description" has a space (not "Job_description" or "JobDescription")
- "Status" is capitalized
- All other names match exactly

**Permission errors**: Make sure your integration is:
- Connected to the database
- Has "Insert content" and "Update content" capabilities enabled

**Database ID not working**: 
- Make sure you're using the ID from the web browser URL, not the desktop app
- The ID should be 32 characters (may include hyphens)

