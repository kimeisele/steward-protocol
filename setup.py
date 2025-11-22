from setuptools import setup, find_packages

setup(
    name="steward-protocol",
    version="0.1.0",
    description="The STEWARD Protocol - Sovereign Agent Identity & Trust Standard",
    author="kimeisele",
    license="MIT",
    packages=find_packages(where="."),
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "cryptography>=41.0.0",
        "rich>=10.0.0",
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
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
