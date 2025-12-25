# JappTracker

Automatically reads incoming job application emails and adds/updates them in your Notion database. Uses ChatGPT to intelligently identify job-related emails and extract relevant information.

## Features

- ✅ Automatically identifies job application emails
- ✅ Extracts job details (role, organization, status, date, job description link)
- ✅ Checks if job already exists in Notion to avoid duplicates
- ✅ Updates existing entries or creates new ones
- ✅ Supports status tracking: Applied, Interview, Rejected
- ✅ Marks processed emails as read

## Prerequisites

1. **Gmail Account** - The script uses Gmail API to read emails
2. **Notion Account** with:
   - A database set up with the required properties (see setup instructions)
   - A Notion API integration token
3. **OpenAI API Key** - For analyzing emails

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Gmail API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as the application type
   - Download the credentials file and save it as `credentials.json` in this directory

### 3. Set Up Notion Database

1. Create a new database in Notion (or use an existing one)
2. Add the following properties to your database:

   | Property Name | Type | Description |
   |--------------|------|-------------|
   | Number | Number | Sequential ID for each application |
   | Role | Title | Job title/role name |
   | Organization | Rich Text | Company/organization name |
   | Job description | URL | Link to job description |
   | Status | Select | Options: Applied, Interview, Rejected |
   | Date | Date | Date of application |
   | Notes | Rich Text | Optional notes (can be left empty) |

3. Get your Database ID:
   - Open your Notion database in a web browser
   - The URL will look like: `https://www.notion.so/workspace/DATABASE_ID?v=...`
   - Copy the `DATABASE_ID` part (32 characters, with hyphens)

4. Create a Notion Integration:
   - Go to https://www.notion.so/my-integrations 
   - Click "New integration"
   - Give it a name (e.g., "JappTracker")
   - Select your workspace
   - Copy the "Internal Integration Token"
   - Go to your database, click the "..." menu, and "Add connections" to connect your integration

### 4. Configure Environment Variables

Create a `.env` file in this directory:

```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Notion Configuration
NOTION_API_KEY=your_notion_integration_token_here
NOTION_DATABASE_ID=your_database_id_here
```

### 5. First Run

When you run the script for the first time, it will:
1. Open a browser window for Gmail authentication
2. Ask you to sign in and authorize the application
3. Save your credentials to `token.json` for future use

## Usage

Run the script:

```bash
python job_application_tracker.py
```

The script will:
1. Fetch unread emails from your Gmail inbox
2. Use ChatGPT to identify job application emails
3. Extract relevant information (role, organization, status, etc.)
4. Check if the job already exists in your Notion database
5. Create a new entry or update an existing one
6. Mark processed emails as read

You can also import and use it as a module:

```python
from job_application_tracker import JobApplicationTracker

tracker = JobApplicationTracker(notion_database_id="your_database_id")
tracker.process_emails(max_emails=20)
```

## How It Works

1. **Email Reading**: Uses Gmail API to fetch unread emails
2. **Classification**: ChatGPT analyzes each email to determine if it's job-related
3. **Information Extraction**: ChatGPT extracts structured data (role, organization, status, date, job link)
4. **Deduplication**: Checks Notion database for existing entries by role and organization
5. **Database Update**: Creates new entries or updates existing ones with latest status

## Troubleshooting

### Gmail Authentication Issues
- Make sure `credentials.json` is in the same directory as the script
- Delete `token.json` and re-authenticate if you get permission errors

### Notion API Issues
- Verify your integration is connected to the database
- Check that all required properties exist in your Notion database
- Ensure property names match exactly (case-sensitive)

### OpenAI API Issues
- Verify your API key is valid and has sufficient credits
- Check your API usage limits

## Notes

- The script processes emails in batches (default: 20 unread emails)
- Emails are marked as read after processing (even if skipped)
- Job applications are matched by both role and organization to detect duplicates
- The status field can be: "Applied", "Interview", or "Rejected"

## License

MIT License - feel free to use and modify as needed.

