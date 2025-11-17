"""
Google Drive Manager Module (Bonus Feature)

Manages Google Drive integration for portfolio storage.

Features:
- Upload PDF portfolios to Drive
- Organize files in folders
- Generate shareable links
- File management (delete, update)
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from typing import Dict, Optional
from pathlib import Path
from src.utils.logger import LoggerMixin
from src.utils.config import get_config


class DriveManager(LoggerMixin):
    """
    Manages Google Drive operations for portfolio storage.
    
    Features:
    - Upload files
    - Create folders
    - Generate shareable links
    - File organization
    """
    
    def __init__(self):
        """Initialize Google Drive Manager."""
        self.setup_logging("DriveManager")
        self.config = get_config()
        self.service = None
        self.folder_id = self.config.GOOGLE_DRIVE_FOLDER_ID
        
        # Initialize service
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Drive API service."""
        try:
            # Load credentials
            credentials = service_account.Credentials.from_service_account_file(
                self.config.GOOGLE_SHEETS_CREDENTIALS_FILE,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            
            # Build service
            self.service = build('drive', 'v3', credentials=credentials)
            self.log_info("Google Drive service initialized successfully")
            
        except Exception as e:
            self.log_error(f"Failed to initialize Google Drive service: {e}", exc_info=True)
            raise
    
    def upload_file(self, file_path: str, folder_id: Optional[str] = None) -> Dict:
        """
        Upload a file to Google Drive.
        
        Args:
            file_path: Path to file to upload
            folder_id: Optional folder ID (uses default if not provided)
        
        Returns:
            Dictionary with upload result including file ID and shareable link
        """
        self.log_info(f"Uploading file: {file_path}")
        
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # File metadata
            file_metadata = {
                'name': file_path_obj.name
            }
            
            # Set parent folder
            target_folder = folder_id or self.folder_id
            if target_folder:
                file_metadata['parents'] = [target_folder]
            
            # Upload file
            media = MediaFileUpload(
                file_path,
                mimetype='application/pdf',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            # Make file shareable (anyone with link can view)
            self._make_shareable(file['id'])
            
            self.log_info(f"File uploaded successfully: {file['name']}")
            
            return {
                'success': True,
                'file_id': file['id'],
                'file_name': file['name'],
                'web_link': file.get('webViewLink', ''),
                'error': None
            }
            
        except HttpError as e:
            self.log_error(f"HTTP error uploading file: {e}")
            return {
                'success': False,
                'file_id': '',
                'file_name': '',
                'web_link': '',
                'error': str(e)
            }
        except Exception as e:
            self.log_error(f"Error uploading file: {e}", exc_info=True)
            return {
                'success': False,
                'file_id': '',
                'file_name': '',
                'web_link': '',
                'error': str(e)
            }
    
    def _make_shareable(self, file_id: str):
        """
        Make a file shareable (anyone with link can view).
        
        Args:
            file_id: Google Drive file ID
        """
        try:
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
            self.log_debug(f"File {file_id} made shareable")
            
        except Exception as e:
            self.log_warning(f"Could not make file shareable: {e}")
    
    def create_folder(self, folder_name: str, parent_folder_id: Optional[str] = None) -> Dict:
        """
        Create a new folder in Google Drive.
        
        Args:
            folder_name: Name of the folder
            parent_folder_id: Parent folder ID (optional)
        
        Returns:
            Dictionary with folder info
        """
        self.log_info(f"Creating folder: {folder_name}")
        
        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id, name'
            ).execute()
            
            self.log_info(f"Folder created: {folder['name']}")
            
            return {
                'success': True,
                'folder_id': folder['id'],
                'folder_name': folder['name'],
                'error': None
            }
            
        except Exception as e:
            self.log_error(f"Error creating folder: {e}")
            return {
                'success': False,
                'folder_id': '',
                'folder_name': '',
                'error': str(e)
            }
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from Google Drive.
        
        Args:
            file_id: File ID to delete
        
        Returns:
            True if successful, False otherwise
        """
        self.log_info(f"Deleting file: {file_id}")
        
        try:
            self.service.files().delete(fileId=file_id).execute()
            self.log_info(f"File deleted: {file_id}")
            return True
            
        except Exception as e:
            self.log_error(f"Error deleting file: {e}")
            return False
    
    def list_files(self, folder_id: Optional[str] = None, max_results: int = 100) -> list:
        """
        List files in Google Drive.
        
        Args:
            folder_id: Folder ID to list files from (optional)
            max_results: Maximum number of results
        
        Returns:
            List of file dictionaries
        """
        try:
            query = ""
            if folder_id:
                query = f"'{folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                pageSize=max_results,
                fields="files(id, name, mimeType, createdTime, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            self.log_info(f"Found {len(files)} files")
            
            return files
            
        except Exception as e:
            self.log_error(f"Error listing files: {e}")
            return []


# Example usage
if __name__ == "__main__":
    # This is a standalone test/demo
    manager = DriveManager()
    
    # Test folder creation
    folder_result = manager.create_folder("Test Portfolios")
    print(f"Folder created: {folder_result['success']}")
    
    # Test file upload (requires an actual PDF file)
    # upload_result = manager.upload_file("path/to/portfolio.pdf")
    # print(f"File uploaded: {upload_result['success']}")
