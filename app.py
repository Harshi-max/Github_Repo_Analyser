"""
GitHub Portfolio Analyzer & Enhancer

A comprehensive Streamlit application for analyzing GitHub profiles
and providing recruiter-style evaluation with actionable improvements.
"""

import streamlit as st
import os
from datetime import datetime
import json
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our modules
from core.analyzer import GitHubAnalyzer
from utils.helpers import (
    format_large_number, validate_github_url, calculate_grade,
    truncate_text, format_date, create_summary_text, generate_improvement_plan
)

# Page configuration
st.set_page_config(
    page_title="GitHub Portfolio Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern SaaS dashboard styling
st.markdown("""
<style>
    /* Global styles */
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Main background */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 0px !important;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px 20px;
        color: white;
        border-radius: 0px 0px 20px 20px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        margin-bottom: 30px;
    }
    
    .header-title {
        font-size: 2.5em;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .header-subtitle {
        font-size: 1.1em;
        font-weight: 300;
        margin: 5px 0 0 0;
        opacity: 0.95;
    }
    
    /* Input section styling */
    .input-section {
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        margin-bottom: 30px;
        border: 2px solid #f0f2f6;
        transition: all 0.3s ease;
    }
    
    .input-section:hover {
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
        border-color: #667eea;
    }
    
    /* Card styling */
    .stat-card {
        background: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
        margin: 10px 0;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    /* Score card styles */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.35);
        margin: 10px;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.45);
    }
    
    .metric-value {
        font-size: 2.5em;
        font-weight: 800;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 0.95em;
        opacity: 0.9;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Score color classes */
    .score-excellent {
        background: linear-gradient(135deg, #00d084 0%, #00c853 100%) !important;
        box-shadow: 0 8px 25px rgba(0, 208, 132, 0.35) !important;
    }
    
    .score-good {
        background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%) !important;
        box-shadow: 0 8px 25px rgba(0, 180, 219, 0.35) !important;
    }
    
    .score-fair {
        background: linear-gradient(135deg, #ffa726 0%, #fb8c00 100%) !important;
        box-shadow: 0 8px 25px rgba(255, 167, 38, 0.35) !important;
    }
    
    .score-poor {
        background: linear-gradient(135deg, #ef5350 0%, #e53935 100%) !important;
        box-shadow: 0 8px 25px rgba(239, 83, 80, 0.35) !important;
    }
    
    /* Summary boxes */
    .summary-section {
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        margin: 20px 0;
    }
    
    .strength-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-left: 5px solid #00c853;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .red-flag-box {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border-left: 5px solid #ef5350;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .recommendation-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 5px solid #2196f3;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .verdict-box {
        padding: 25px;
        border-radius: 12px;
        background: white;
        border: 2px solid #667eea;
        margin: 15px 0;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.15);
    }
    
    /* Badge styling */
    .badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
        margin: 4px 4px 4px 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-success {
        background: linear-gradient(135deg, #00d084 0%, #00c853 100%);
        color: white;
    }
    
    .badge-warning {
        background: linear-gradient(135deg, #ffa726 0%, #fb8c00 100%);
        color: white;
    }
    
    .badge-danger {
        background: linear-gradient(135deg, #ef5350 0%, #e53935 100%);
        color: white;
    }
    
    .badge-info {
        background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
        color: white;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 30px;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1em;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.35);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.45);
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.8em;
        font-weight: 700;
        color: #1a1a1a;
        margin: 30px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }
    
    /* Expandable sections */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* Data table styling */
    .dataframe {
        border-collapse: collapse;
        width: 100%;
    }
    
    .dataframe th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        text-align: left;
        font-weight: 600;
        border: none;
    }
    
    .dataframe td {
        padding: 12px 15px;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .dataframe tr:hover {
        background-color: #f5f7fa;
    }
    
    /* Chart styling */
    .plotly-container {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin: 20px 0;
    }
    
    /* Text styling */
    h1, h2, h3 {
        color: #1a1a1a;
        font-weight: 700;
    }
    
    p {
        color: #4a5568;
        line-height: 1.6;
    }
    
    /* Spinner/loading */
    .stSpinner > div {
        border-color: #667eea;
        border-right-color: transparent;
    }
    
    /* Message boxes */
    .stSuccess {
        background-color: #e8f5e9;
        border-left: 4px solid #00c853;
    }
    
    .stWarning {
        background-color: #fff3e0;
        border-left: 4px solid #ffa726;
    }
    
    .stError {
        background-color: #ffebee;
        border-left: 4px solid #ef5350;
    }
    
    .stInfo {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .metric-card {
            padding: 20px;
            margin: 5px 0;
        }
        
        .header-title {
            font-size: 1.8em;
        }
    }
</style>
""", unsafe_allow_html=True)


def get_analyzer():
    """Get or create GitHubAnalyzer instance."""
    if "analyzer" not in st.session_state:
        github_token = os.getenv("GITHUB_TOKEN")
        openai_key = os.getenv("OPENAI_API_KEY")
        st.session_state.analyzer = GitHubAnalyzer(
            token=github_token,
            openai_key=openai_key
        )
    return st.session_state.analyzer


def create_score_gauge(score: float) -> go.Figure:
    """Create gauge chart for score visualization."""
    color = "green" if score >= 85 else "blue" if score >= 70 else "orange" if score >= 50 else "red"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Portfolio Score"},
        delta={"reference": 70},
        gauge={
            "axis": {"range": [None, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 50], "color": "#ffebee"},
                {"range": [50, 70], "color": "#fff3e0"},
                {"range": [70, 85], "color": "#e8f5e9"},
                {"range": [85, 100], "color": "#c8e6c9"},
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 90,
            },
        },
    ))
    
    fig.update_layout(font={"size": 18}, height=350)
    return fig


