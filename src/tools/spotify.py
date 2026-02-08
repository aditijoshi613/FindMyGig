"""Spotify integration for user music preferences."""
import os
from typing import Optional
from dataclasses import dataclass
from collections import Counter

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from langchain_core.tools import tool


@dataclass
class MusicProfile:
    """User's music preferences from Spotify."""
    top_artists: list[str]
    top_genres: list[str]
    top_tracks: list[str]
    recently_played: list[str]
    
    def to_context_string(self) -> str:
        """Format music profile for LLM context."""
        parts = []
        if self.top_artists:
            artists_str = ", ".join(self.top_artists[:10])
            parts.append(f"User's favorite artists: {artists_str}")
        if self.top_genres:
            genres_str = ", ".join(self.top_genres[:8])
            parts.append(f"User's favorite genres: {genres_str}")
        if self.top_tracks:
            tracks_str = ", ".join(self.top_tracks[:10])
            parts.append(f"User's favorite tracks: {tracks_str}")
        if self.recently_played:
            recent_str = ", ".join(self.recently_played[:5])
            parts.append(f"Recently listened to: {recent_str}")
        return "\n".join(parts)


def get_spotify_client(access_token: str) -> spotipy.Spotify:
    """Create Spotify client from access token."""
    return spotipy.Spotify(auth=access_token)


def fetch_user_music_profile(
    access_token: str, 
    time_range: str = "medium_term"
) -> MusicProfile:
    """
    Fetch user's Spotify listening preferences.
    
    Args:
        access_token: Spotify OAuth access token
        time_range: 'short_term' (4 weeks), 'medium_term' (6 months), 'long_term' (years)
    
    Returns:
        MusicProfile with top artists, genres, tracks, and recent plays
    """
    sp = get_spotify_client(access_token)

    top_artists: list[str] = []
    top_genres: list[str] = []
    top_tracks: list[str] = []
    recently_played: list[str] = []

    # Get top artists
    try:
        top_artists_data = sp.current_user_top_artists(limit=20, time_range=time_range)
        top_artists = [artist['name'] for artist in top_artists_data.get('items', [])]
        # Extract genres from top artists
        genres: list[str] = []
        for artist in top_artists_data.get('items', []):
            genres.extend(artist.get('genres', []))
        top_genres = [genre for genre, _ in Counter(genres).most_common(10)]
    except Exception:
        pass

    # Get top tracks
    try:
        top_tracks_data = sp.current_user_top_tracks(limit=20, time_range=time_range)
        top_tracks = [
            f"{track['name']} by {track['artists'][0]['name']}"
            for track in top_tracks_data.get('items', [])
        ]
    except Exception:
        pass

    # Get recently played tracks
    try:
        recently_played_data = sp.current_user_recently_played(limit=20)
        recently_played = [
            f"{item['track']['name']} by {item['track']['artists'][0]['name']}"
            for item in recently_played_data.get('items', [])
        ]
    except Exception:
        pass

    return MusicProfile(
        top_artists=top_artists,
        top_genres=top_genres,
        top_tracks=top_tracks,
        recently_played=recently_played,
    )


@tool
def get_user_music_taste(access_token: str) -> str:
    """
    Get user's music taste from their Spotify listening history.
    
    This tool fetches the user's top artists, genres, and recent listening history
    from Spotify to help recommend live music events that match their preferences.
    
    Args:
        access_token: Spotify OAuth access token
    
    Returns:
        Formatted string with user's music preferences
    """
    try:
        profile = fetch_user_music_profile(access_token)
        return profile.to_context_string()
    except Exception as e:
        return f"Could not fetch Spotify data: {str(e)}"


def init_spotify_oauth(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    cache_path: str = ".spotify_cache"
) -> SpotifyOAuth:
    """
    Initialize Spotify OAuth handler.
    
    Args:
        client_id: Spotify app client ID
        client_secret: Spotify app client secret
        redirect_uri: OAuth redirect URI (must match Spotify app settings)
        cache_path: Path to store OAuth token cache
    
    Returns:
        Configured SpotifyOAuth instance
    """
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="user-top-read user-read-recently-played",
        cache_path=cache_path,
        show_dialog=True  # Force login dialog for clarity
    )