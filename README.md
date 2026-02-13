# GitHub Portfolio Analyzer & Enhancer

> **Recruiting-Grade Portfolio Analysis Powered by AI** 📊

Analyze your GitHub profile like a technical recruiter would. Get actionable insights, skill assessment, red flags, and improvement suggestions with an AI-powered system.

[![Built with Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-red?style=flat&logo=streamlit)](https://streamlit.io)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue?style=flat&logo=python)](https://python.org)
[![License MIT](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

## 🎯 Problem Statement

GitHub portfolios are often evaluated by:
- Technical recruiters looking for hiring signals
- Companies assessing developer candidates
- Developers seeking to improve their portfolio

However, there's no standardized way to:
- Quantify portfolio strength across multiple dimensions
- Get recruiter-perspective feedback on coding projects
- Identify specific, actionable improvements
- Benchmark against hiring standards

**GitHub Portfolio Analyzer** solves this by providing AI-powered, recruiter-style portfolio evaluation.

## ✨ Key Features

### 📊 Portfolio Scoring (100 points)
Evaluates across 5 key dimensions:
- **Documentation Quality** (20): README quality, setup instructions, examples
- **Code Structure & Best Practices** (20): Organization, tests, linting
- **Activity Consistency** (20): Recent commits, contribution frequency
- **Repository Organization** (20): Profile completeness, descriptions, topics
- **Impact & Real-World Relevance** (20): Stars, forks, deployments, business fit

### 🤖 AI-Powered Evaluation
- **LLM Analysis**: GPT-3.5 for qualitative assessment
- **RAG System**: Recruiter knowledge base for context-aware insights
- **Fallback Logic**: Rule-based evaluation if LLM unavailable

### 💼 Recruiter Verdict
- ⭐⭐⭐ **85+**: Strong Hire Signal
- ⭐⭐ **70-85**: Interview Worthy
- ⭐ **50-70**: Needs Positioning
- **<50**: Needs Serious Work

### 🚀 Actionable Improvements
- 5-7 specific recommendations
- Priority ranking (quick wins vs. long-term)
- Implementation guides
- Resume bullet point generation

### 📈 Detailed Analytics
- Commit frequency and consistency analysis
- Repository impact metrics
- Language skill distribution
- Market positioning insights
- Activity trend visualization

### 💾 Export & Sharing
- JSON export of full analysis
- Markdown summary download
- Resume bullet points
- Share-ready insights

## 🏗️ Architecture

```
github-portfolio-analyzer/
├── app.py                          # Streamlit UI (main entry point)
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── core/                           # Core analysis modules
│   ├── github_fetcher.py          # GitHub API integration
│   ├── scoring_engine.py          # Portfolio scoring logic
│   ├── activity_analyzer.py       # Commit & activity patterns
│   ├── impact_analyzer.py         # Impact & business relevance
│   ├── rag_engine.py              # LLM + RAG evaluation
│   └── analyzer.py                # Main orchestrator
│
├── data/                           # Knowledge & data
│   └── recruiter_knowledge.txt    # Recruiter evaluation criteria
│
└── utils/                          # Utilities
    ├── cache.py                   # Result caching (SQLite)
    └── helpers.py                 # Helper functions
```

### Technology Stack

**Backend:**
- `Python 3.8+`
- `Streamlit` - Interactive web interface
- `Requests` - GitHub API calls
- `LangChain` - LLM orchestration
- `OpenAI` - GPT-3.5-turbo for analysis
- `FAISS` - Vector embeddings & RAG
- `SQLite` - Caching layer

**Frontend:**
- `Streamlit` - Responsive UI components
- `Plotly` - Interactive visualizations
- `Custom CSS` - Styling & theming

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- (Optional) OpenAI API key for LLM features

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/github-portfolio-analyzer.git
cd github-portfolio-analyzer
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables (optional)**
```bash
# Create .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env
echo "GITHUB_TOKEN=your_github_token_here" >> .env
```

5. **Run the application**
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 💻 Usage

### Web Interface

1. **Enter GitHub Profile**
   - Enter a GitHub username (e.g., `torvalds`)
   - Or paste a full GitHub URL (e.g., `https://github.com/torvalds`)

2. **Click "Analyze"**
   - System fetches data from GitHub API
   - Analyzes repositories, commits, activity patterns
   - Generates AI-powered evaluation
   - Takes 30-60 seconds

3. **Review Results**
   - Portfolio score and verdict
   - Category breakdown with grades
   - Strengths and red flags
   - Actionable improvement suggestions
   - Repository breakdown
   - Activity metrics
   - Export options

### Example Python Usage

```python
from core.analyzer import GitHubAnalyzer
import os

# Initialize analyzer
analyzer = GitHubAnalyzer(
    token=os.getenv("GITHUB_TOKEN"),
    openai_key=os.getenv("OPENAI_API_KEY")
)

# Analyze a profile
analysis = analyzer.analyze_profile("torvalds")

# Get score
print(f"Score: {analysis['score_summary']['total_score']}/100")

# Get verdict
verdict = analysis['score_summary']['recruiter_verdict']
print(f"Verdict: {verdict['verdict']}")

# Get improvements
improvements = analyzer.generate_actionable_improvements(analysis)
for i, imp in enumerate(improvements, 1):
    print(f"{i}. {imp}")
```

## 📊 Scoring Methodology

### Category Details

**Documentation Quality (0-20)**
- README presence and length
- Setup instructions completeness
- Problem statement clarity
- Usage examples and demos
- Screenshots/diagrams

**Code Structure (0-20)**
- Language diversity (2-3+ languages)
- Repository size and complexity
- Configuration files (tsconfig, package.json, etc.)
- Test presence indicators
- Linting and formatting signals

**Activity Consistency (0-20)**
- Commits in last 90 days
- Consistency of contribution pattern
- Account tenure and longevity
- Regularity of commits

**Repository Organization (0-20)**
- Profile completeness (bio, location, email, links)
- Repository descriptions
- Topics/tags usage
- Public repository count

**Impact & Relevance (0-20)**
- Stars and community validation
- Fork counts
- Deployment signals (live URLs)
- Business keywords (SaaS, platform, tool, etc.)
- Real-world applicability

### Verdict Thresholds

| Score | Verdict | Description |
|-------|---------|-------------|
| 85-100 | 🟢 Strong Hire | Exceptional portfolio, clear leader |
| 70-84 | 🔵 Interview Worthy | Solid contributor, good fit |
| 50-69 | 🟡 Needs Positioning | Good potential, needs refinement |
| 0-49 | 🔴 Needs Serious Work | Early stage or inconsistent |

## 🤖 RAG-Powered Evaluation

The system uses Retrieval Augmented Generation (RAG) for intelligent evaluation:

1. **Knowledge Base**: Embeddings of recruiter evaluation criteria
2. **Context Retrieval**: Finds relevant evaluation guidelines
3. **LLM Prompting**: Generates tailored feedback
4. **Fallback Logic**: Rule-based evaluation if LLM unavailable

This approach provides:
- Context-aware insights
- Professional recruiter perspective
- Specific, actionable recommendations
- Confidence-scored assessments

## 📈 Improvement Recommendations

The tool generates recommendations in priority order:

### Quick Wins (1-2 weeks)
- Add missing READMEs
- Update stale repository descriptions
- Complete GitHub profile
- Add project topics/tags

### Medium Term (1-2 months)
- Improve code documentation
- Add tests to projects
- Make recent commits
- Polish top project

### Long Term (2-6 months)
- Build new projects
- Contribute to open source
- Deploy applications
- Build in target stack

## 🔐 Security & Privacy

✅ **Secure by Default:**
- Uses public GitHub API (no authentication required)
- No personal data stored on server
- Optional caching (expires in 24 hours)
- Environment variables for secrets
- No hardcoded API keys

✅ **Data Handling:**
- API calls are read-only
- Cached data is SQLite (local)
- No data transmitted to third parties
- Optional OpenAI API respects privacy

## 📱 Deployment

### Streamlit Cloud

1. **Push to GitHub**
```bash
git push origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to [streamlit.io/cloud](https://streamlit.io/cloud)
   - Click "New app"
   - Select your repository
   - Enter `github-portfolio-analyzer/app.py`
   - Click Deploy

3. **Add Secrets**
   - In Streamlit Cloud dashboard
   - Add `OPENAI_API_KEY` (optional)
   - Add `GITHUB_TOKEN` (optional)

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Local Docker

```bash
docker build -t github-analyzer .
docker run -p 8501:8501 -e OPENAI_API_KEY="your_key" github-analyzer
```

## 🧪 Testing

```bash
# Run core components
python -c "from core.analyzer import GitHubAnalyzer; a = GitHubAnalyzer(); print(a.analyze_profile('torvalds'))"

# Test with your profile
streamlit run app.py
```

## 📊 Example Analysis Output

```json
{
  "username": "torvalds",
  "score_summary": {
    "total_score": 92.5,
    "recruiter_verdict": {
      "verdict": "Strong Hire Signal",
      "hire_confidence": 0.92
    },
    "category_scores": {
      "documentation": 18,
      "code_structure": 19,
      "activity": 20,
      "organization": 18,
      "impact": 19
    }
  },
  "evaluation": {
    "strengths": [
      "Legendary open-source contributor with global impact",
      "Decades of maintained, high-quality software",
      "Perfect consistency in long-term commitment"
    ],
    "red_flags": [],
    "recommendations": [...]
  }
}
```

## 🤝 Contributing

We welcome contributions! Please:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit changes** (`git commit -m 'Add amazing feature'`)
4. **Push to branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Areas for Improvement
- [ ] GraphQL API for deeper insights
- [ ] More sophisticated NLP analysis
- [ ] Comparative benchmarking
- [ ] Job-specific portfolio recommendations
- [ ] Integration with LinkedIn
- [ ] Portfolio report generation (PDF)
- [ ] Multi-language support

## 🗺️ Roadmap

### Phase 1 (Current)
- ✅ Basic portfolio scoring
- ✅ Recruiter evaluation
- ✅ Improvement suggestions
- ✅ Streamlit UI

### Phase 2
- 📋 GitHub Actions integration
- 📊 Historical trend analysis
- 🔄 Batch profile analysis
- 📧 Email report generation

### Phase 3
- 🎯 Job-specific recommendations
- 💼 LinkedIn integration
- 🤝 Community benchmarking
- 🎓 Learning path suggestions

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👥 Authors

**Built by:** AI Engineer & Hackathon Team

## 🙋 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/github-portfolio-analyzer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/github-portfolio-analyzer/discussions)
- **Email**: support@example.com

## 🎓 Learning Resources

**GitHub Profile Best Practices:**
- [GitHub Profile README](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile)
- [Open Source Guide](https://opensource.guide/)
- [Forking Projects](https://docs.github.com/en/get-started/quickstart/fork-a-repo)

**Technical Skills Development:**
- [The Missing Semester](https://missing.csail.mit.edu/)
- [Project-Based Learning](https://github.com/practical-tutorials/project-based-learning)
- [Coding Interview Tips](https://www.techinterviewhandbook.org/)

## � Complete File Inventory

### Project Statistics
- **Total Code**: 5,000+ lines
- **Documentation**: 2,500+ lines  
- **Core Modules**: 7 files
- **Utility Modules**: 2 files
- **Main Classes**: 8
- **Total Functions**: 100+

### Root Level Files (11)
| File | Purpose | Status |
|------|---------|--------|
| `app.py` | Streamlit web UI (700+ lines) | ✅ |
| `requirements.txt` | Python dependencies | ✅ |
| `setup.py` | Package installation | ✅ |
| `setup.bat` | Windows quick setup | ✅ |
| `setup.sh` | Linux/macOS quick setup | ✅ |
| `Dockerfile` | Docker container config | ✅ |
| `docker-compose.yml` | Docker Compose | ✅ |
| `.gitignore` | Git configuration | ✅ |
| `.env.example` | Environment template | ✅ |
| `LICENSE` | MIT License | ✅ |
| `.streamlit/config.toml` | Streamlit config | ✅ |

### Core Modules (core/, 7 files, 1850+ lines)
- `github_fetcher.py` - GitHub API integration (350+ lines)
- `scoring_engine.py` - Portfolio scoring (350+ lines)
- `activity_analyzer.py` - Activity patterns (200+ lines)
- `impact_analyzer.py` - Impact evaluation (250+ lines)
- `rag_engine.py` - LLM + RAG (400+ lines)
- `analyzer.py` - Main orchestrator (300+ lines)

### Utility Modules (utils/, 3 files, 350+ lines)
- `cache.py` - SQLite caching (150+ lines)
- `helpers.py` - Helper functions (200+ lines)

### Data Files
- `data/recruiter_knowledge.txt` - Recruiter evaluation criteria (3500+ lines)

### Optional Integrations
- `autopatch_integration/autopatch_client.py` - AutoPatch integration (250+ lines)

## 🛠️ Development Guide

### Local Development Setup

#### Prerequisites
- Python 3.8+
- Git
- pip or conda

#### Environment Setup

1. **Clone and navigate to project**
```bash
git clone https://github.com/yourusername/github-portfolio-analyzer.git
cd github-portfolio-analyzer
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Create .env file from template
cp .env.example .env

# Edit .env and add your keys:
# OPENAI_API_KEY=your_openai_key_here
# GITHUB_TOKEN=your_github_token_here  # Optional but recommended
```

5. **Run application**
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

### GitHub Token Setup (Recommended)

GitHub has different rate limits:
- **Without token**: 60 requests/hour
- **With token**: 5,000 requests/hour

To get a GitHub token:
1. Go to https://github.com/settings/tokens/new
2. Select scopes: `public_repo`, `read:user`
3. Copy the token
4. Add to `.env`: `GITHUB_TOKEN=your_token_here`
5. Restart the app

### Code Style & Standards

**Python Code Style:**
- Follow PEP 8
- Use meaningful variable names  
- Add docstrings to all functions
- Include type hints where possible
- Keep functions focused and small

**Example Function:**
```python
def analyze_repository_impact(
    repos: List[Dict[str, Any]], 
    readmes: Dict[str, str]
) -> Dict[str, Any]:
    """
    Analyze impact metrics across repositories.
    
    Args:
        repos: List of repository data dictionaries
        readmes: README contents mapped by repo name
        
    Returns:
        Dictionary containing impact analysis with metrics
    """
    # Implementation
    pass
```

### Testing

#### Manual Testing
```bash
# Test core components
python -c "from core.analyzer import GitHubAnalyzer; a = GitHubAnalyzer(); print(a.analyze_profile('torvalds'))"

# Run Streamlit app
streamlit run app.py
```

#### Automated Testing (when added)
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_scoring.py

# Run with coverage report
pytest --cov=core tests/
```

### Debugging

```python
# Add to modules for debugging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Use in code
logger.debug(f"Processing repository: {repo_name}")
logger.info(f"Score calculated: {score}")
logger.error(f"Error fetching profile: {error}")
```

## 🤝 Contributing

### Report Bugs

1. Check existing issues first
2. Create a detailed bug report with:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior  
   - Environment (OS, Python version)
   - Relevant logs/screenshots

### Suggest Features

1. Check discussions for similar ideas
2. Create a feature request with:
   - Clear use case and benefits
   - Proposed implementation
   - Usage examples

### Submit Pull Requests

#### Before Starting
- Fork the repository
- Create feature branch: `git checkout -b feature/amazing-feature`

#### Development Checklist
- [ ] Code follows PEP 8 style guide
- [ ] Added docstrings to functions
- [ ] Included type hints
- [ ] Tested locally with `streamlit run app.py`
- [ ] Updated documentation if needed
- [ ] No API keys or secrets committed

#### Commit & Push
```bash
git add .
git commit -m "Add amazing feature (#issue-number)"
git push origin feature/amazing-feature
```

#### PR Description Template
```
## Description
What changes are made and why?

## Testing
How to test this change?

## Related
Closes #issue-number
```

### Areas for Contribution
- [ ] Additional scoring categories
- [ ] GraphQL API implementation  
- [ ] Advanced NLP analysis
- [ ] Job-specific recommendations
- [ ] PDF report generation
- [ ] More visualization options
- [ ] Performance optimizations

## 🔧 API Error Handling & Troubleshooting

### GitHub API Rate Limiting

**Problem**: "Could not fetch profile" error

**Root Cause**: GitHub API rate limit exceeded
- Unauthenticated: 60 requests/hour
- Authenticated: 5,000 requests/hour

**Solution**:
```bash
# Add GitHub token to .env
GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Restart app
streamlit run app.py
```

### Common Issues

**Issue: "OPENAI_API_KEY not found"**
- Solution: Add `OPENAI_API_KEY` to `.env` file
- Or disable LLM features (analysis still works)

**Issue: "ModuleNotFoundError: No module named 'faiss'"**
- This is handled gracefully with fallback evaluation
- For better performance: `pip install faiss-cpu`

**Issue: Token imports warning**
- This is expected and safe
- Falls back to rule-based evaluation automatically

## 📋 Version History

### v1.0.0 - 2024-02-13

**Core Features**
- ✅ 5-category portfolio scoring system
- ✅ AI-powered evaluation (GPT-3.5-turbo)
- ✅ RAG-based recruiter insights
- ✅ Activity consistency analysis
- ✅ Impact evaluation
- ✅ 7+ improvement suggestions
- ✅ Resume bullet generation

**Scoring System**
- Documentation Quality (20 pts)
- Code Structure & Best Practices (20 pts)
- Activity Consistency (20 pts)
- Repository Organization (20 pts)
- Impact & Relevance (20 pts)
- **Total**: 0-100 with recruiter verdict

**Analysis Components**
- GitHub REST API integration
- Repository metrics (stars, forks, languages)
- Commit pattern analysis
- Activity trend evaluation
- README quality assessment
- Business relevance detection

**User Interface**
- Modern Streamlit web interface
- Interactive score visualization
- Category breakdown with radar chart
- Strengths and red flags display
- Actionable improvement plan
- Export (JSON, Markdown)
- Resume bullet generator
- Custom CSS styling

**Data Management**
- SQLite caching (24-hour TTL)
- GitHub API rate limit handling
- Error handling & validation
- Environment variable support
- Secure credential management

**Deployment**
- Local Streamlit
- Docker containerization
- Docker Compose
- Streamlit Cloud ready
- CI/CD ready structure

**Documentation**
- Comprehensive README
- Getting Started guide
- Architecture documentation
- Contributing guidelines
- Changelog

### Future Roadmap

**Phase 2 (Planned)**
- GitHub Actions integration
- Historical trend analysis
- Batch profile analysis
- Email report generation

**Phase 3 (Planned)**
- Job-specific recommendations
- LinkedIn integration
- Community benchmarking
- Learning path suggestions

## �🙏 Acknowledgments

- GitHub API documentation
- OpenAI for powerful LLM capabilities
- LangChain for LLM orchestration
- Streamlit for interactive UI framework
- FAISS for efficient similarity search

---

**Made with ❤️ by developers, for developers**

**[⬆ Back to Top](#github-portfolio-analyzer--enhancer)**
