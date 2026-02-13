"""
Scoring Engine Module

Calculates GitHub portfolio scores across multiple dimensions:
- Documentation Quality
- Code Structure & Best Practices
- Activity Consistency
- Repository Organization
- Impact & Real-World Relevance
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta


class ScoringEngine:
    """Calculates quantitative portfolio scores."""
    
    def __init__(self):
        """Initialize scoring engine with weights."""
        self.max_score = 100
        self.category_weights = {
            "documentation": 20,
            "code_structure": 20,
            "activity": 20,
            "organization": 20,
            "impact": 20,
        }
    
    def calculate_documentation_score(self, repos: List[Dict[str, Any]], readmes: Dict[str, str]) -> float:
        """
        Score documentation quality.
        
        Criteria:
        - README presence and quality
        - Length of README
        - Technical documentation signals
        
        Score: 0-20
        """
        if not repos:
            return 0
        
        score = 0
        readme_count = 0
        total_readme_quality = 0
        
        for repo in repos:
            if repo["name"] in readmes and readmes[repo["name"]]:
                readme_count += 1
                readme_text = readmes[repo["name"]].lower()
                
                # Calculate quality based on content
                quality = 0
                
                # Check for setup instructions
                if any(word in readme_text for word in ["setup", "install", "installation", "prerequisites"]):
                    quality += 2
                
                # Check for tech stack
                if any(word in readme_text for word in ["stack", "technologies", "built with", "requires"]):
                    quality += 2
                
                # Check for problem statement
                if any(word in readme_text for word in ["problem", "motivation", "why", "purpose", "solves"]):
                    quality += 2
                
                # Check for usage examples
                if any(word in readme_text for word in ["example", "usage", "how to use", "demo", "quickstart"]):
                    quality += 2
                
                # Check for screenshots
                if "![" in readme_text or ".png" in readme_text or ".jpg" in readme_text:
                    quality += 2
                
                # Length bonus
                length = len(readmes[repo["name"]])
                if length > 500:
                    quality += 2
                if length > 1000:
                    quality += 2
                if length > 2000:
                    quality += 2
                
                # Cap at 10 per repo
                quality = min(quality, 10)
                total_readme_quality += quality
        
        # Base score on README presence
        if readme_count > 0:
            avg_quality = total_readme_quality / readme_count
            coverage_bonus = min((readme_count / len(repos)) * 10, 10)
            score = avg_quality + coverage_bonus
        
        return min(score, 20)
    
    def calculate_code_structure_score(self, repos: List[Dict[str, Any]], readmes: Dict[str, str]) -> float:
        """
        Score code structure and best practices.
        
        Criteria:
        - Repository size and code depth
        - Presence of configuration files (indicates structure)
        - Has tests indicator
        - Folder organization signals
        
        Score: 0-20
        """
        if not repos:
            return 0
        
        score = 0
        lang_count = len(set(r.get("language") for r in repos if r.get("language")))
        
        # Language diversity (up to 4 points)
        lang_score = min(lang_count * 1.5, 4)
        score += lang_score
        
        # Repository maturity (size as proxy)
        avg_size = sum(r.get("size", 0) for r in repos) / len(repos) if repos else 0
        if avg_size > 100:
            score += 2
        if avg_size > 500:
            score += 2
        if avg_size > 2000:
            score += 2
        
        # Check for configuration files in readmes (indicates structure)
        config_indicators = [".gitignore", "package.json", "requirements.txt", "dockerfile", 
                            "setup.py", "tsconfig", "eslint", "makefile", "gradle", "pom.xml"]
        
        config_count = 0
        for readme_text in readmes.values():
            if readme_text:
                for indicator in config_indicators:
                    if indicator.lower() in readme_text.lower():
                        config_count += 1
        
        config_score = min((config_count / len(repos)) * 4 if repos else 0, 4)
        score += config_score
        
        # Test indicators in readmes
        test_keywords = ["test", "pytest", "jest", "mocha", "unittest", "coverage", "tdd"]
        test_mention = sum(1 for readme in readmes.values() 
                          if readme and any(keyword in readme.lower() for keyword in test_keywords))
        test_score = min((test_mention / len(repos)) * 2 if repos else 0, 2)
        score += test_score
        
        return min(score, 20)
    
    def calculate_activity_score(self, profile: Dict[str, Any], repos_with_commits: Dict[str, List[Dict]]) -> float:
        """
        Score activity consistency and freshness.
        
        Criteria:
        - Recent commits in past 90 days
        - Consistency of activity
        - Account age and activity distribution
        
        Score: 0-20
        """
        score = 0
        
        # Check recent activity
        now = datetime.now()
        ninety_days_ago = now - timedelta(days=90)
        
        recent_commits = 0
        total_commits = 0
        
        for commits in repos_with_commits.values():
            for commit in commits:
                total_commits += 1
                try:
                    commit_date = datetime.fromisoformat(commit.get("date", "").replace("Z", "+00:00"))
                    if commit_date > ninety_days_ago:
                        recent_commits += 1
                except:
                    pass
        
        # Recent activity (up to 8 points)
        if recent_commits > 0:
            if recent_commits > 50:
                score += 8
            elif recent_commits > 20:
                score += 6
            elif recent_commits > 5:
                score += 4
            else:
                score += 2
        
        # Total commit count as consistency indicator (up to 6 points)
        if total_commits > 500:
            score += 6
        elif total_commits > 200:
            score += 4
        elif total_commits > 50:
            score += 2
        else:
            score += 1
        
        # Account tenure (up to 6 points)
        created_at = profile.get("created_at")
        if created_at:
            try:
                account_age = datetime.now() - datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                years = account_age.days / 365
                
                if years >= 5:
                    score += 6
                elif years >= 3:
                    score += 4
                elif years >= 1:
                    score += 2
                else:
                    score += 1
            except:
                pass
        
        return min(score, 20)
    
    def calculate_organization_score(self, repos: List[Dict[str, Any]], profile: Dict[str, Any]) -> float:
        """
        Score repository organization and discoverability.
        
        Criteria:
        - Repository descriptions completeness
        - Topics/tags usage
        - Profile completeness
        - Pinned repos quality
        
        Score: 0-20
        """
        score = 0
        
        # Profile completeness (up to 5 points)
        profile_fields = ["name", "bio", "company", "location", "email", "blog", "twitter_username"]
        filled_fields = sum(1 for field in profile_fields if profile.get(field))
        profile_score = min((filled_fields / len(profile_fields)) * 5, 5)
        score += profile_score
        
        # Description completeness (up to 7 points)
        if repos:
            repos_with_desc = sum(1 for r in repos if r.get("description"))
            desc_score = min((repos_with_desc / len(repos)) * 7, 7)
            score += desc_score
        
        # Topics usage (up to 5 points)
        if repos:
            repos_with_topics = sum(1 for r in repos if r.get("topics") and len(r["topics"]) > 0)
            topic_score = min((repos_with_topics / len(repos)) * 5, 5)
            score += topic_score
        
        # Public repositories count (up to 3 points)
        public_repos = profile.get("public_repos", 0)
        if public_repos >= 10:
            score += 3
        elif public_repos >= 5:
            score += 2
        elif public_repos >= 2:
            score += 1
        
        return min(score, 20)
    
    def calculate_impact_score(self, repos: List[Dict[str, Any]], profile: Dict[str, Any]) -> float:
        """
        Score impact and real-world relevance.
        
        Criteria:
        - Stars and forks as community validation
        - Deployment indicators in repo descriptions
        - Business keywords
        - Metrics mentioned (users, scale, etc)
        
        Score: 0-20
        """
        score = 0
        
        if not repos:
            return 0
        
        # Star count (up to 6 points)
        total_stars = sum(r.get("stargazers_count", 0) for r in repos)
        if total_stars >= 100:
            score += 6
        elif total_stars >= 50:
            score += 4
        elif total_stars >= 10:
            score += 2
        else:
            score += 1
        
        # Fork count (up to 4 points)
        total_forks = sum(r.get("forks_count", 0) for r in repos)
        if total_forks >= 50:
            score += 4
        elif total_forks >= 20:
            score += 2
        elif total_forks >= 5:
            score += 1
        
        # Deployment/live signals (up to 5 points)
        live_keywords = ["live", "deploy", "production", "www.", "https://", "app", "api", "service"]
        deployment_count = 0
        for repo in repos:
            repo_text = (repo.get("description") or "") + (repo.get("homepage") or "")
            if any(keyword in repo_text.lower() for keyword in live_keywords):
                deployment_count += 1
        
        deploy_score = min((deployment_count / len(repos)) * 5, 5)
        score += deploy_score
        
        # Business impact keywords (up to 5 points)
        business_keywords = ["analytics", "saas", "platform", "framework", "library", "tool", 
                            "dashboard", "automation", "integration", "data", "ai", "ml"]
        business_count = 0
        for repo in repos:
            repo_text = ((repo.get("description") or "") + " " + 
                        " ".join(repo.get("topics", []))).lower()
            if any(keyword in repo_text for keyword in business_keywords):
                business_count += 1
        
        business_score = min((business_count / len(repos)) * 5, 5)
        score += business_score
        
        return min(score, 20)
    
    def calculate_total_score(self, category_scores: Dict[str, float]) -> float:
        """
        Calculate total portfolio score from category scores.
        
        Args:
            category_scores: Dictionary with category names and scores
            
        Returns:
            Total score out of 100
        """
        total = 0
        for category, score in category_scores.items():
            if category in self.category_weights:
                weight = self.category_weights[category]
                # Normalize to full weight and add
                total += (score / 20) * weight
        
        return min(max(total, 0), 100)
    
    def get_recruiter_verdict(self, total_score: float) -> tuple[str, str]:
        """
        Get recruiter verdict based on score.
        
        Args:
            total_score: Total portfolio score
            
        Returns:
            Tuple of (verdict, description)
        """
        if total_score >= 85:
            return "Strong Hire Signal", "Exceptional portfolio showing leadership, impact, and sustained contribution quality."
        elif total_score >= 70:
            return "Interview Worthy", "Solid contributor with demonstrated capabilities. Worth technical conversation."
        elif total_score >= 50:
            return "Needs Positioning", "Good potential but needs better portfolio presentation and some skill building."
        else:
            return "Needs Serious Work", "Early stage or inconsistent profile. Recommend focusing on contributions, documentation, and consistency."
    
    def generate_score_summary(
        self, 
        total_score: float, 
        category_scores: Dict[str, float],
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive score summary.
        
        Args:
            total_score: Total portfolio score
            category_scores: Category breakdown
            profile: User profile
            
        Returns:
            Complete score summary
        """
        verdict, description = self.get_recruiter_verdict(total_score)
        
        return {
            "total_score": round(total_score, 1),
            "max_score": 100,
            "category_scores": {k: round(v, 1) for k, v in category_scores.items()},
            "recruiter_verdict": {
                "verdict": verdict,
                "description": description,
                "hire_confidence": min(max((total_score - 40) / 50, 0), 1)  # Normalize 40-90 to 0-100%
            }
        }
