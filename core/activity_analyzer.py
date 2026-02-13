"""
Activity Analyzer Module

Analyzes GitHub activity patterns, consistency, and contribution frequency.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class ActivityAnalyzer:
    """Analyzes user activity and contribution patterns."""
    
    def __init__(self):
        """Initialize activity analyzer."""
        self.now = datetime.now()
    
    def analyze_commitment(self, repos_with_commits: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Analyze commitment and participation patterns.
        
        Focuses on:
        - Commit frequency
        - Repository maintenance
        - Contribution diversity
        
        Returns:
            Commitment analysis with patterns and insights
        """
        if not repos_with_commits:
            return {}
        
        total_commits = 0
        commits_by_repo = {}
        date_distribution = defaultdict(int)
        last_commit = None
        
        for repo_name, commits in repos_with_commits.items():
            commits_by_repo[repo_name] = len(commits)
            total_commits += len(commits)
            
            for commit in commits:
                try:
                    commit_date = datetime.fromisoformat(
                        commit.get("date", "").replace("Z", "+00:00")
                    )
                    date_distribution[commit_date.date()] += 1
                    
                    if not last_commit or commit_date > last_commit:
                        last_commit = commit_date
                except:
                    pass
        
        # Calculate metrics
        days_with_commits = len(date_distribution)
        
        # Activity level classification
        ninety_days_ago = self.now - timedelta(days=90)
        recent_commits = 0
        
        for repo_name, commits in repos_with_commits.items():
            for commit in commits:
                try:
                    commit_date = datetime.fromisoformat(
                        commit.get("date", "").replace("Z", "+00:00")
                    )
                    if commit_date > ninety_days_ago:
                        recent_commits += 1
                except:
                    pass
        
        # Classification
        if recent_commits > 50:
            activity_level = "🔥 Very Active"
        elif recent_commits > 20:
            activity_level = "✅ Active"
        elif recent_commits > 5:
            activity_level = "⚠️ Moderate"
        else:
            activity_level = "❌ Inactive"
        
        # Days since last commit
        days_since_last = None
        if last_commit:
            days_since_last = (self.now - last_commit.replace(tzinfo=None)).days
        
        return {
            "total_commits": total_commits,
            "commits_by_repo": commits_by_repo,
            "days_with_commits": days_with_commits,
            "recent_commits_90d": recent_commits,
            "activity_level": activity_level,
            "days_since_last_commit": days_since_last,
            "last_commit_date": last_commit.isoformat() if last_commit else None,
            "repositories_contributed": len(repos_with_commits),
        }
    
    def analyze_consistency(self, repos_with_commits: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Analyze consistency of contributions.
        
        Evaluates:
        - Commit frequency patterns
        - Gaps in activity
        - Engagement level
        
        Returns:
            Consistency metrics and insights
        """
        if not repos_with_commits:
            return {}
        
        all_dates = []
        
        for commits in repos_with_commits.values():
            for commit in commits:
                try:
                    commit_date = datetime.fromisoformat(
                        commit.get("date", "").replace("Z", "+00:00")
                    )
                    all_dates.append(commit_date)
                except:
                    pass
        
        if not all_dates:
            return {}
        
        all_dates.sort()
        
        # Calculate gaps
        gaps = []
        for i in range(1, len(all_dates)):
            gap = (all_dates[i] - all_dates[i-1]).days
            if gap > 0:
                gaps.append(gap)
        
        # Analyze consistency
        max_gap = max(gaps) if gaps else 0
        avg_gap = sum(gaps) / len(gaps) if gaps else 0
        
        # Consistency score (lower gaps = more consistent)
        if max_gap <= 7:
            consistency_rating = "⭐⭐⭐ Excellent - Weekly engagement"
        elif max_gap <= 30:
            consistency_rating = "⭐⭐ Good - Monthly engagement"
        elif max_gap <= 90:
            consistency_rating = "⭐ Fair - Sporadic engagement"
        else:
            consistency_rating = "❌ Poor - Inconsistent pattern"
        
        # Calculate commitment index (commits / days since first commit)
        days_active = (all_dates[-1] - all_dates[0]).days + 1
        commitment_index = len(all_dates) / days_active if days_active > 0 else 0
        
        return {
            "max_gap_days": max_gap,
            "avg_gap_days": round(avg_gap, 2),
            "consistency_rating": consistency_rating,
            "commitment_index": round(commitment_index, 3),
            "first_commit_date": all_dates[0].isoformat() if all_dates else None,
            "last_commit_date": all_dates[-1].isoformat() if all_dates else None,
            "total_days_active": days_active,
        }
    
    def get_activity_summary(self, profile: Dict[str, Any], 
                           repos_with_commits: Dict[str, List[Dict]]) -> str:
        """
        Generate human-readable activity summary.
        
        Args:
            profile: User profile
            repos_with_commits: Commits by repository
            
        Returns:
            Activity summary text
        """
        commitment = self.analyze_commitment(repos_with_commits)
        consistency = self.analyze_consistency(repos_with_commits)
        
        if not commitment or not consistency:
            return "Insufficient activity data to analyze."
        
        summary = f"""
ACTIVITY ANALYSIS:

• Activity Level: {commitment.get('activity_level', 'Unknown')}
• Total Commits: {commitment.get('total_commits', 0)}
• Recent (90 days): {commitment.get('recent_commits_90d', 0)} commits
• Last Commit: {commitment.get('days_since_last_commit', 'Unknown')} days ago
• Active Repositories: {commitment.get('repositories_contributed', 0)}

CONSISTENCY SCORE:
{consistency.get('consistency_rating', 'Unknown')}

• Max Gap Between Commits: {consistency.get('max_gap_days', 'Unknown')} days
• Average Gap: {consistency.get('avg_gap_days', 'Unknown')} days
• Engagement Index: {consistency.get('commitment_index', 'Unknown'):.3f}
• Total Active Period: {consistency.get('total_days_active', 0)} days
"""
        
        return summary