def create_category_chart(category_scores: Dict[str, float]) -> go.Figure:
    """Create radar/polar chart for category scores."""
    categories = [cat.replace("_", " ").title() for cat in category_scores.keys()]
    scores = list(category_scores.values())
    
    fig = go.Figure(data=go.Scatterpolar(
        r=scores,
        theta=categories,
        fill="toself",
        name="Score",
        line_color="mediumpurple",
        fillcolor="rgba(147, 112, 219, 0.5)"
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 20],
                tickfont=dict(size=10),
            ),
            bgcolor="rgba(240, 240, 240, 0.5)"
        ),
        showlegend=True,
        height=450,
        font=dict(size=11),
    )
    
    return fig


def create_repo_chart(repos: list) -> go.Figure:
    """Create bar chart for top repositories."""
    top_repos = sorted(repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)[:10]
    
    names = [r.get("name") for r in top_repos]
    stars = [r.get("stargazers_count", 0) for r in top_repos]
    forks = [r.get("forks_count", 0) for r in top_repos]
    
    fig = go.Figure(data=[
        go.Bar(name="Stars", x=names, y=stars, marker_color="mediumpurple"),
        go.Bar(name="Forks", x=names, y=forks, marker_color="lightseagreen"),
    ])
    
    fig.update_layout(
        barmode="group",
        title="Top Repositories by Stars & Forks",
        xaxis_title="Repository",
        yaxis_title="Count",
        height=400,
        hovermode="x unified",
    )
    
    return fig


