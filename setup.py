#!/usr/bin/env python
"""
Setup script for GitHub Portfolio Analyzer

Usage:
    python setup.py install
    OR
    pip install -e .
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="github-portfolio-analyzer",
    version="1.0.0",
    author="AI Engineer Team",
    author_email="team@example.com",
    description="Recruiting-grade GitHub portfolio analysis powered by AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/github-portfolio-analyzer",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "github-analyzer=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "data": ["recruiter_knowledge.txt"],
    },
)
