from setuptools import setup, find_packages

setup(
    name="youtube-channel-metadata",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "yt-dlp>=2023.12.30",
        "pandas>=2.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-mock>=3.12.0",
            "pytest-cov>=4.1.0",
            "flake8>=7.0.0",
            "black>=24.1.0",
            "mypy>=1.8.0",
            "types-python-dateutil>=2.8.19.14",
            "types-requests>=2.31.0.20240106",
        ],
    },
    python_requires=">=3.8",
    author="Michael",
    description="A tool to extract YouTube channel video metadata",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
