from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="steward-protocol",
    version="0.2.0",
    description="Cryptographic Identity + Governance for AI Agents. A.G.I. Infrastructure.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="kimeisele",
    author_email="contact@steward-protocol.io",
    url="https://github.com/kimeisele/steward-protocol",
    project_urls={
        "Documentation": "https://github.com/kimeisele/steward-protocol#readme",
        "Source": "https://github.com/kimeisele/steward-protocol",
        "Tracker": "https://github.com/kimeisele/steward-protocol/issues",
        "Leaderboard": "https://steward-protocol.io/leaderboard",
    },
    license="MIT",
    packages=find_packages(where="."),
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "ecdsa>=0.18.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": ["pytest", "black", "flake8", "pytest-cov"],
        "github": ["PyGithub>=2.0.0"],
    },
    entry_points={
        "console_scripts": [
            "steward=steward.cli:main",
        ],
    },
    keywords=[
        "ai",
        "agents",
        "governance",
        "cryptography",
        "identity",
        "autonomous",
        "protocol",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
)
