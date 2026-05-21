"""YouTube Music integration for user preferences."""
import json
from typing import Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from langchain_core.tools import tool


def fetch_youtube_music_profile(credentials: Credentials, max_results: int = 50) -> str:
    """
    Fetch user's YouTube Music preferences.
    
    Note: YouTube Music API is limited, so we use YouTube Data API v3 to get:
    - Liked music videos
    - Music-related subscriptions
    - Playlists with music content
    
    Args:
        credentials: Google OAuth2 credentials
        max_results: Maximum number of items to fetch
    
    Returns:
        Formatted string with user's YouTube music preferences
    """
    youtube = build('youtube', 'v3', credentials=credentials)
    
    parts = []
    
    # Get liked videos (filter for music)
    try:
        liked_request = youtube.videos().list(
            part="snippet",
            myRating="like",
            maxResults=max_results
        )
        liked_response = liked_request.execute()
        
        liked_music = []
        for item in liked_response.get('items', []):
            snippet = item['snippet']
            title = snippet['title']
            channel = snippet['channelTitle']
            
            # Filter for music-related content
            music_keywords = [
                'music', 'official', 'audio', 'live', 'concert', 
                'session', 'performance', 'acoustic', 'cover'
            ]
            if any(keyword in title.lower() for keyword in music_keywords):
                liked_music.append(f"{title} by {channel}")
        
        if liked_music:
            parts.append(f"YouTube liked music: {', '.join(liked_music[:15])}")
    except Exception as e:
        parts.append(f"Could not fetch liked videos: {str(e)}")
    
    # Get music-related subscriptions
    try:
        subs_request = youtube.subscriptions().list(
            part="snippet",
            mine=True,
            maxResults=50
        )
        subs_response = subs_request.execute()
        
        music_channels = []
        for item in subs_response.get('items', []):
            channel_title = item['snippet']['title']
            # Filter for music channels
            music_indicators = ['music', 'vevo', 'records', 'official']
            if any(indicator in channel_title.lower() for indicator in music_indicators):
                music_channels.append(channel_title)
        
        if music_channels:
            parts.append(f"Subscribed to: {', '.join(music_channels[:10])}")
    except Exception as e:
        parts.append(f"Could not fetch subscriptions: {str(e)}")
    
    if not parts:
        return "No YouTube music data available"
    
    return "\n".join(parts)


@tool
def get_youtube_music_taste(credentials_json: str) -> str:
    """
    Get user's music taste from YouTube Music.
    
    Analyzes liked music videos and subscriptions to understand user preferences.
    
    Args:
        credentials_json: JSON string containing Google OAuth2 credentials
    
    Returns:
        Formatted string with user's YouTube music preferences
    """
    try:
        creds_dict = json.loads(credentials_json)
        credentials = Credentials(**creds_dict)
        return fetch_youtube_music_profile(credentials)
    except Exception as e:
        return f"Could not fetch YouTube data: {str(e)}"


def init_youtube_oauth(client_config: dict, scopes: list[str]) -> dict:
    """
    Initialize YouTube OAuth flow.
    
    Args:
        client_config: OAuth client configuration dict
        scopes: List of OAuth scopes to request
    
    Returns:
        OAuth configuration for flow
    """
    from google_auth_oauthlib.flow import Flow
    
    flow = Flow.from_client_config(
        client_config,
        scopes=scopes,
        redirect_uri='http://localhost:8501'
    )
    
    return {
        'authorization_url': flow.authorization_url()[0],
        'flow': flow
    }