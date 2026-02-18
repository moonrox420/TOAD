#!/usr/bin/env python3
"""
Setup configuration for EnterpriseAI-Local Code Generation Agent

LEGITIMATE REPOSITORY: https://github.com/moonrox420/TOAD
Owner: moonrox420 (Dustin Hill / DroxAI)

Install with:
    pip install -e .

Then use from anywhere:
    enterpriseai generate "Create a REST API"
    enterpriseai analyze "requirement"
    enterpriseai interactive
    enterpriseai benchmark
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="enterpriseai-local",
    version="1.0.0",
    description="EnterpriseAI-Local Code Generation Agent - Local AI-Powered Code Generation by Dustin Hill / DroxAI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dustin Hill (moonrox420)",
    author_email="dustin@droxai.com",
    url="https://github.com/moonrox420/TOAD",
    license="See LICENSE.md",
    
    # Package discovery
    packages=find_packages(),
    py_modules=["agent", "cli", "web_ui"],
    
    # Console scripts - makes commands available globally
    entry_points={
        'console_scripts': [
            'enterpriseai=cli:main',
            'enterpriseai-web=web_ui:main',
            'enterpriseai-tui=tui:main',
        ],
    },
    
    # Dependencies
    install_requires=[
        "aiosqlite>=0.17.0",
    ],
    
    # Optional dependencies for enhanced features
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "black>=23.0.0",
            "flake8>=5.0.0",
        ],
        "llm": [
            "openai>=0.27.0",
            "anthropic>=0.3.0",
        ],
        "ml": [
            "scikit-learn>=1.2.0",
            "numpy>=1.24.0",
            "pandas>=1.5.0",
        ],
    },
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Metadata
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    
    keywords="code generation ai agent development productivity enterpriseai-local",
    project_urls={
        "Source": "https://github.com/moonrox420/TOAD",
        "Issues": "https://github.com/moonrox420/TOAD/issues",
    },
)
