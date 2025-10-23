"""
Email Connector - IMAP邮件提取和CSV导出工具
"""
from setuptools import setup, find_packages
import os

# 读取README文件
def read_long_description():
    """读取README.md作为长描述"""
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as fh:
            return fh.read()
    return "IMAP Email Extractor and CSV Export Tool"

setup(
    name="email-connector",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="专业级IMAP邮件提取和CSV导出工具",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/email-connector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Email",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="email imap csv export parser connector",
    python_requires=">=3.8",
    install_requires=[
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "enhanced": [
            "tqdm>=4.66.0",
            "colorama>=0.4.6",
            "rich>=13.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "email-connector=src.main:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/email-connector/issues",
        "Source": "https://github.com/yourusername/email-connector",
        "Documentation": "https://github.com/yourusername/email-connector/blob/main/README.md",
    },
)