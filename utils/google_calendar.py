"""
Google Calendar integration utilities
"""
import os
from datetime import datetime, timedelta
from flask import url_for
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from database import db
from models import GoogleCalendarConnection


# Google OAuth 2.0 configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:5001/auth/google/callback')

# OAuth 2.0 scopes required for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']

# OAuth 2.0 configuration for Flow
CLIENT_CONFIG = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [GOOGLE_REDIRECT_URI]
    }
} if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET else None


def get_authorization_url():
    """
    Get Google OAuth authorization URL
    Returns: authorization URL string
    """
    if not CLIENT_CONFIG:
        raise ValueError("Google OAuth credentials not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.")
    
    flow = Flow.from_client_config(CLIENT_CONFIG, SCOPES)
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'  # Force consent to get refresh token
    )
    
    return authorization_url, state


def exchange_code_for_tokens(code, state):
    """
    Exchange authorization code for access and refresh tokens
    Args:
        code: Authorization code from callback
        state: State parameter from authorization
    Returns: credentials dict with access_token, refresh_token, etc.
    """
    if not CLIENT_CONFIG:
        raise ValueError("Google OAuth credentials not configured.")
    
    flow = Flow.from_client_config(CLIENT_CONFIG, SCOPES, state=state)
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    
    flow.fetch_token(code=code)
    
    credentials = flow.credentials
    
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
        'expiry': credentials.expiry
    }


def get_user_credentials(user_id):
    """
    Get valid credentials for a user, refreshing if necessary
    Args:
        user_id: User ID
    Returns: Credentials object or None
    """
    connection = GoogleCalendarConnection.query.filter_by(
        user_id=user_id,
        is_active=True
    ).first()
    
    if not connection:
        return None
    
    # Check if token needs refresh
    if connection.is_token_expired() and connection.refresh_token:
        credentials_dict = refresh_user_token(user_id)
        if not credentials_dict:
            return None
    else:
        credentials_dict = {
            'token': connection.access_token,
            'refresh_token': connection.refresh_token,
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'scopes': SCOPES,
            'expiry': connection.token_expiry
        }
    
    return Credentials.from_authorized_user_info(credentials_dict)


def refresh_user_token(user_id):
    """
    Refresh access token using refresh token
    Args:
        user_id: User ID
    Returns: Updated credentials dict or None
    """
    connection = GoogleCalendarConnection.query.filter_by(
        user_id=user_id,
        is_active=True
    ).first()
    
    if not connection or not connection.refresh_token:
        return None
    
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        
        credentials = Credentials(
            token=None,
            refresh_token=connection.refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET
        )
        
        credentials.refresh(Request())
        
        # Update connection with new token
        connection.access_token = credentials.token
        connection.token_expiry = credentials.expiry
        db.session.commit()
        
        return {
            'token': credentials.token,
            'refresh_token': connection.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'scopes': SCOPES,
            'expiry': credentials.expiry
        }
    except Exception as e:
        print(f"Error refreshing token for user {user_id}: {e}")
        return None


def get_calendar_service(user_id):
    """
    Get Google Calendar API service instance for a user
    Args:
        user_id: User ID
    Returns: Calendar service object or None
    """
    credentials = get_user_credentials(user_id)
    
    if not credentials:
        return None
    
    try:
        service = build('calendar', 'v3', credentials=credentials)
        return service
    except Exception as e:
        print(f"Error building calendar service for user {user_id}: {e}")
        return None


def create_calendar_event(user_id, title, start_datetime, end_datetime=None, 
                         description=None, location=None, calendar_id='primary'):
    """
    Create a calendar event in Google Calendar
    Args:
        user_id: User ID
        title: Event title
        start_datetime: Start datetime (datetime object)
        end_datetime: End datetime (datetime object), defaults to 1 hour after start
        description: Event description
        location: Event location
        calendar_id: Calendar ID (default: 'primary')
    Returns: Created event dict or None
    """
    service = get_calendar_service(user_id)
    
    if not service:
        return None
    
    # Default end time to 1 hour after start if not provided
    if not end_datetime:
        end_datetime = start_datetime + timedelta(hours=1)
    
    # Format datetime for Google Calendar API (RFC3339)
    event = {
        'summary': title,
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'Asia/Tokyo',
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'Asia/Tokyo',
        },
    }
    
    if description:
        event['description'] = description
    
    if location:
        event['location'] = location
    
    try:
        created_event = service.events().insert(
            calendarId=calendar_id,
            body=event
        ).execute()
        
        # Update last sync time
        connection = GoogleCalendarConnection.query.filter_by(
            user_id=user_id,
            is_active=True
        ).first()
        if connection:
            connection.last_sync_at = datetime.utcnow()
            db.session.commit()
        
        return created_event
    except HttpError as e:
        print(f"Error creating calendar event: {e}")
        return None


def update_calendar_event(user_id, event_id, title=None, start_datetime=None, 
                         end_datetime=None, description=None, location=None, calendar_id='primary'):
    """
    Update an existing calendar event
    Args:
        user_id: User ID
        event_id: Google Calendar event ID
        title: Event title (optional)
        start_datetime: Start datetime (optional)
        end_datetime: End datetime (optional)
        description: Event description (optional)
        location: Event location (optional)
        calendar_id: Calendar ID (default: 'primary')
    Returns: Updated event dict or None
    """
    service = get_calendar_service(user_id)
    
    if not service:
        return None
    
    try:
        # Get existing event
        event = service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        
        # Update fields if provided
        if title:
            event['summary'] = title
        if start_datetime:
            event['start'] = {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'Asia/Tokyo',
            }
        if end_datetime:
            event['end'] = {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'Asia/Tokyo',
            }
        if description is not None:
            event['description'] = description
        if location is not None:
            event['location'] = location
        
        updated_event = service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event
        ).execute()
        
        return updated_event
    except HttpError as e:
        print(f"Error updating calendar event: {e}")
        return None


def delete_calendar_event(user_id, event_id, calendar_id='primary'):
    """
    Delete a calendar event
    Args:
        user_id: User ID
        event_id: Google Calendar event ID
        calendar_id: Calendar ID (default: 'primary')
    Returns: True if successful, False otherwise
    """
    service = get_calendar_service(user_id)
    
    if not service:
        return False
    
    try:
        service.events().delete(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        
        return True
    except HttpError as e:
        print(f"Error deleting calendar event: {e}")
        return False


def get_calendar_list(user_id):
    """
    Get list of calendars available to the user
    Args:
        user_id: User ID
    Returns: List of calendar dicts or None
    """
    service = get_calendar_service(user_id)
    
    if not service:
        return None
    
    try:
        calendars = service.calendarList().list().execute()
        return calendars.get('items', [])
    except HttpError as e:
        print(f"Error getting calendar list: {e}")
        return None


def test_connection(user_id):
    """
    Test Google Calendar connection by making a simple API call
    Args:
        user_id: User ID
    Returns: True if connection is valid, False otherwise
    """
    try:
        calendars = get_calendar_list(user_id)
        return calendars is not None
    except Exception as e:
        print(f"Error testing connection: {e}")
        return False