def display_header():
    """Display application header with modern SaaS design."""
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">📊 GitHub Portfolio Analyzer</h1>
        <p class="header-subtitle">Transform your GitHub profile into a recruiter-ready career portfolio</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Show value proposition
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        #### 📈 Score Your Portfolio
        Get an objective 0-100 rating based on recruiter standards
        """)
    with col2:
        st.markdown("""
        #### 🎯 Actionable Insights
        Specific recommendations to improve your GitHub presence
        """)
    with col3:
        st.markdown("""
        #### ⚡ AI-Powered Analysis
        Deep analysis of documentation, impact, and best practices
        """)
    
    st.markdown("<br>", unsafe_allow_html=True)


def display_input_section():
    """Display GitHub URL input section with modern styling."""
    st.markdown("""
    <div class="input-section">
        <h2 class="section-header">🔍 Analyze Your GitHub Profile</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        github_input = st.text_input(
            "GitHub Username or Profile URL",
            placeholder="e.g., torvalds or https://github.com/torvalds",
            help="Enter your GitHub username or the full profile URL",
            label_visibility="collapsed"
        )
    
    with col2:
        analyze_button = st.button("🚀 Analyze", key="analyze_btn", use_container_width=True)
    
    with col3:
        clear_button = st.button("🔄 Reset", key="reset_btn", use_container_width=True)
    
    return github_input, analyze_button, clear_button


def display_loading_animation():
    """Display loading animation."""
    with st.spinner("🔄 Analyzing GitHub profile..."):
        st.info("Fetching repositories, commits, and generating analysis. This may take up to 60 seconds...")
        return True


def display_profile_section(analysis: Dict[str, Any]):
    """Display profile overview."""
    profile = analysis.get("profile", {})
    repo_count = analysis.get("repositories", {}).get("total_count", 0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "👤 Profile",
            profile.get("name", profile.get("login", "Unknown")),
            profile.get("followers", 0).__str__() + " followers"
        )
    
    with col2:
        st.metric("📦 Repositories", repo_count)
    
    with col3:
        st.metric("⭐ Total Stars", format_large_number(
            sum(r.get("stargazers_count", 0) for r in analysis.get("repositories", {}).get("all_repos", []))
        ))
    
    with col4:
        st.metric("🍴 Total Forks", format_large_number(
            sum(r.get("forks_count", 0) for r in analysis.get("repositories", {}).get("all_repos", []))
        ))
    
    st.markdown("---")


