"""
Setup script para Signify
"""

from setuptools import setup, find_packages
from pathlib import Path

# Leer el README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else ""

# Leer requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="signbridge-ai",
    version="2.0.0",
    author="Signify Team",
    author_email="contact@signbridge.ai",
    description="Sistema Profesional de Consulta de Lengua de Señas Ecuatoriano",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/signbridge-ai/signbridge-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "signbridge=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.csv", "*.json", "*.md", "*.txt"],
    },
    keywords="sign language, ecuadorian signs, accessibility, speech synthesis, voice recognition, streamlit",
    project_urls={
        "Bug Reports": "https://github.com/signbridge-ai/signbridge-ai/issues",
        "Source": "https://github.com/signbridge-ai/signbridge-ai",
        "Documentation": "https://signbridge-ai.readthedocs.io/",
    },
)