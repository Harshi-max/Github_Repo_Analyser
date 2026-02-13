"""
GitHub API Fetcher Module

Handles all GitHub REST API interactions for fetching user data,
repositories, commits, and activity information.
"""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time


class GitHubFetcher:
    """Handles GitHub API interactions with rate limiting and error handling."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub fetcher.
        
        Args:
            token: Optional GitHub personal access token for higher rate limits
        """
        self.token = token
        self.headers = self._get_headers()
        
    def _get_headers(self) -> Dict[str, str]:
        """Build request headers with authentication if available."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Portfolio-Analyzer"
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make API request with error handling and rate limit management.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response or dict with error key if request fails
        """
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            # Get rate limit info from headers
            rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', 'unknown')
            rate_limit_reset = response.headers.get('X-RateLimit-Reset', 'unknown')
            
            # Check rate limit (403 Forbidden)
            if response.status_code == 403:
                auth_status = "authenticated" if self.token else "unauthenticated"
                reset_info = ""
                if rate_limit_reset != 'unknown':
                    try:
                        reset_time = datetime.fromtimestamp(int(rate_limit_reset))
                        reset_info = f" Rate limit resets at {reset_time.strftime('%H:%M:%S UTC')}"
                    except:
                        reset_info = f" Rate limit will reset soon."
                
                error_msg = f"GitHub API rate limit exceeded ({auth_status} requests).{reset_info}"
                if not self.token:
                    error_msg += " Provide a GitHub token for 5000 requests/hour limit."
                    
                return {"error": error_msg, "rate_limited": True}
            
            # Check for not found (404)
            if response.status_code == 404:
                return {"error": "User not found on GitHub"}
            
            # Check for other errors
            if response.status_code >= 400:
                error_detail = response.text[:200] if response.text else f"HTTP {response.status_code}"
                return {"error": f"GitHub API error: {error_detail}"}
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": "API request timed out. Please try again."}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection error. Check your internet connection."}
        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {str(e)[:200]}"}
    
    def get_user_profile(self, username: str) -> Dict[str, Any]:
        """
        Fetch user profile information.
        
        Args:
            username: GitHub username
            
        Returns:
            User profile data or dict with error key
        """
        data = self._make_request(f"/users/{username}")
        if data and "error" in data:
            return data  # Return error dict from API
        
        if data:
            return {
                "login": data.get("login"),
                "name": data.get("name"),
                "bio": data.get("bio"),
                "company": data.get("company"),
                "location": data.get("location"),
                "email": data.get("email"),
                "blog": data.get("blog"),
                "twitter_username": data.get("twitter_username"),
                "public_repos": data.get("public_repos"),
                "followers": data.get("followers"),
                "following": data.get("following"),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "public_gists": data.get("public_gists"),
            }
        return {"error": "Unknown error fetching profile"}
    
    def get_user_repos(self, username: str, per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch all public repositories for a user.
        
        Args:
            username: GitHub username
            per_page: Results per page (max 100)
            
        Returns:
            List of repository data
        """
        all_repos = []
        page = 1
        
        while True:
            params = {
                "sort": "updated",
                "direction": "desc",
                "per_page": per_page,
                "page": page
            }
            
            data = self._make_request(f"/users/{username}/repos", params=params)
            
            if not data or isinstance(data, dict) and "error" in data:
                break
            
            if not data:
                break
            
            all_repos.extend(data)
            page += 1
            
            if len(data) < per_page:
                break
        
        # Clean and standardize repo data
        cleaned_repos = []
        for repo in all_repos:
            cleaned_repos.append({
                "id": repo.get("id"),
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "description": repo.get("description"),
                "url": repo.get("html_url"),
                "homepage": repo.get("homepage"),
                "topics": repo.get("topics", []),
                "language": repo.get("language"),
                "stargazers_count": repo.get("stargazers_count", 0),
                "forks_count": repo.get("forks_count", 0),
                "watchers_count": repo.get("watchers_count", 0),
                "size": repo.get("size", 0),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "pushed_at": repo.get("pushed_at"),
                "has_wiki": repo.get("has_wiki"),
                "has_pages": repo.get("has_pages"),
                "has_downloads": repo.get("has_downloads"),
                "has_issues": repo.get("has_issues"),
                "open_issues_count": repo.get("open_issues_count", 0),
                "default_branch": repo.get("default_branch"),
                "is_fork": repo.get("fork", False),
            })
        
        return cleaned_repos
    
    def get_repo_readme(self, owner: str, repo: str) -> Optional[str]:
        """
        Fetch README content from a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            README content or None
        """
        # Try different README files
        readme_files = ["README.md", "README", "readme.md", "readme"]
        
        for readme_file in readme_files:
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{readme_file}"
            headers = self.headers.copy()
            headers["Accept"] = "application/vnd.github.v3.raw"
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    return response.text
            except requests.exceptions.RequestException:
                continue
        
        return None
    
    def get_repo_commits(self, owner: str, repo: str, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch recent commits from a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            since: ISO timestamp to fetch commits since
            
        Returns:
            List of commit data
        """
        params = {
            "per_page": 100,
            "page": 1
        }
        
        if since:
            params["since"] = since
        
        data = self._make_request(f"/repos/{owner}/{repo}/commits", params=params)
        
        if data and "error" not in data and isinstance(data, list):
            commits = []
            for commit in data:
                commits.append({
                    "sha": commit.get("sha"),
                    "message": commit.get("commit", {}).get("message", ""),
                    "author": commit.get("commit", {}).get("author", {}).get("name"),
                    "author_email": commit.get("commit", {}).get("author", {}).get("email"),
                    "date": commit.get("commit", {}).get("author", {}).get("date"),
                    "url": commit.get("html_url"),
                })
            return commits
        
        return []
    
    def get_user_events(self, username: str) -> List[Dict[str, Any]]:
        """
        Fetch recent events from a user.
        
        Args:
            username: GitHub username
            
        Returns:
            List of events
        """
        data = self._make_request(f"/users/{username}/events/public", params={"per_page": 100})
        
        if data and isinstance(data, list) and "error" not in data:
            return data
        
        return []
    
    def get_user_contributions_collection(self, username: str) -> Dict[str, Any]:
        """
        Fetch contribution data (requires GraphQL, falls back to REST API estimation).
        
        This method estimates contribution data from public events.
        
        Args:
            username: GitHub username
            
        Returns:
            Contribution data estimation
        """
        events = self.get_user_events(username)
        
        contribution_types = {}
        for event in events:
            event_type = event.get("type", "Unknown")
            contribution_types[event_type] = contribution_types.get(event_type, 0) + 1
        
        return {
            "total_events": len(events),
            "contribution_types": contribution_types,
            "last_event": events[0].get("created_at") if events else None,
        }
    
    def extract_username_from_url(self, url: str) -> Optional[str]:
        """
        Extract GitHub username from various GitHub URL formats.
        
        Args:
            url: GitHub URL or username
            
        Returns:
            GitHub username or None
        """
        url = url.strip().lower()
        
        # If it's just a username
        if not ("github.com" in url or "http" in url):
            return url
        
        # Parse full GitHub URLs
        if "github.com/" in url:
            parts = url.split("github.com/")
            if len(parts) > 1:
                username = parts[1].strip("/").split("/")[0].split("?")[0]
                if username and username != "join":
                    return username
        
        return None