def display_score_section(analysis: Dict[str, Any]):
    """Display score and verdict section with modern SaaS design."""
    score_summary = analysis.get("score_summary", {})
    total_score = score_summary.get("total_score", 0)
    category_scores = score_summary.get("category_scores", {})
    verdict = score_summary.get("recruiter_verdict", {})
    
    # Overall score with styling
    st.markdown("<h2 class='section-header'>📊 Portfolio Score Analysis</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.plotly_chart(create_score_gauge(total_score), use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.markdown("<h3 style='color: #667eea; margin-top: 0;'>Category Breakdown</h3>", unsafe_allow_html=True)
        
        # Sort categories by score
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        
        for category, score in sorted_categories:
            progress = min(score / 20.0, 1.0)
            category_name = category.replace('_', ' ').title()
            grade = calculate_grade(score * 5)
            
            # Color code by grade
            if score >= 18:
                badge_class = "badge-success"
            elif score >= 15:
                badge_class = "badge-info"
            elif score >= 12:
                badge_class = "badge-warning"
            else:
                badge_class = "badge-danger"
            
            col_a, col_b, col_c = st.columns([3, 0.8, 0.6])
            
            with col_a:
                st.progress(progress, text=f"{category_name}: {score}/20")
            
            with col_b:
                st.markdown(f"<span class='badge {badge_class}'>{grade}</span>", unsafe_allow_html=True)
            
            with col_c:
                st.markdown(f"<small>{int(score/20*100)}%</small>", unsafe_allow_html=True)
    
    # Display verdict with enhanced styling
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h2 class='section-header'>💼 Recruiter Verdict</h2>", unsafe_allow_html=True)
    
    verdict_text = verdict.get("verdict", "Unknown")
    verdict_desc = verdict.get("description", "")
    confidence = verdict.get("hire_confidence", 0)
    
    # Color based on verdict
    if total_score >= 85:
        verdict_color = "green"
        verdict_badge = "Excellent"
    elif total_score >= 70:
        verdict_color = "blue"
        verdict_badge = "Good"
    elif total_score >= 50:
        verdict_color = "orange"
        verdict_badge = "Fair"
    else:
        verdict_color = "red"
        verdict_badge = "Needs Improvement"
    
    st.markdown(f"""
    <div class="verdict-box" style="border-left-color: {verdict_color};">
        <h3 style="color: {verdict_color}; margin-top: 0;">{verdict_text}</h3>
        <p>{verdict_desc}</p>
        <p><strong>Hire Confidence: </strong>{confidence * 100:.0f}%</p>
    </div>
    """, unsafe_allow_html=True)


def display_strengths_and_flags(analysis: Dict[str, Any]):
    """Display strengths and red flags with modern SaaS design."""
    evaluation = analysis.get("evaluation", {})
    strengths = evaluation.get("strengths", [])
    red_flags = evaluation.get("red_flags", [])
    
    st.markdown("<h2 class='section-header'>🎯 Evaluation Summary</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 style='color: #00c853; margin-top: 0;'>✅ Key Strengths</h3>", unsafe_allow_html=True)
        if strengths:
            for strength in strengths:
                st.markdown(f"""
                <div class="strength-box">
                    <strong>✓ {strength}</strong>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("🔍 No major strengths identified yet. Focus on the recommendations below.")
    
    with col2:
        st.markdown("<h3 style='color: #ef5350; margin-top: 0;'>⚠️ Areas to Improve</h3>", unsafe_allow_html=True)
        if red_flags:
            for flag in red_flags:
                st.markdown(f"""
                <div class="red-flag-box">
                    <strong>⚠️ {flag}</strong>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🎉 No major red flags detected! Your profile is looking good.")
    
    st.markdown("<br>", unsafe_allow_html=True)


def display_improvements(analysis: Dict[str, Any], improvements: list):
    """Display actionable improvements with modern design."""
    st.markdown("<h2 class='section-header'>🚀 Growth Path - Actionable Recommendations</h2>", unsafe_allow_html=True)
    
    improvement_plan = generate_improvement_plan(analysis, improvements)
    
    # Display recommendations
    for improvement in improvements[:3]:
        st.markdown(f"""
        <div class="recommendation-box">
            <strong>💡 {improvement}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Expandable detailed guide
    with st.expander("📋 Detailed Implementation Guide", expanded=False):
        st.markdown("""
        ### Documentation Best Practices
        
        **Priority 1: Top 3 Projects**
        - Add comprehensive README with:
          - Clear problem statement
          - Solution overview
          - Installation instructions
          - Usage examples with code snippets
          - Screenshots or demo links
          - Tech stack badges
        
        **Priority 2: Code Organization**
        - Use clear folder structure
        - Add code comments for complex logic
        - Include LICENSE file
        - Add CONTRIBUTING.md for collaboration
        
        **Priority 3: Activity & Impact**
        - Maintain consistent commit history
        - Add meaningful commit messages
        - Highlight metrics (e.g., "Improved performance by 40%")
        - Include production links when applicable
        
        **Priority 4: Advanced Portfolio Items**
        - Link to live demos
        - Create portfolio website
        - Add blog posts about projects
        - Showcase open source contributions
        """)
    
    st.markdown("<br>", unsafe_allow_html=True)


def display_repos_section(analysis: Dict[str, Any]):
    """Display repository breakdown with modern design."""
    repos = analysis.get("repositories", {}).get("all_repos", [])
    
    st.markdown("<h2 class='section-header'>🏗️ Repository Portfolio</h2>", unsafe_allow_html=True)
    
    st.plotly_chart(create_repo_chart(repos), use_container_width=True, config={'displayModeBar': False})
    
    # Repository details table
    with st.expander("📦 View Repository Details", expanded=False):
        repo_df_data = []
        for repo in repos:
            repo_df_data.append({
                "Repository": repo.get("name"),
                "Description": truncate_text(repo.get("description", "No description"), 60),
                "Language": repo.get("language", "Unknown"),
                "⭐ Stars": repo.get("stargazers_count", 0),
                "🍴 Forks": repo.get("forks_count", 0),
                "Size": f"{repo.get('size', 0)} KB",
                "Updated": format_date(repo.get("pushed_at", "")),
            })
        
        st.dataframe(repo_df_data, use_container_width=True, hide_index=True)
    
    st.markdown("<br>", unsafe_allow_html=True)


def display_activity_section(analysis: Dict[str, Any]):
    """Display activity metrics with modern design."""
    activity = analysis.get("activity", {})
    commitment = activity.get("commitment", {})
    consistency = activity.get("consistency", {})
    
    st.markdown("<h2 class='section-header'>📈 Activity & Commitment</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Commits</div>
            <div class="metric-value">{format_large_number(commitment.get('total_commits', 0))}</div>
            <small>{commitment.get('activity_level', 'Unknown')}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Recent Activity (90d)</div>
            <div class="metric-value">{commitment.get('recent_commits_90d', 0)}</div>
            <small>Last commit {commitment.get('days_since_last_commit', 'N/A')} days ago</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Active Repositories</div>
            <div class="metric-value">{commitment.get('repositories_contributed', 0)}</div>
            <small>{consistency.get('consistency_rating', 'Unknown')}</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Consistency details
    with st.expander("📊 Commit Consistency Analysis", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            **Consistency Rating:** `{consistency.get('consistency_rating', 'Unknown')}`
            
            - Max Gap: {consistency.get('max_gap_days', 'N/A')} days
            - Avg Gap: {consistency.get('avg_gap_days', 'N/A')} days
            """)
        with col2:
            st.markdown(f"""
            **Engagement Profile**
            
            - Commitment Index: {consistency.get('commitment_index', 'N/A')}
            - Active Since: {consistency.get('total_days_active', 'N/A')} days
            """)
    
    st.markdown("<br>", unsafe_allow_html=True)


def display_impact_section(analysis: Dict[str, Any]):
    """Display impact metrics with modern design."""
    impact = analysis.get("impact", {})
    impact_analysis = impact.get("analysis", {})
    market = impact.get("market", {})
    
    st.markdown("<h2 class='section-header'>⚡ Project Impact & Market Position</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card score-excellent">
            <div class="metric-label">Impact Score</div>
            <div class="metric-value">{impact_analysis.get('total_impact_score', 'N/A')}/100</div>
            <small>{len(impact_analysis.get('high_impact_repos', []))} high-impact projects</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card score-good">
            <div class="metric-label">Tech Specialization</div>
            <div class="metric-value">{impact_analysis.get('top_language', 'Diverse')}</div>
            <small>{impact_analysis.get('deployment_count', 0)} deployed projects</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card score-fair">
            <div class="metric-label">Market Diversity</div>
            <div class="metric-value">{len(impact_analysis.get('business_relevant', []))}</div>
            <small>{market.get('market_diversity', 0)} different domains</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)


def display_resume_bullets(analysis: Dict[str, Any], bullet_points: list):
    """Display resume bullet points with modern design."""
    st.markdown("<h2 class='section-header'>📝 Professional Achievements</h2>", unsafe_allow_html=True)
    st.markdown("⭐ Use these bullet points in your resume, LinkedIn, or cover letter:")
    
    for bullet in bullet_points:
        st.markdown(f"""
        <div class="recommendation-box">
            <strong>↳ {bullet}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Copy option
    with st.expander("📋 Copy All Bullets"):
        bullets_text = "\n".join([f"• {b}" for b in bullet_points])
        st.text_area("Select and copy the text below:", bullets_text, height=150, disabled=True, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)


def display_export_section(analysis: Dict[str, Any]):
    """Display export options with modern design."""
    st.markdown("<h2 class='section-header'>💾 Export Your Analysis</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # JSON export
        json_data = json.dumps(analysis, indent=2, default=str)
        st.download_button(
            label="📥 Download Full Analysis (JSON)",
            data=json_data,
            file_name=f"github_analysis_{analysis.get('username', 'profile')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Markdown summary export
        summary_text = create_summary_text(analysis)
        st.download_button(
            label="📄 Download Summary (Markdown)",
            data=summary_text,
            file_name=f"github_summary_{analysis.get('username', 'profile')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    st.markdown("<br>", unsafe_allow_html=True)


def main():
    """Main application function."""
    # Display header
    display_header()
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        st.info("""
        **Setup Instructions:**
        
        1. GitHub is public - no token required
        2. For AI analysis: Set `OPENAI_API_KEY` environment variable
        3. Results are cached for 24 hours
        """)
        
        st.markdown("---")
        
        if st.button("🗑️ Clear Cache"):
            if "last_analysis" in st.session_state:
                del st.session_state["last_analysis"]
            st.success("Cache cleared!")
        
        st.markdown("---")
        st.markdown("""
        ### 📊 About This Tool
        
        This portfolio analyzer evaluates GitHub profiles like a technical recruiter would:
        
        - **5 Scoring Categories**: Documentation, Code Quality, Activity, Organization, Impact
        - **AI-Powered Analysis**: LLM + RAG for insights
        - **Actionable Feedback**: 7+ improvement suggestions
        - **Recruiting Insights**: Verdicts based on hiring criteria
        
        [GitHub](https://github.com/yourusername) | [Documentation](https://github.com/yourusername/github-portfolio-analyzer)
        """)
    
    # Main input section
    github_input, analyze_btn, clear_btn = display_input_section()
    
    if clear_btn:
        st.session_state.clear()
        st.rerun()
    
    # Handle analysis
    if analyze_btn:
        if not github_input or not validate_github_url(github_input):
            st.error("❌ Please enter a valid GitHub username or profile URL")
        else:
            display_loading_animation()
            
            try:
                analyzer = get_analyzer()
                analysis = analyzer.analyze_profile(github_input)
                
                if "error" in analysis:
                    error_msg = analysis['error']
                    
                    # Special handling for rate limit errors
                    if "rate limit" in error_msg.lower():
                        st.error(f"⏱️ {error_msg}")
                        st.warning(
                            "💡 **How to fix this:**\n\n"
                            "1. Create a GitHub Personal Access Token:\n"
                            "   - Go to github.com → Settings → Developer settings → Personal access tokens\n"
                            "   - Create a token with `public_repo` & `user` scopes\n"
                            "2. Add token to `.env` file: `GITHUB_TOKEN=your_token_here`\n"
                            "3. Restart the app\n\n"
                            "With a token, you get 5000 requests/hour instead of 60!"
                        )
                    else:
                        st.error(f"❌ Error: {error_msg}")
                else:
                    st.session_state.last_analysis = analysis
                    st.success("✅ Analysis complete!")
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
    
    # Display analysis results if available
    if "last_analysis" in st.session_state:
        analysis = st.session_state.last_analysis
        
        # Profile section
        display_profile_section(analysis)
        
        # Score section
        st.markdown("## 📊 Portfolio Score")
        display_score_section(analysis)
        
        # Strengths and flags
        st.markdown("## 🎯 Evaluation Summary")
        display_strengths_and_flags(analysis)
        
        # Improvements
        st.markdown("## 🚀 Growth Path")
        improvements = st.session_state.analyzer.generate_actionable_improvements(analysis)
        display_improvements(analysis, improvements)
        
        # Activity section
        st.markdown("## 📈 Activity Metrics")
        display_activity_section(analysis)
        
        # Impact section
        st.markdown("## 💼 Impact Analysis")
        display_impact_section(analysis)
        
        # Repository section
        st.markdown("## 🏗️ Project Portfolio")
        display_repos_section(analysis)
        
        # Resume bullets
        st.markdown("## 📝 Professional Summary")
        resume_bullets = st.session_state.analyzer.generate_resume_bullets(analysis)
        display_resume_bullets(analysis, resume_bullets)
        
        # Export section
        st.markdown("## 💾 Export Your Analysis")
        display_export_section(analysis)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 12px;">
        <p>GitHub Portfolio Analyzer & Enhancer | Built with Streamlit | Powered by OpenAI & LangChain</p>
        <p>Not affiliated with GitHub or Microsoft</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
