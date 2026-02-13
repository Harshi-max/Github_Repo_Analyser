"""
Impact Analyzer Module

Analyzes the impact and real-world relevance of GitHub projects.
"""

from typing import Dict, List, Any, Optional
import re


class ImpactAnalyzer:
    """Analyzes project impact and business relevance."""
    
    def __init__(self):
        """Initialize impact analyzer."""
        self.business_keywords = [
            "saas", "platform", "framework", "library", "analytics", "dashboard",
            "automation", "integration", "api", "tool", "service", "app", "application",
            "ml", "ai", "data", "enterprise", "cloud", "distributed", "scalable"
        ]
        
        self.deployment_keywords = [
            "live", "production", "deployed", "vercel", "heroku", "aws", "azure",
            "deployed", "hosting", "domain", "https://", "app.", "api.", "live."
        ]
    
    def analyze_repository_impact(self, repos: List[Dict[str, Any]], 
                                 readmes: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyze impact metrics across repositories.
        
        Evaluates:
        - Community reception (stars, forks)
        - Scale indicators
        - Real-world deployment
        - Business relevance
        
        Returns:
            Impact analysis with metrics and insights
        """
        if not repos:
            return {}
        
        impact_data = {
            "high_impact_repos": [],
            "moderate_impact_repos": [],
            "emerging_repos": [],
            "total_impact_score": 0,
            "top_language": None,
            "deployment_count": 0,
            "business_relevant": [],
        }
        
        language_counts = {}
        total_impact = 0
        
        for repo in repos:
            impact_score = self._calculate_repo_impact_score(repo, readmes)
            
            # Track languages
            lang = repo.get("language")
            if lang:
                language_counts[lang] = language_counts.get(lang, 0) + 1
            
            # Categorize by impact
            if impact_score >= 70:
                impact_data["high_impact_repos"].append({
                    "name": repo.get("name"),
                    "score": impact_score,
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                })
            elif impact_score >= 40:
                impact_data["moderate_impact_repos"].append({
                    "name": repo.get("name"),
                    "score": impact_score,
                    "stars": repo.get("stargazers_count", 0),
                })
            else:
                impact_data["emerging_repos"].append({
                    "name": repo.get("name"),
                    "score": impact_score,
                })
            
            total_impact += impact_score
        
        # Calculate averages and top metrics
        impact_data["total_impact_score"] = round(total_impact / len(repos), 1)
        
        if language_counts:
            impact_data["top_language"] = max(language_counts, key=language_counts.get)
        
        # Count deployments
        deployment_count = 0
        for repo in repos:
            if self._has_deployment_signal(repo, readmes):
                deployment_count += 1
        impact_data["deployment_count"] = deployment_count
        
        # Business relevant projects
        for repo in repos:
            if self._is_business_relevant(repo, readmes):
                impact_data["business_relevant"].append(repo.get("name"))
        
        return impact_data
    
    def _calculate_repo_impact_score(self, repo: Dict[str, Any], readmes: Dict[str, str]) -> float:
        """Calculate impact score for a single repository."""
        score = 0
        
        # Stars (up to 30 points)
        stars = repo.get("stargazers_count", 0)
        if stars >= 100:
            score += 30
        elif stars >= 50:
            score += 25
        elif stars >= 10:
            score += 20
        elif stars >= 1:
            score += 10
        
        # Forks (up to 20 points)
        forks = repo.get("forks_count", 0)
        if forks >= 50:
            score += 20
        elif forks >= 20:
            score += 15
        elif forks >= 5:
            score += 10
        elif forks >= 1:
            score += 5
        
        # Size/Complexity (up to 15 points)
        size = repo.get("size", 0)
        if size >= 2000:
            score += 15
        elif size >= 1000:
            score += 12
        elif size >= 500:
            score += 8
        elif size >= 100:
            score += 4
        
        # Documentation (up to 15 points)
        readme = readmes.get(repo.get("name"), "")
        if readme and len(readme) > 2000:
            score += 15
        elif readme and len(readme) > 1000:
            score += 10
        elif readme:
            score += 5
        
        # Business relevance (up to 20 points)
        repo_text = ((repo.get("description") or "") + " " + 
                    " ".join(repo.get("topics", []))).lower()
        
        business_score = 0
        for keyword in self.business_keywords:
            if keyword in repo_text:
                business_score += 3
        
        business_score = min(business_score, 20)
        score += business_score
        
        return min(score, 100)
    
    def _has_deployment_signal(self, repo: Dict[str, Any], readmes: Dict[str, str]) -> bool:
        """Check if repository has deployment/live signals."""
        # Check homepage
        if repo.get("homepage"):
            return True
        
        # Check README for deployment keywords
        readme = readmes.get(repo.get("name"), "").lower()
        for keyword in self.deployment_keywords:
            if keyword in readme:
                return True
        
        # Check description
        desc = (repo.get("description") or "").lower()
        for keyword in self.deployment_keywords:
            if keyword in desc:
                return True
        
        return False
    
    def _is_business_relevant(self, repo: Dict[str, Any], readmes: Dict[str, str]) -> bool:
        """Check if repository is business-relevant."""
        repo_text = ((repo.get("description") or "") + " " + 
                    " ".join(repo.get("topics", []))).lower()
        
        return any(keyword in repo_text for keyword in self.business_keywords)
    
    def analyze_market_fit(self, repos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze if projects target specific markets or problems.
        
        Returns:
            Market analysis and positioning insights
        """
        technical_repos = {
            "web": 0, "mobile": 0, "backend": 0, "frontend": 0,
            "devtools": 0, "data": 0, "ai_ml": 0, "cloud": 0
        }
        
        market_keywords = {
            "web": ["react", "vue", "angular", "nextjs", "web", "html", "css"],
            "mobile": ["react-native", "flutter", "android", "ios", "mobile"],
            "backend": ["django", "flask", "nodejs", "express", "java", "spring", "fastapi"],
            "frontend": ["react", "vue", "angular", "nextjs", "svelte"],
            "devtools": ["cli", "parser", "compiler", "linter", "formatter", "toolkit"],
            "data": ["etl", "data-pipeline", "analytics", "pandas", "dbt"],
            "ai_ml": ["tensorflow", "pytorch", "keras", "nlp", "computer-vision", "ml"],
            "cloud": ["aws", "kubernetes", "docker", "terraform", "infrastructure"]
        }
        
        for repo in repos:
            text = ((repo.get("description") or "") + " " + 
                   " ".join(repo.get("topics", []))).lower()
            
            for market, keywords in market_keywords.items():
                if any(kw in text for kw in keywords):
                    technical_repos[market] += 1
        
        # Identify primary market
        primary_market = max(technical_repos, key=technical_repos.get)
        
        return {
            "market_distribution": technical_repos,
            "primary_market": primary_market,
            "market_depth": technical_repos[primary_market],
            "market_diversity": sum(1 for v in technical_repos.values() if v > 0),
        }
    
    def generate_impact_summary(self, repos: List[Dict[str, Any]], 
                              readmes: Dict[str, str]) -> str:
        """
        Generate human-readable impact summary.
        
        Args:
            repos: Repository list
            readmes: README contents by repo name
            
        Returns:
            Impact summary text
        """
        impact = self.analyze_repository_impact(repos, readmes)
        market = self.analyze_market_fit(repos)
        
        summary = f"""
IMPACT ANALYSIS:

📊 Overall Impact Score: {impact.get('impact_score', impact.get('total_impact_score', 'N/A'))}/100

🌟 HIGH IMPACT PROJECTS: {len(impact.get('high_impact_repos', []))}
"""
        
        for repo in impact.get("high_impact_repos", [])[:3]:
            summary += f"  • {repo.get('name')}: {repo.get('score')} impact score ({repo.get('stars')} stars)\n"
        
        summary += f"""
💼 MARKET FOCUS: {market.get('primary_market', 'Diverse')}
📦 Repositories with Deployment: {impact.get('deployment_count', 0)}
🎯 Business-Relevant Projects: {len(impact.get('business_relevant', []))}

MARKET POSITIONING:
"""
        
        for market_type, count in market.get("market_distribution", {}).items():
            if count > 0:
                summary += f"  • {market_type.title()}: {count} projects\n"
        
        return summary
