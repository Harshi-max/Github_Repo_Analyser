"""
Cache Module

Handles caching of analysis results to avoid redundant API calls.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Optional
import sqlite3


class Cache:
    """Simple cache system for GitHub analysis results."""
    
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
        """
        Initialize cache.
        
        Args:
            cache_dir: Directory for cache files
            ttl_hours: Time to live for cached results in hours
        """
        self.cache_dir = cache_dir
        self.ttl_hours = ttl_hours
        self.db_path = os.path.join(cache_dir, "analysis_cache.db")
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize database
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for cache."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Database initialization failed: {e}")
    
    def set(self, key: str, value: Any) -> bool:
        """
        Store value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            
        Returns:
            True if successful
        """
        try:
            # Remove old entry if exists
            self.delete(key)
            
            # Serialize value
            serialized = json.dumps(value, default=str)
            
            # Calculate expiration
            expires_at = datetime.now() + timedelta(hours=self.ttl_hours)
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO cache (key, value, expires_at)
                VALUES (?, ?, ?)
            ''', (key, serialized, expires_at.isoformat()))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Warning: Cache write failed: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if expired/not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT value, expires_at FROM cache
                WHERE key = ?
            ''', (key,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return None
            
            value_str, expires_at_str = result
            
            # Check expiration
            expires_at = datetime.fromisoformat(expires_at_str)
            if datetime.now() > expires_at:
                self.delete(key)
                return None
            
            # Deserialize and return
            return json.loads(value_str)
        except Exception as e:
            print(f"Warning: Cache read failed: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        Delete entry from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM cache WHERE key = ?', (key,))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Warning: Cache delete failed: {e}")
            return False
    
    def clear_expired(self) -> int:
        """
        Clear expired cache entries.
        
        Returns:
            Number of entries cleared
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM cache
                WHERE expires_at < datetime('now')
            ''')
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted
        except Exception as e:
            print(f"Warning: Cache cleanup failed: {e}")
            return 0
