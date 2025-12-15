#!/usr/bin/env python3
"""
Setup configuration for DroxAI Code Generation Agent

Install with:
    pip install -e .

Then use from anywhere:
    droxai generate "Create a REST API"
    droxai analyze "requirement"
    droxai interactive
    droxai benchmark
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="droxai-codegen",
    version="1.0.0",
    description="DroxAI Code Generation Agent - AI-Powered Code Generation with 92.83/100 Performance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dustin Hill",
    author_email="dustin@droxai.com",
    url="https://github.com/moonrox420/TOAD",
    license="Proprietary",
    
    # Package discovery
    packages=find_packages(),
    py_modules=["agent", "cli", "web_ui"],
    
    # Console scripts - makes commands available globally
    entry_points={
        "console_scripts": [
            "droxai=cli:main",
            "droxai-web=web_ui:main",
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
    
    keywords="code generation ai agent development productivity",
    project_urls={
        "Bug Reports": "https://github.com/moonrox420/TOAD/issues",
        "Documentation": "https://github.com/moonrox420/TOAD#readme",
        "Source Code": "https://github.com/moonrox420/TOAD",
    },
)
