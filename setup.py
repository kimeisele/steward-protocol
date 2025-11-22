from setuptools import setup, find_packages

setup(
    name="vibe-agency",
    version="0.1.0",
    description="The Vibe Agent Runtime - An OS for AI Agents",
    author="kimeisele",
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
        "dev": ["pytest", "black", "flake8"],
    },
    entry_points={
        "console_scripts": [
            "steward=steward.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
