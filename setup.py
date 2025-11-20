"""Setup configuration for Proactive Security Orchestrator."""

from pathlib import Path
from setuptools import setup, find_packages

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="proactive-security-orchestrator",
    version="1.0.5",
    description="Security orchestration platform integrating Semgrep and Gitleaks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Proactive Security Team",
    author_email="",
    url="",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={"proactive_security_orchestrator": ["contracts/*.json"]},
    python_requires=">=3.11",
    install_requires=[
        "typer>=0.9.0",
        "rich==13.5.2",
        "pydantic>=2.0.0",
        "jsonschema>=4.0.0",
        "structlog>=23.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "security-scan=proactive_security_orchestrator.cli:app",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)

