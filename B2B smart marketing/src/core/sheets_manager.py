"""
Google Sheets Manager Module

Manages Google Sheets integration for lead tracking and data management.

Features:
- Read/write operations
- Duplicate detection
- Data validation
- Batch updates
- Error handling and retry logic
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Dict, List, Optional
from datetime import datetime
import time
from src.utils.logger import LoggerMixin
from src.utils.config import get_config


class SheetsManager(LoggerMixin):
    """
    Manages Google Sheets operations for lead tracking.
    
    Features:
    - Create/update lead records
    - Duplicate detection
    - Batch operations
    - Column management
    """
    
    # Default sheet headers
    HEADERS = [
        'Company Name',
        'Website',
        'Contact Email',
        'Industry',
        'Services Matched',
        'Email Draft Subject',
        'Email Draft Body',
        'Portfolio File Path',
        'Date Added',
        'Status',
        'Notes'
    ]
    
    def __init__(self):
        """Initialize Google Sheets Manager."""
        self.setup_logging("SheetsManager")
        self.config = get_config()
        self.service = None
        self.spreadsheet_id = self.config.GOOGLE_SHEETS_SPREADSHEET_ID
        self.worksheet_name = self.config.GOOGLE_SHEETS_WORKSHEET_NAME
        
        # Initialize service
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Sheets API service."""
        try:
            # Load credentials
            credentials = service_account.Credentials.from_service_account_file(
                self.config.GOOGLE_SHEETS_CREDENTIALS_FILE,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            # Build service
            self.service = build('sheets', 'v4', credentials=credentials)
            self.log_info("Google Sheets service initialized successfully")
            
            # Ensure headers exist
            self._ensure_headers()
            
        except Exception as e:
            self.log_error(f"Failed to initialize Google Sheets service: {e}", exc_info=True)
            raise
    
    def _ensure_headers(self):
        """Ensure spreadsheet has the correct headers."""
        try:
            # Check if sheet exists
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            sheets = sheet_metadata.get('sheets', [])
            sheet_exists = any(
                sheet['properties']['title'] == self.worksheet_name 
                for sheet in sheets
            )
            
            if not sheet_exists:
                # Create worksheet
                self._create_worksheet()
            
            # Check headers
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.worksheet_name}!A1:K1"
            ).execute()
            
            values = result.get('values', [])
            
            if not values or values[0] != self.HEADERS:
                # Write headers
                self._write_headers()
                self.log_info("Headers written to spreadsheet")
            
        except Exception as e:
            self.log_error(f"Error ensuring headers: {e}")
    
    def _create_worksheet(self):
        """Create a new worksheet."""
        try:
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': self.worksheet_name
                        }
                    }
                }]
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=request_body
            ).execute()
            
            self.log_info(f"Created worksheet: {self.worksheet_name}")
            
        except Exception as e:
            self.log_error(f"Error creating worksheet: {e}")
            raise
    
    def _write_headers(self):
        """Write headers to the first row."""
        try:
            body = {
                'values': [self.HEADERS]
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.worksheet_name}!A1:K1",
                valueInputOption='RAW',
                body=body
            ).execute()
            
            # Format headers (bold)
            self._format_headers()
            
        except Exception as e:
            self.log_error(f"Error writing headers: {e}")
            raise
    
    def _format_headers(self):
        """Format header row (bold, background color)."""
        try:
            request_body = {
                'requests': [
                    {
                        'repeatCell': {
                            'range': {
                                'sheetId': self._get_sheet_id(),
                                'startRowIndex': 0,
                                'endRowIndex': 1
                            },
                            'cell': {
                                'userEnteredFormat': {
                                    'backgroundColor': {
                                        'red': 0.2,
                                        'green': 0.2,
                                        'blue': 0.2
                                    },
                                    'textFormat': {
                                        'bold': True,
                                        'foregroundColor': {
                                            'red': 1.0,
                                            'green': 1.0,
                                            'blue': 1.0
                                        }
                                    }
                                }
                            },
                            'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                        }
                    }
                ]
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=request_body
            ).execute()
            
        except Exception as e:
            self.log_warning(f"Could not format headers: {e}")
    
    def _get_sheet_id(self) -> int:
        """Get sheet ID by worksheet name."""
        try:
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            for sheet in sheet_metadata.get('sheets', []):
                if sheet['properties']['title'] == self.worksheet_name:
                    return sheet['properties']['sheetId']
            
            return 0  # Default to first sheet
            
        except Exception as e:
            self.log_error(f"Error getting sheet ID: {e}")
            return 0
    
    def add_lead(self, lead_data: Dict) -> Dict:
        """
        Add a new lead to the spreadsheet.
        
        Args:
            lead_data: Dictionary containing lead information
        
        Returns:
            Result dictionary with success status
        """
        self.log_info(f"Adding lead: {lead_data.get('company_name', 'Unknown')}")
        
        try:
            # Check for duplicates
            if self.is_duplicate(lead_data.get('website', '')):
                self.log_warning(f"Duplicate lead found: {lead_data.get('company_name')}")
                return {
                    'success': False,
                    'error': 'Duplicate lead',
                    'is_duplicate': True
                }
            
            # Prepare row data
            row_data = [
                lead_data.get('company_name', ''),
                lead_data.get('website', ''),
                lead_data.get('contact_email', ''),
                lead_data.get('industry', ''),
                ', '.join(lead_data.get('matched_services', [])),
                lead_data.get('email_subject', ''),
                lead_data.get('email_body', ''),
                lead_data.get('portfolio_path', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'New',
                ''
            ]
            
            # Append row
            body = {
                'values': [row_data]
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.worksheet_name}!A:K",
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            self.log_info(f"Successfully added lead: {lead_data.get('company_name')}")
            return {
                'success': True,
                'error': None,
                'is_duplicate': False,
                'updated_range': result.get('updates', {}).get('updatedRange', '')
            }
            
        except HttpError as e:
            self.log_error(f"HTTP error adding lead: {e}")
            return {
                'success': False,
                'error': str(e),
                'is_duplicate': False
            }
        except Exception as e:
            self.log_error(f"Error adding lead: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'is_duplicate': False
            }
    
    def is_duplicate(self, website: str) -> bool:
        """
        Check if a lead with the same website already exists.
        
        Args:
            website: Website URL to check
        
        Returns:
            True if duplicate exists, False otherwise
        """
        if not website:
            return False
        
        try:
            # Get all website values (column B)
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.worksheet_name}!B:B"
            ).execute()
            
            values = result.get('values', [])
            
            # Normalize URLs for comparison
            website_normalized = website.lower().strip().rstrip('/')
            
            for row in values[1:]:  # Skip header
                if row:
                    existing_website = row[0].lower().strip().rstrip('/')
                    if existing_website == website_normalized:
                        return True
            
            return False
            
        except Exception as e:
            self.log_error(f"Error checking for duplicates: {e}")
            return False
    
    def get_all_leads(self) -> List[Dict]:
        """
        Get all leads from the spreadsheet.
        
        Returns:
            List of lead dictionaries
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.worksheet_name}!A:K"
            ).execute()
            
            values = result.get('values', [])
            
            if not values or len(values) < 2:
                return []
            
            # Convert to list of dictionaries
            headers = values[0]
            leads = []
            
            for row in values[1:]:
                # Pad row if necessary
                while len(row) < len(headers):
                    row.append('')
                
                lead = dict(zip(headers, row))
                leads.append(lead)
            
            self.log_info(f"Retrieved {len(leads)} leads from spreadsheet")
            return leads
            
        except Exception as e:
            self.log_error(f"Error getting leads: {e}")
            return []
    
    def update_lead_status(self, website: str, status: str, notes: str = '') -> bool:
        """
        Update the status of a lead.
        
        Args:
            website: Website URL to identify the lead
            status: New status value
            notes: Additional notes
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the row
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.worksheet_name}!B:B"
            ).execute()
            
            values = result.get('values', [])
            row_index = None
            
            website_normalized = website.lower().strip().rstrip('/')
            
            for i, row in enumerate(values[1:], start=2):  # Start from row 2 (skip header)
                if row:
                    existing_website = row[0].lower().strip().rstrip('/')
                    if existing_website == website_normalized:
                        row_index = i
                        break
            
            if row_index is None:
                self.log_warning(f"Lead not found: {website}")
                return False
            
            # Update status and notes
            updates = []
            
            if status:
                updates.append({
                    'range': f"{self.worksheet_name}!I{row_index}",
                    'values': [[status]]
                })
            
            if notes:
                updates.append({
                    'range': f"{self.worksheet_name}!J{row_index}",
                    'values': [[notes]]
                })
            
            body = {
                'valueInputOption': 'RAW',
                'data': updates
            }
            
            self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            
            self.log_info(f"Updated lead status: {website}")
            return True
            
        except Exception as e:
            self.log_error(f"Error updating lead status: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """
        Get statistics about leads in the spreadsheet.
        
        Returns:
            Dictionary with statistics
        """
        try:
            leads = self.get_all_leads()
            
            if not leads:
                return {
                    'total_leads': 0,
                    'by_status': {},
                    'by_industry': {}
                }
            
            stats = {
                'total_leads': len(leads),
                'by_status': {},
                'by_industry': {}
            }
            
            for lead in leads:
                # Count by status
                status = lead.get('Status', 'Unknown')
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                
                # Count by industry
                industry = lead.get('Industry', 'Unknown')
                stats['by_industry'][industry] = stats['by_industry'].get(industry, 0) + 1
            
            return stats
            
        except Exception as e:
            self.log_error(f"Error getting stats: {e}")
            return {
                'total_leads': 0,
                'by_status': {},
                'by_industry': {}
            }
