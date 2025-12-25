# Quick Start Guide

Follow these steps to get started quickly with JappTracker:

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Set Up Gmail API Credentials

1. Download `credentials.json` from Google Cloud Console (see main README)
2. Place it in this directory

## 3. Configure Environment Variables

Create a `.env` file in this directory:

```env
OPENAI_API_KEY=sk-...
NOTION_API_KEY=secret_...
NOTION_DATABASE_ID=abc123...
```

## 4. Set Up Notion Database

Follow `NOTION_SETUP.md` to:
- Create a database with the required properties
- Create and connect a Notion integration
- Get your database ID

## 5. Run the Script

```bash
python job_application_tracker.py
```

First run will:
1. Open browser for Gmail authentication
2. Process unread emails
3. Add/update jobs in Notion

## Troubleshooting

**"credentials.json not found"**
- Download OAuth credentials from Google Cloud Console
- Save as `credentials.json` in this directory

**"NOTION_DATABASE_ID not found"**
- Check your `.env` file has the correct variable name
- Get the ID from your Notion database URL

**"Property 'Role' is not a title property"**
- Check property names match exactly (case-sensitive)
- Verify property types in Notion match the setup guide

