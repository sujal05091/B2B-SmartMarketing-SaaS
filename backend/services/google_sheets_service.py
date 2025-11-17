import json
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from models.user import User
from models.lead import Lead
from datetime import datetime

class GoogleSheetsService:
    """Service for syncing leads with Google Sheets"""
    
    @staticmethod
    def _get_sheets_service(user: User):
        """Get Google Sheets API service"""
        if not user.google_sheets_credentials:
            raise Exception("Google Sheets credentials not configured")
        
        try:
            creds_data = json.loads(user.google_sheets_credentials)
            credentials = service_account.Credentials.from_service_account_info(
                creds_data,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            service = build('sheets', 'v4', credentials=credentials)
            return service
        except Exception as e:
            raise Exception(f"Failed to authenticate with Google Sheets: {str(e)}")
    
    @staticmethod
    async def create_or_get_sheet(user: User, sheet_name: str = "B2B Leads") -> str:
        """
        Create a new Google Sheet or return existing sheet ID
        
        Returns:
            Sheet ID
        """
        service = GoogleSheetsService._get_sheets_service(user)
        
        try:
            # Create new spreadsheet
            spreadsheet = {
                'properties': {
                    'title': sheet_name
                },
                'sheets': [{
                    'properties': {
                        'title': 'Leads',
                        'gridProperties': {
                            'frozenRowCount': 1
                        }
                    }
                }]
            }
            
            sheet = service.spreadsheets().create(body=spreadsheet).execute()
            sheet_id = sheet.get('spreadsheetId')
            
            # Add headers
            headers = [[
                'Company Name', 'Website', 'Industry', 'Services',
                'Contact Email', 'Status', 'Email Subject', 
                'Created At', 'Notes'
            ]]
            
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range='Leads!A1:I1',
                valueInputOption='RAW',
                body={'values': headers}
            ).execute()
            
            # Format headers (bold)
            requests = [{
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True},
                            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            }]
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body={'requests': requests}
            ).execute()
            
            print(f"✅ Created Google Sheet: {sheet_id}")
            return sheet_id
            
        except HttpError as e:
            raise Exception(f"Google Sheets API error: {str(e)}")
    
    @staticmethod
    async def export_leads(user: User, leads: List[Lead]) -> dict:
        """
        Export leads to Google Sheets
        
        Args:
            user: User with Google Sheets configured
            leads: List of leads to export
            
        Returns:
            Dict with success status and sheet URL
        """
        if not user.google_sheets_enabled:
            return {"success": False, "error": "Google Sheets integration not enabled"}
        
        try:
            service = GoogleSheetsService._get_sheets_service(user)
            sheet_id = user.google_sheet_id
            
            if not sheet_id:
                # Create new sheet
                sheet_id = await GoogleSheetsService.create_or_get_sheet(user)
                user.google_sheet_id = sheet_id
                await user.save()
            
            # Prepare lead data
            values = []
            for lead in leads:
                row = [
                    lead.company_name,
                    lead.website or '',
                    lead.industry or '',
                    lead.services or '',
                    lead.contact_email or '',
                    lead.status,
                    lead.email_subject or '',
                    lead.created_at.strftime('%Y-%m-%d %H:%M'),
                    lead.notes or ''
                ]
                values.append(row)
            
            # Get current row count
            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range='Leads!A:A'
            ).execute()
            current_rows = len(result.get('values', [])) + 1
            
            # Append data
            service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=f'Leads!A{current_rows}',
                valueInputOption='RAW',
                body={'values': values}
            ).execute()
            
            sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
            print(f"✅ Exported {len(leads)} leads to Google Sheets")
            
            return {
                "success": True,
                "sheet_url": sheet_url,
                "leads_exported": len(leads)
            }
            
        except Exception as e:
            print(f"❌ Google Sheets Export Error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def sync_lead(user: User, lead: Lead) -> dict:
        """Sync a single lead to Google Sheets"""
        if user.google_sheets_enabled:
            return await GoogleSheetsService.export_leads(user, [lead])
        return {"success": False, "error": "Google Sheets not enabled"}
