import os
import json
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SheetsService:
    """Service to interact with Google Sheets"""
    
    def __init__(self):
        """Initialize the Google Sheets service"""
        try:
            # Get service account from file or environment variable
            service_account_path = "/etc/secrets/Pasted--type-service-account-project-id-ferrous-biplane-371416-private-key-id-a8e44c-1741852814317.txt"
            
            try:
                with open(service_account_path) as f:
                    service_account_info = json.load(f)
            except FileNotFoundError:
                # Fallback to environment variable if file not found
                service_account_json = os.environ.get("SERVICE_ACCOUNT_JSON")
                if not service_account_json:
                    raise ValueError("Service account credentials not found")
                service_account_info = json.loads(service_account_json)
            self.service_account_email = service_account_info.get('client_email')
            
            # Create credentials
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            # Build the service
            self.service = build('sheets', 'v4', credentials=credentials)
            
            # Get spreadsheet ID from environment variable
            self.spreadsheet_id = os.environ.get("SPREADSHEET_ID")
            
            logger.info("Google Sheets service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets service: {str(e)}")
            raise
    
    def _find_first_empty_row(self):
        """Find the first empty row in the spreadsheet"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='A:A'
            ).execute()
            
            values = result.get('values', [])
            return len(values) + 1
        except Exception as e:
            logger.error(f"Error finding empty row: {str(e)}")
            raise ValueError(f"Failed to find empty row: {str(e)}")

class SheetsService:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.spreadsheet_id = os.environ.get('GOOGLE_SHEETS_ID')
        self.credentials = self._get_credentials()
        self.service = build('sheets', 'v4', credentials=self.credentials)
        # Log service account email for sharing
        creds_info = json.loads(os.environ.get('GOOGLE_SHEETS_CREDENTIALS', '{}'))
        self.service_account_email = creds_info.get('client_email')
        if self.service_account_email:
            logger.info(f"Service account email: {self.service_account_email}")
        else:
            logger.error("Could not find service account email in credentials")

    def _get_credentials(self):
        """Get credentials from environment variable"""
        try:
            creds_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
            if not creds_json:
                raise ValueError("Google Sheets credentials not found in environment")

            # Parse the JSON string into a dictionary
            creds_info = json.loads(creds_json)

            return service_account.Credentials.from_service_account_info(
                creds_info,
                scopes=self.SCOPES
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse credentials JSON: {str(e)}")
            raise ValueError("Invalid Google Sheets credentials format")
        except Exception as e:
            logger.error(f"Error getting credentials: {str(e)}")
            raise ValueError(f"Failed to initialize credentials: {str(e)}")

    def _find_first_empty_row(self):
        """Find the first empty row in column A"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='A:A'  # Get all values in column A
            ).execute()

            values = result.get('values', [])
            for index, row in enumerate(values, start=1):
                # If we find an empty cell in column A
                if not row or not row[0]:
                    return index

            # If no empty cells found, return the next row
            return len(values) + 1

        except Exception as e:
            logger.error(f"Error finding first empty row: {str(e)}")
            raise ValueError("Failed to find first empty row in spreadsheet")

    def log_break(self, date, start_time, end_time, reason):
        """Log a break entry to Google Sheets"""
        try:
            if not self.spreadsheet_id:
                raise ValueError("Google Sheets ID not found in environment")

            if not self.service_account_email:
                raise ValueError("Service account email not found in credentials")

            # Find the first empty row
            first_empty_row = self._find_first_empty_row()
            logger.info(f"Found first empty row: {first_empty_row}")

            # Prepare the values to be inserted with formulas
            # Add one hour to start and end times
            start_time_obj = datetime.strptime(start_time, '%H:%M:%S')
            end_time_obj = datetime.strptime(end_time, '%H:%M:%S')
            
            adjusted_start = (start_time_obj + timedelta(hours=1)).strftime('%H:%M:%S')
            adjusted_end = (end_time_obj + timedelta(hours=1)).strftime('%H:%M:%S')
            
            values = [[
                date,           # Column A - Date
                adjusted_start, # Column B - Start Time
                adjusted_end,   # Column C - End Time
                f'=C{first_empty_row}-B{first_empty_row}',  # Column D - Duration
                reason,     # Column E - Reason
                '',        # Column F - Empty
                f'=SUMIF(A2:A{first_empty_row},A{first_empty_row},D2:D{first_empty_row})'  # Column G - Running total (same day only)
            ]]

            # Define the range for the first empty row
            range_name = f'A{first_empty_row}:G{first_empty_row}'

            body = {
                'values': values
            }

            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',  # Changed to USER_ENTERED to allow formulas
                body=body
            ).execute()

            logger.info(f"Successfully logged break entry in row {first_empty_row}: {values}")
            return result
        except HttpError as e:
            error_message = (
                f"Failed to write to Google Sheets. Please share the spreadsheet with "
                f"the service account email: {self.service_account_email} "
                f"and give it editor access."
            )
            logger.error(f"Google Sheets API error: {str(e)}")
            raise ValueError(error_message)
        except Exception as e:
            logger.error(f"Error logging break: {str(e)}")
            raise ValueError(f"Failed to log break: {str(e)}")