"""
RAG Engine Module

Implements Retrieval Augmented Generation using embeddings and LangChain
for recruiter-style evaluation and insights.
"""

import os
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

try:
    from langchain.text_splitter import CharacterTextSplitter
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.chains.qa.retrieval import RetrievalQA
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import PromptTemplate
except ImportError:
    # Fallback for newer versions
    try:
        from langchain_text_splitters import CharacterTextSplitter
        from langchain_openai import OpenAIEmbeddings, ChatOpenAI
        from langchain_community.vectorstores import FAISS
        from langchain.chains.qa.retrieval import RetrievalQA
        from langchain.prompts import PromptTemplate
    except ImportError:
        pass


class RAGEngine:
    """Recruiter-focused RAG evaluation engine."""
    
    def __init__(self, api_key: Optional[str] = None, knowledge_base_path: str = "data/recruiter_knowledge.txt"):
        """
        Initialize RAG engine.
        
        Args:
            api_key: OpenAI API key
            knowledge_base_path: Path to recruiter knowledge base
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.knowledge_base_path = knowledge_base_path
        self.vectorstore = None
        self.qa_chain = None
        self._initialized = False
        
        # Try to initialize RAG components
        try:
            if self.api_key:
                self._initialize_rag()
                self._initialized = True
        except Exception as e:
            print(f"Warning: RAG initialization failed: {e}. Falling back to rule-based evaluation.")
            self._initialized = False
    
    def _initialize_rag(self):
        """Initialize RAG components with knowledge base."""
        if not os.path.exists(self.knowledge_base_path):
            self._create_default_knowledge_base()
        
        # Load knowledge base
        with open(self.knowledge_base_path, "r") as f:
            knowledge_text = f.read()
        
        # Split text into chunks
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        texts = text_splitter.split_text(knowledge_text)
        
        # Create embeddings and vectorstore
        embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
        self.vectorstore = FAISS.from_texts(texts, embeddings)
        
        # Create QA chain
        llm = ChatOpenAI(openai_api_key=self.api_key, temperature=0.7, model="gpt-3.5-turbo")
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=False,
        )
    
    def _create_default_knowledge_base(self):
        """Create default knowledge base if it doesn't exist."""
        os.makedirs(os.path.dirname(self.knowledge_base_path), exist_ok=True)
        
        knowledge = """
RECRUITER EVALUATION GUIDE FOR GITHUB PORTFOLIOS

What Recruiters Look For:

1. CONSISTENT CONTRIBUTION PATTERN
   - Regular commits across multiple repositories
   - Activity in the last 3-6 months shows current engagement
   - Long-term involvement in projects indicates reliability
   - Diverse types of contributions (code, documentation, reviews)

2. QUALITY OVER QUANTITY
   - Well-documented, production-ready code
   - README files that demonstrate problem-solving clarity
   - Clean commit messages showing deliberate development
   - Low number of abandoned repositories

3. TECHNICAL DEPTH
   - Complex projects with multiple components
   - Use of modern frameworks and technologies
   - Evidence of learning new technologies
   - Implementation of best practices (tests, CI/CD, etc.)

4. IMPACT AND SCALE
   - Public recognition through stars/forks
   - Useful libraries or tools for others
   - Deployed/production applications
   - Metrics showing real-world usage

5. COMMUNICATION SKILLS
   - Clear, comprehensive READMEs
   - Well-structured code with comments
   - Meaningful commit messages
   - Proper use of documentation

RED FLAGS IN GITHUB PORTFOLIOS:

1. Inactive Account
   - No commits in 6+ months
   - No response to issues or PRs
   - Account created but minimal activity
   
2. Inconsistent Work Habits
   - Irregular commit patterns
   - Large gaps between activity periods
   - Pile-up of work followed by silence

3. Poor Code Quality
   - No tests or error handling
   - Minimal documentation
   - Single-file projects with no structure
   - Copy-pasted code without customization

4. Limited Technical Range
   - Only forks, no original work
   - Single technology/language never expanded
   - Incomplete projects

5. Communication Issues
   - No README files
   - Cryptic commit messages
   - No response to collaboration requests
   - Obscure code without documentation

STRONG HIRING SIGNALS:

✓ Multiple well-documented repositories with 50+ stars
✓ Regular contributions (multiple times per month)
✓ Personal projects showing initiative and creativity
✓ Evidence of impact (deployed systems, used by others)
✓ Contributions to open source projects
✓ Clear problem-solving approach in code structure
✓ Professional profile with work experience listed
✓ Diverse technology stack indicating versatility

PORTFOLIO IMPROVEMENT STRATEGIES:

1. Code Quality
   - Add unit tests to existing projects
   - Implement proper error handling
   - Use linting and formatting tools
   - Create proper folder structure

2. Documentation
   - Write comprehensive READMEs with examples
   - Add setup/installation instructions
   - Include architecture diagrams
   - Create API documentation

3. Activity
   - Make 2-3 commits per week to projects
   - Contribute to open source
   - Create demo applications
   - Maintain technical blog

4. Visibility
   - Add meaningful project descriptions
   - Use relevant topics/tags
   - Pin your best project
   - Link to deployed versions

5. Specialization
   - Build projects in your target technology stack
   - Show depth in 2-3 key areas
   - Demonstrate solve real problems
"""
        
        with open(self.knowledge_base_path, "w") as f:
            f.write(knowledge)
    
    def evaluate_with_rag(self, profile_data: Dict[str, Any], analysis_context: str) -> Dict[str, Any]:
        """
        Evaluate GitHub profile using RAG-based approach.
        
        Args:
            profile_data: User profile and repositories data
            analysis_context: Context about the profile analysis
            
        Returns:
            RAG-based evaluation results
        """
        if not self._initialized or not self.qa_chain:
            return self._fallback_evaluation(profile_data)
        
        try:
            strengths = self._evaluate_strengths(profile_data, analysis_context)
            red_flags = self._evaluate_red_flags(profile_data, analysis_context)
            recommendations = self._generate_recommendations(profile_data, analysis_context)
            
            return {
                "method": "rag_based",
                "strengths": strengths,
                "red_flags": red_flags,
                "recommendations": recommendations,
            }
        except Exception as e:
            print(f"RAG evaluation failed: {e}")
            return self._fallback_evaluation(profile_data)
    
    def _evaluate_strengths(self, profile_data: Dict[str, Any], context: str) -> List[str]:
        """Identify portfolio strengths using RAG."""
        if not self.qa_chain:
            return self._fallback_strengths(profile_data)
        
        prompt = f"""Based on this GitHub profile: {context}
        
        What are the top 3-5 technical strengths of this developer's portfolio?
        Focus on what would impress a technical recruiter.
        Return as a bullet point list."""
        
        try:
            result = self.qa_chain.run(prompt)
            strengths = [s.strip() for s in result.split("\n") if s.strip() and not s.startswith("Based on")]
            return strengths[:5]
        except:
            return self._fallback_strengths(profile_data)
    
    def _evaluate_red_flags(self, profile_data: Dict[str, Any], context: str) -> List[str]:
        """Identify portfolio red flags using RAG."""
        if not self.qa_chain:
            return self._fallback_red_flags(profile_data)
        
        prompt = f"""Based on this GitHub profile: {context}
        
        What are the top 3-4 potential concerns or red flags in this portfolio?
        Focus on what would concern a technical recruiter.
        Return as a bullet point list."""
        
        try:
            result = self.qa_chain.run(prompt)
            flags = [f.strip() for f in result.split("\n") if f.strip() and not f.startswith("Based on")]
            return flags[:4]
        except:
            return self._fallback_red_flags(profile_data)
    
    def _fallback_strengths(self, profile_data: Dict[str, Any]) -> List[str]:
        """Rule-based strength evaluation."""
        strengths = []
        
        repos = profile_data.get("repos", [])
        profile = profile_data.get("profile", {})
        
        # Check for high star count
        stars = sum(r.get("stargazers_count", 0) for r in repos)
        if stars > 50:
            strengths.append(f"Community recognition with {stars} total stars across repositories")
        
        # Check for diverse languages
        languages = set(r.get("language") for r in repos if r.get("language"))
        if len(languages) >= 3:
            strengths.append(f"Technical versatility spanning {len(languages)} different programming languages")
        
        # Check profile completeness
        profile_fields = ["name", "bio", "company", "location", "email", "blog"]
        filled = sum(1 for f in profile_fields if profile.get(f))
        if filled >= 4:
            strengths.append("Well-established professional profile with complete information")
        
        # Check for recent activity
        repos_with_recent = sum(1 for r in repos if self._is_recent(r.get("pushed_at")))
        if repos_with_recent >= len(repos) * 0.7:
            strengths.append("Consistent recent activity showing ongoing engagement")
        
        # Check for documentation
        readmes_count = profile_data.get("readmes_count", 0)
        if readmes_count >= len(repos) * 0.6:
            strengths.append(f"Good documentation practices with READMEs in {readmes_count} repositories")
        
        # Check for diversity
        if len(repos) > 5:
            strengths.append(f"Substantial portfolio with {len(repos)} public repositories")
        
        return strengths[:5]
    
    def _fallback_red_flags(self, profile_data: Dict[str, Any]) -> List[str]:
        """Rule-based red flag evaluation."""
        flags = []
        
        repos = profile_data.get("repos", [])
        profile = profile_data.get("profile", {})
        
        # Check for inactivity
        stale_repos = sum(1 for r in repos if not self._is_recent(r.get("pushed_at")))
        if stale_repos >= len(repos) * 0.5 and len(repos) > 2:
            flags.append(f"Over 50% of repositories appear inactive or abandoned")
        
        # Check for poor documentation
        readmes_count = profile_data.get("readmes_count", 0)
        if readmes_count < len(repos) * 0.3 and len(repos) > 2:
            flags.append(f"Limited documentation - only {readmes_count} repositories have READMEs")
        
        # Check for no stars
        stars = sum(r.get("stargazers_count", 0) for r in repos)
        if stars == 0 and len(repos) > 3:
            flags.append("No stars or recognition across repositories - consider projects may lack visibility")
        
        # Check for forked-only repos
        forks_only = sum(1 for r in repos if r.get("is_fork"))
        if forks_only > 0 and len(repos) <= 5:
            flags.append(f"Primary activity centers on forks rather than original projects")
        
        # Check profile completeness
        profile_fields = ["name", "bio", "company"]
        filled = sum(1 for f in profile_fields if profile.get(f))
        if filled < 1:
            flags.append("Minimal profile information - appears not ready for recruitment")
        
        # Check for minimal portfolio
        if len(repos) < 2:
            flags.append("Very limited number of public repositories to evaluate")
        
        return flags[:4]
    
    def _is_recent(self, timestamp: Optional[str], days: int = 180) -> bool:
        """Check if timestamp is recent."""
        if not timestamp:
            return False
        try:
            date = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return (datetime.now(date.tzinfo) - date).days < days
        except:
            return False
    
    def _generate_recommendations(self, profile_data: Dict[str, Any], context: str) -> List[str]:
        """Generate actionable recommendations."""
        if not self.qa_chain:
            return self._fallback_recommendations(profile_data)
        
        prompt = f"""Based on this GitHub profile: {context}
        
        Generate 5-7 specific, actionable recommendations for improving this developer's GitHub portfolio.
        Focus on items they can implement in the next 2-4 weeks.
        Return as a numbered list."""
        
        try:
            result = self.qa_chain.run(prompt)
            recs = [r.strip() for r in result.split("\n") if r.strip() and len(r.strip()) > 10]
            return recs[:7]
        except:
            return self._fallback_recommendations(profile_data)
    
    def _fallback_recommendations(self, profile_data: Dict[str, Any]) -> List[str]:
        """Rule-based recommendations."""
        recommendations = []
        
        repos = profile_data.get("repos", [])
        profile = profile_data.get("profile", {})
        readmes = profile_data.get("readmes", {})
        
        # Recommendation 1: Documentation
        readme_count = sum(1 for r in readmes.values() if r)
        if readme_count < len(repos):
            recommendations.append(f"Add comprehensive READMEs to {len(repos) - readme_count} repositories. Include setup instructions, examples, and problem statement.")
        
        # Recommendation 2: Recent project
        if not any(self._is_recent(r.get("pushed_at"), 30) for r in repos):
            recommendations.append("Create or update a project with recent commits (within the last month) to demonstrate current engagement.")
        
        # Recommendation 3: Stars/visibility
        stars = sum(r.get("stargazers_count", 0) for r in repos)
        if stars < 10 and len(repos) > 0:
            recommendations.append("Focus on one project and polish it: improve documentation, add features, promote on social media, or contribute to make it production-ready.")
        
        # Recommendation 4: Profile
        if not profile.get("bio"):
            recommendations.append("Write a compelling bio (50-100 words) explaining your technical interests and specialization area.")
        
        # Recommendation 5: Structure
        if len(repos) > 0:
            langs = set(r.get("language") for r in repos if r.get("language"))
            if len(langs) <= 1:
                recommendations.append("Diversify your technical skills by building projects in 2-3 different programming languages relevant to your target role.")
        
        # Recommendation 6: Contributions
        recommendation_6 = "Contribute to open-source projects. Add features, fix bugs, or improve documentation in established projects to show collaboration skills."
        if recommendation_6 not in recommendations:
            recommendations.append(recommendation_6)
        
        # Recommendation 7: Showcase
        if len(repos) > 0 and not any(r.get("homepage") for r in repos):
            recommendations.append("Add URLs to deployed/live versions of your projects (websites, apps, APIs) to demonstrate real-world impact.")
        
        return recommendations[:7]
    
    def _fallback_evaluation(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete rule-based fallback evaluation when RAG is unavailable."""
        return {
            "method": "rule_based",
            "strengths": self._fallback_strengths(profile_data),
            "red_flags": self._fallback_red_flags(profile_data),
            "recommendations": self._fallback_recommendations(profile_data),
        }
    
    def generate_analysis_context(self, profile_data: Dict[str, Any]) -> str:
        """Generate a text context for RAG evaluation."""
        repos = profile_data.get("repos", [])
        profile = profile_data.get("profile", {})
        
        context = f"""
GITHUB PROFILE SUMMARY:
User: {profile.get('login', 'Unknown')}
Name: {profile.get('name', 'Not provided')}
Bio: {profile.get('bio', 'Not provided')}
Followers: {profile.get('followers', 0)}
Public Repos: {profile.get('public_repos', 0)}
Company: {profile.get('company', 'Not specified')}

REPOSITORIES:
"""
        
        for repo in repos[:10]:  # Top 10 repos
            context += f"\n- {repo.get('name')}: {repo.get('description', 'No description')} ({repo.get('language', 'Unknown')} - {repo.get('stargazers_count', 0)} stars)"
        
        return context
