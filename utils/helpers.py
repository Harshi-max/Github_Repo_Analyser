"""
Helpers Module

Utility functions for the application.
"""

import re
from typing import List, Dict, Any


def format_large_number(num: int) -> str:
    """
    Format large numbers with K, M suffixes.
    
    Args:
        num: Number to format
        
    Returns:
        Formatted string
    """
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)


def extract_email(text: str) -> str:
    """
    Extract email from text.
    
    Args:
        text: Text to search
        
    Returns:
        Email address or empty string
    """
    match = re.search(r'[\w\.-]+@[\w\.-]+\.[\w\.-]+', text)
    return match.group(0) if match else ""


def validate_github_url(url: str) -> bool:
    """
    Validate GitHub URL or username.
    
    Args:
        url: URL or username to validate
        
    Returns:
        True if valid
    """
    # Check if it's a valid username (alphanumeric, hyphens, no spaces)
    username_pattern = r'^[a-zA-Z0-9\-]+$'
    
    url = url.strip()
    
    # Extract username from URL if needed
    if "github.com" in url:
        parts = url.split("github.com/")
        if len(parts) > 1:
            username = parts[1].strip("/").split("/")[0]
        else:
            return False
    else:
        username = url
    
    return bool(re.match(username_pattern, username)) and len(username) > 0


def calculate_grade(score: float) -> str:
    """
    Convert score to grade.
    
    Args:
        score: Score out of 100
        
    Returns:
        Grade letter
    """
    if score >= 90:
        return "A+"
    elif score >= 85:
        return "A"
    elif score >= 80:
        return "A-"
    elif score >= 75:
        return "B+"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    else:
        return "F"


def get_score_color(score: float) -> str:
    """
    Get color for score visualization.
    
    Args:
        score: Score out of 100
        
    Returns:
        Color code
    """
    if score >= 85:
        return "#00FF00"  # Green
    elif score >= 70:
        return "#90EE90"  # Light green
    elif score >= 50:
        return "#FFD700"  # Gold
    elif score >= 35:
        return "#FFA500"  # Orange
    else:
        return "#FF0000"  # Red


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    # Handle None or empty values
    if not text:
        return "No description"
    
    text = str(text)  # Convert to string if not already
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def format_date(date_str: str) -> str:
    """
    Format ISO date string to readable format.
    
    Args:
        date_str: ISO format date string
        
    Returns:
        Formatted date
    """
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except:
        return date_str


def create_summary_text(analysis: Dict[str, Any]) -> str:
    """
    Create a text summary of analysis.
    
    Args:
        analysis: Analysis report
        
    Returns:
        Summary text
    """
    profile = analysis.get("profile", {})
    score = analysis.get("score_summary", {})
    
    text = f"""
# GitHub Portfolio Analysis: {profile.get('name', profile.get('login'))}

**Overall Score:** {score.get('total_score', 'N/A')}/100
**Verdict:** {score.get('recruiter_verdict', {}).get('verdict', 'N/A')}

## Profile Summary
- **Location:** {profile.get('location', 'Not specified')}
- **Company:** {profile.get('company', 'Not specified')}
- **Followers:** {profile.get('followers', 0)}
- **Public Repos:** {profile.get('public_repos', 0)}

## Score Breakdown
"""
    
    for category, cat_score in score.get('category_scores', {}).items():
        text += f"- **{category.replace('_', ' ').title()}:** {cat_score}/20\n"
    
    return text


def generate_improvement_plan(analysis: Dict[str, Any], improvements: List[str]) -> str:
    """
    Generate improvement action plan.
    
    Args:
        analysis: Analysis report
        improvements: List of improvements
        
    Returns:
        Formatted improvement plan
    """
    plan = "# 🚀 GitHub Portfolio Improvement Plan\n\n"
    
    score_summary = analysis.get("score_summary", {})
    category_scores = score_summary.get("category_scores", {})
    
    # Find weakest categories
    sorted_cats = sorted(category_scores.items(), key=lambda x: x[1])
    
    plan += f"## Priority Areas\nYour portfolio is strongest in **{sorted_cats[-1][0].replace('_', ' ').title()}** and needs work in **{sorted_cats[0][0].replace('_', ' ').title()}**.\n\n"
    
    plan += "## Quick Wins (Next 1-2 Weeks)\n"
    for i, imp in enumerate(improvements[:3], 1):
        plan += f"{i}. {imp}\n"
    
    plan += "\n## Bigger Improvements (1-2 Months)\n"
    for i, imp in enumerate(improvements[3:], 1):
        plan += f"{i}. {imp}\n"
    
    return plan
