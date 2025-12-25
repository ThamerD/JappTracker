"""
JappTracker - Job Application Email Tracker
Automatically reads incoming emails, identifies job applications,
and updates a Notion database.
"""

import os
import json
import re
import base64
from typing import Optional, Dict, Any
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from notion_client import Client

load_dotenv()

# Scopes required for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

@dataclass
class JobApplication:
    """Represents a job application extracted from email."""
    role: str
    organization: str
    job_description_link: Optional[str]
    status: str  # Applied, Interview, Rejected

class EmailReader:
    """Handles reading emails from Gmail."""
    
    def __init__(self):
        self.service = self._authenticate_gmail()
    
    def _authenticate_gmail(self):
        """Authenticate and return Gmail service."""
        creds = None
        # Token file stores the user's access and refresh tokens
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # If there are no valid credentials, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    def get_unread_emails(self, max_results: int = 10) -> list:
        """Fetch unread emails from inbox."""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()
            messages = results.get('messages', [])
            return messages
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def get_email_content(self, message_id: str) -> Dict[str, Any]:
        """Get full email content by message ID."""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract subject and body
            headers = message['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            date_header = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Extract body text
            body = self._extract_body(message['payload'])
            
            return {
                'id': message_id,
                'subject': subject,
                'body': body,
                'date': date_header,
                'snippet': message.get('snippet', '')
            }
        except HttpError as error:
            print(f'An error occurred: {error}')
            return {}
    
    def _extract_body(self, payload: Dict) -> str:
        """Recursively extract email body text."""
        body = ''
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                elif part['mimeType'] == 'text/html':
                    # Prefer plain text, but use HTML if that's all we have
                    if not body:
                        data = part['body'].get('data')
                        if data:
                            html = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                            # Simple HTML tag removal
                            body = re.sub('<[^<]+?>', '', html)
        else:
            if payload['mimeType'] == 'text/plain':
                data = payload['body'].get('data')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        return body
    
    def mark_as_read(self, message_id: str):
        """Mark an email as read."""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
        except HttpError as error:
            print(f'An error occurred: {error}')


class EmailAnalyzer:
    """Uses OpenAI to analyze emails and extract job application information."""
    
    def __init__(self):
        self.client = OpenAI()
    
    def is_job_application(self, email_subject: str, email_body: str) -> bool:
        """Determine if an email is job application related."""
        prompt = f"""Analyze the following email and determine if it is related to a job application (either an application submission confirmation, interview invitation, rejection, or any job application status update).

Email Subject: {email_subject}

Email Body:
{email_body[:2000]}

Respond with only "YES" or "NO" (no explanation)."""
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that identifies job application related emails. Be precise - only say YES if the email is clearly related to job applications (confirmations, interviews, rejections, status updates, etc.)."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        if not content:
            return False
        answer = content.strip().upper()
        return answer == "YES"
    
    def extract_job_info(self, email_subject: str, email_body: str) -> Optional[JobApplication]:
        """Extract job application information from email."""
        prompt = f"""Extract job application information from this email. 

Email Subject: {email_subject}

Email Body:
{email_body[:3000]}

Extract the following information:
1. Role/Job Title (the position name)
2. Organization/Company Name
3. Job description link/URL (if mentioned, otherwise return null)
4. Status: Determine the current status - one of: "Applied" (application submitted), "Interview" (interview invitation or scheduling), "Rejected" (rejection notification). Default to "Applied" if unclear.

Return a JSON object with these keys: role, organization, job_description_link, status.

If any information cannot be found, use null for that field (except status which should default to "Applied").

ONLY return valid JSON, no additional text or explanation."""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured information from emails. Always return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        try:
            content = response.choices[0].message.content
            if not content:
                return None
            
            data = json.loads(content)
            
            # Normalize status
            status = str(data.get('status', 'Applied')).strip().capitalize()
            if status not in ['Applied', 'Interview', 'Rejected']:
                status = 'Applied'
            
            # Validate role and organization
            role = data.get('role', 'Unknown')
            organization = data.get('organization', 'Unknown')
            if not role or str(role).lower() in ['null', 'unknown']:
                role = 'Unknown Role'
            if not organization or str(organization).lower() in ['null', 'unknown']:
                organization = 'Unknown Organization'
            
            # Get job description link
            job_link = data.get('job_description_link')
            job_link = str(job_link).strip() if job_link and str(job_link).strip() and job_link != 'null' else None
            
            return JobApplication(
                role=str(role).strip(),
                organization=str(organization).strip(),
                job_description_link=job_link,
                status=status
            )
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None


class NotionManager:
    """Manages Notion database operations."""
    
    def __init__(self, database_id: str):
        self.client = Client(auth=os.getenv('NOTION_API_KEY'))
        self.database_id = database_id
        # Property names match your database exactly
        self.number_prop = 'Number'
        self.role_prop = 'Role'
        self.org_prop = 'Organization'
        self.status_prop = 'Status'
        self.notes_prop = 'Notes'
        self.desc_prop = 'Job description'
    
    def _get_db_id_formats(self):
        """Get database ID in both formats (with and without hyphens)."""
        db_id_with_hyphens = f"{self.database_id[:8]}-{self.database_id[8:12]}-{self.database_id[12:16]}-{self.database_id[16:20]}-{self.database_id[20:]}"
        return [self.database_id, db_id_with_hyphens]
    
    def get_next_number(self) -> int:
        """Get the next sequential number for the job application."""
        try:
            max_num = 0
            start_cursor = None
            db_ids = self._get_db_id_formats()
            
            while True:
                search_params = {
                    "filter": {"property": "object", "value": "page"},
                    "page_size": 100
                }
                if start_cursor:
                    search_params["start_cursor"] = start_cursor
                
                search_response = self.client.search(**search_params)
                
                for page in search_response.get('results', []):
                    parent_id = page.get('parent', {}).get('database_id', '')
                    if parent_id in db_ids:
                        num = page.get('properties', {}).get(self.number_prop, {}).get('number', 0)
                        if num and num > max_num:
                            max_num = num
                
                if not search_response.get('has_more'):
                    break
                start_cursor = search_response.get('next_cursor')
            
            return int(max_num) + 1 if max_num > 0 else 1
        except Exception as e:
            print(f"Error getting next number: {e}")
            return 1
    
    def job_exists(self, role: str, organization: str) -> Optional[str]:
        """Check if a job already exists. Returns page_id if found, None otherwise."""
        if not role or not organization:
            return None
        
        role = str(role).strip()
        organization = str(organization).strip()
        if not role or not organization:
            return None
        
        try:
            start_cursor = None
            db_ids = self._get_db_id_formats()
            
            while True:
                search_params = {
                    "filter": {"property": "object", "value": "page"},
                    "page_size": 100
                }
                if start_cursor:
                    search_params["start_cursor"] = start_cursor
                
                search_response = self.client.search(**search_params)
                
                for page in search_response.get('results', []):
                    parent_id = page.get('parent', {}).get('database_id', '')
                    if parent_id not in db_ids:
                        continue
                    
                    props = page.get('properties', {})
                    role_data = props.get(self.role_prop, {}).get('title', [])
                    org_data = props.get(self.org_prop, {}).get('rich_text', [])
                    
                    page_role = role_data[0].get('plain_text', '').strip() if role_data else ''
                    page_org = org_data[0].get('plain_text', '').strip() if org_data else ''
                    
                    if page_role == role and page_org == organization:
                        return page.get('id')
                
                if not search_response.get('has_more'):
                    break
                start_cursor = search_response.get('next_cursor')
            
            return None
        except Exception as e:
            print(f"Error checking if job exists: {e}")
            return None
    
    def create_job_application(self, job: JobApplication) -> bool:
        """Create a new job application entry in Notion."""
        if not job.role or not job.organization:
            print(f"Error: Role and Organization are required")
            return False
        
        job.role = str(job.role).strip()
        job.organization = str(job.organization).strip()
        if not job.role or not job.organization:
            print(f"Error: Role and Organization cannot be empty")
            return False
        
        try:
            number = self.get_next_number()
            
            properties = {
                self.number_prop: {"number": number},
                self.role_prop: {"title": [{"text": {"content": job.role}}]},
                self.org_prop: {"rich_text": [{"text": {"content": job.organization}}]},
                self.notes_prop: {"rich_text": []}
            }
            
            # Add status
            if job.status:
                status_value = str(job.status).strip().capitalize()
                if status_value not in ['Applied', 'Interview', 'Rejected']:
                    status_value = 'Applied'
                properties[self.status_prop] = {"status": {"name": status_value}}
            
            # Add job description link if available
            if job.job_description_link:
                properties[self.desc_prop] = {"url": str(job.job_description_link)}
            
            self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            print(f"[OK] Created new job application: {job.role} at {job.organization}")
            return True
        except Exception as e:
            print(f"Error creating job application: {e}")
            return False
    
    def update_job_application(self, page_id: str, job: JobApplication) -> bool:
        """Update an existing job application in Notion."""
        try:
            properties = {}
            
            # Update status
            if job.status:
                status_value = str(job.status).strip().capitalize()
                if status_value not in ['Applied', 'Interview', 'Rejected']:
                    status_value = 'Applied'
                properties[self.status_prop] = {"status": {"name": status_value}}
            
            # Update job description link if provided
            if job.job_description_link:
                properties[self.desc_prop] = {"url": str(job.job_description_link)}
            
            if properties:
                self.client.pages.update(page_id=page_id, properties=properties)
            
            print(f"[OK] Updated job application: {job.role} at {job.organization}")
            return True
        except Exception as e:
            print(f"Error updating job application: {e}")
            return False


class JobApplicationTracker:
    """Main class that orchestrates the job application tracking process."""
    
    def __init__(self, notion_database_id: str):
        self.email_reader = EmailReader()
        self.email_analyzer = EmailAnalyzer()
        self.notion_manager = NotionManager(notion_database_id)
    
    def process_emails(self, max_emails: int = 10):
        """Process unread emails and update Notion database."""
        print("Fetching unread emails...")
        messages = self.email_reader.get_unread_emails(max_results=max_emails)
        
        if not messages:
            print("No unread emails found.")
            return
        
        print(f"Found {len(messages)} unread email(s). Processing...")
        
        for msg in messages:
            email_data = self.email_reader.get_email_content(msg['id'])
            
            if not email_data:
                continue
            
            # Handle Unicode in email subject for Windows console
            subject = email_data['subject']
            try:
                print(f"\nProcessing: {subject}")
            except UnicodeEncodeError:
                # Fallback: encode to ASCII, replacing problematic characters
                subject_safe = subject.encode('ascii', 'replace').decode('ascii')
                print(f"\nProcessing: {subject_safe}")
            
            # Check if it's a job application
            if not self.email_analyzer.is_job_application(
                email_data['subject'], 
                email_data['body']
            ):
                print("  -> Not a job application email, skipping...")
                self.email_reader.mark_as_read(msg['id'])
                continue
            
            print("  -> Job application email detected!")
            
            # Extract job information
            job = self.email_analyzer.extract_job_info(
                email_data['subject'],
                email_data['body']
            )
            
            if not job:
                print("  -> Failed to extract job information, skipping...")
                self.email_reader.mark_as_read(msg['id'])
                continue
            
            print(f"  -> Extracted: {job.role} at {job.organization} ({job.status})")
            
            # Check if job already exists
            existing_page_id = self.notion_manager.job_exists(job.role, job.organization)
            
            if existing_page_id:
                print("  -> Job already exists, updating...")
                self.notion_manager.update_job_application(existing_page_id, job)
            else:
                print("  -> New job application, creating entry...")
                self.notion_manager.create_job_application(job)
            
            # Mark email as read
            self.email_reader.mark_as_read(msg['id'])
        
        print("\n[OK] Processing complete!")


def main():
    """Main entry point."""
    # Load configuration
    notion_database_id = os.getenv('NOTION_DATABASE_ID')
    
    if not notion_database_id:
        print("ERROR: NOTION_DATABASE_ID not found in environment variables.")
        print("Please set it in your .env file.")
        return
    
    if not os.getenv('OPENAI_API_KEY'):
        print("ERROR: OPENAI_API_KEY not found in environment variables.")
        return
    
    if not os.getenv('NOTION_API_KEY'):
        print("ERROR: NOTION_API_KEY not found in environment variables.")
        return
    
    # Create tracker and process emails
    tracker = JobApplicationTracker(notion_database_id)
    tracker.process_emails(max_emails=20)


if __name__ == "__main__":
    main()

