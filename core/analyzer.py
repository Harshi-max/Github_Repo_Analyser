"""
Main Analyzer Module

Orchestrates the complete analysis workflow combining all analyzers.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from core.github_fetcher import GitHubFetcher
from core.scoring_engine import ScoringEngine
from core.activity_analyzer import ActivityAnalyzer
from core.impact_analyzer import ImpactAnalyzer
from core.rag_engine import RAGEngine
from utils.cache import Cache


class GitHubAnalyzer:
    """Main analyzer orchestrating the complete analysis."""
    
    def __init__(self, token: Optional[str] = None, openai_key: Optional[str] = None):
        """
        Initialize analyzer with all components.
        
        Args:
            token: GitHub token
            openai_key: OpenAI API key for RAG
        """
        self.github_fetcher = GitHubFetcher(token=token)
        self.scoring_engine = ScoringEngine()
        self.activity_analyzer = ActivityAnalyzer()
        self.impact_analyzer = ImpactAnalyzer()
        self.rag_engine = RAGEngine(api_key=openai_key)
        self.cache = Cache()
    
    def analyze_profile(self, username: str) -> Dict[str, Any]:
        """
        Perform complete analysis of a GitHub profile.
        
        Args:
            username: GitHub username
            
        Returns:
            Complete analysis report
        """
        # Check cache
        cached_result = self.cache.get(username)
        if cached_result:
            return cached_result
        
        # Extract username if URL provided
        clean_username = self.github_fetcher.extract_username_from_url(username)
        if not clean_username:
            return {"error": "Invalid GitHub username or URL"}
        
        # Fetch profile
        profile = self.github_fetcher.get_user_profile(clean_username)
        if "error" in profile:
            # Return the actual GitHub API error (includes rate limit info)
            return profile
        
        if not profile:
            return {"error": f"Could not fetch profile for {clean_username}"}
        
        # Fetch repositories
        repos = self.github_fetcher.get_user_repos(clean_username)
        if not repos:
            return {
                "error": f"No public repositories found for {clean_username}",
                "profile": profile
            }
        
        # Fetch READMEs
        readmes = {}
        for repo in repos:
            readme = self.github_fetcher.get_repo_readme(
                profile.get("login"),
                repo.get("name")
            )
            if readme:
                readmes[repo.get("name")] = readme
        
        # Fetch commits for activity analysis
        repos_with_commits = {}
        for repo in repos:
            commits = self.github_fetcher.get_repo_commits(
                profile.get("login"),
                repo.get("name")
            )
            if commits:
                repos_with_commits[repo.get("name")] = commits
        
        # Calculate scores
        doc_score = self.scoring_engine.calculate_documentation_score(repos, readmes)
        structure_score = self.scoring_engine.calculate_code_structure_score(repos, readmes)
        activity_score = self.scoring_engine.calculate_activity_score(profile, repos_with_commits)
        org_score = self.scoring_engine.calculate_organization_score(repos, profile)
        impact_score = self.scoring_engine.calculate_impact_score(repos, profile)
        
        category_scores = {
            "documentation": doc_score,
            "code_structure": structure_score,
            "activity": activity_score,
            "organization": org_score,
            "impact": impact_score,
        }
        
        total_score = self.scoring_engine.calculate_total_score(category_scores)
        score_summary = self.scoring_engine.generate_score_summary(
            total_score, category_scores, profile
        )
        
        # Activity analysis
        activity_data = self.activity_analyzer.analyze_commitment(repos_with_commits)
        consistency_data = self.activity_analyzer.analyze_consistency(repos_with_commits)
        
        # Impact analysis
        impact_data = self.impact_analyzer.analyze_repository_impact(repos, readmes)
        market_data = self.impact_analyzer.analyze_market_fit(repos)
        
        # RAG evaluation
        profile_data = {
            "repos": repos,
            "profile": profile,
            "readmes": readmes,
            "readmes_count": len(readmes),
        }
        analysis_context = self.rag_engine.generate_analysis_context(profile_data)
        rag_evaluation = self.rag_engine.evaluate_with_rag(profile_data, analysis_context)
        
        # Compile complete report
        report = {
            "username": clean_username,
            "profile": profile,
            "repositories": {
                "total_count": len(repos),
                "top_repos": repos[:5],
                "all_repos": repos,
            },
            "score_summary": score_summary,
            "category_scores": category_scores,
            "activity": {
                "commitment": activity_data,
                "consistency": consistency_data,
            },
            "impact": {
                "analysis": impact_data,
                "market": market_data,
            },
            "evaluation": rag_evaluation,
            "readmes_count": len(readmes),
            "generated_at": datetime.now().isoformat(),
        }
        
        # Cache result
        self.cache.set(username, report)
        
        return report
    
    def generate_actionable_improvements(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate actionable improvement suggestions.
        
        Args:
            analysis: Complete analysis report
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        # From RAG evaluation
        rag_recs = analysis.get("evaluation", {}).get("recommendations", [])
        if rag_recs:
            return rag_recs  # Use RAG recommendations if available
        
        # Fallback rule-based suggestions
        score_summary = analysis.get("score_summary", {})
        category_scores = score_summary.get("category_scores", {})
        repos = analysis.get("repositories", {}).get("all_repos", [])
        profile = analysis.get("profile", {})
        activity = analysis.get("activity", {}).get("commitment", {})
        
        # Find weakest category
        weakest = min(category_scores.items(), key=lambda x: x[1])
        
        if weakest[0] == "documentation":
            suggestions.append("📝 Add comprehensive READMEs to repositories. Include setup instructions, examples, and problem statements.")
        
        if weakest[0] == "code_structure":
            suggestions.append("🏗️ Improve code structure by adding tests, linting configs, and proper folder organization.")
        
        if weakest[0] == "activity":
            suggestions.append("🔥 Increase commit frequency. Aim for 2-3 commits per week across your projects.")
        
        if weakest[0] == "organization":
            suggestions.append("📊 Complete your GitHub profile: add bio, work experience, company, website, and topics to repositories.")
        
        if weakest[0] == "impact":
            suggestions.append("⭐ Focus on one high-quality project and promote it. Add deployment URLs and business value.")
        
        # Additional context-based suggestions
        if activity.get("recent_commits_90d", 0) < 10:
            suggestions.append("📅 Show recent activity by making commits in the last 30 days.")
        
        if len(repos) < 3:
            suggestions.append("📦 Build more projects to demonstrate diverse capabilities.")
        
        if not profile.get("bio"):
            suggestions.append("🎯 Write a compelling GitHub bio highlighting your specializations.")
        
        stale_repos = sum(1 for r in repos if not self._is_recent(r.get("pushed_at")))
        if stale_repos > len(repos) * 0.5:
            suggestions.append("🧹 Update or archive inactive repositories to reduce clutter.")
        
        if not any(r.get("homepage") for r in repos):
            suggestions.append("🌐 Add URLs to deployed or live versions of your projects.")
        
        stars_total = sum(r.get("stargazers_count", 0) for r in repos)
        if stars_total == 0:
            suggestions.append("⭐ Share your projects on social media, communities, and relevant forums to gain visibility.")
        
        return suggestions[:7]  # Return top 7
    
    def _is_recent(self, timestamp: Optional[str], days: int = 180) -> bool:
        """Check if timestamp is recent."""
        if not timestamp:
            return False
        try:
            date = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return (datetime.now(date.tzinfo) - date).days < days
        except:
            return False
    
    def generate_resume_bullets(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate resume bullet points from GitHub analysis.
        
        Args:
            analysis: Complete analysis report
            
        Returns:
            List of resume bullet points
        """
        bullets = []
        
        profile = analysis.get("profile", {})
        repos = analysis.get("repositories", {}).get("all_repos", [])
        impact = analysis.get("impact", {}).get("analysis", {})
        
        # Top repo bullets
        high_impact = impact.get("high_impact_repos", [])[:2]
        for repo in high_impact:
            bullets.append(f"Built {repo.get('name')} with {repo.get('stars')} GitHub stars")
        
        # Total contribution
        total_stars = sum(r.get("stargazers_count", 0) for r in repos)
        if total_stars > 10:
            bullets.append(f"Created 10+ repositories with {total_stars} combined GitHub stars")
        
        # Activity
        activity = analysis.get("activity", {}).get("commitment", {})
        total_commits = activity.get("total_commits", 0)
        if total_commits > 100:
            bullets.append(f"Made {total_commits}+ commits across open-source projects demonstrating consistent contribution")
        
        # Language diversity
        languages = set(r.get("language") for r in repos if r.get("language"))
        if len(languages) >= 3:
            bullets.append(f"Proficient in {len(languages)} programming languages and frameworks")
        
        # Business impact
        business_repos = impact.get("business_relevant", [])
        if business_repos:
            bullets.append(f"Developed {len(business_repos)} production-ready applications with market relevance")
        
        # Community
        followers = profile.get("followers", 0)
        if followers > 10:
            bullets.append(f"Followed by {followers} developers on GitHub for technical contributions")
        
        return bullets[:5]
