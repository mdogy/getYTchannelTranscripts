from setuptools import setup, find_packages

setup(
    name="youtube-transcripts",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"youtube_transcripts": ["py.typed"]},
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
    description="A tool to extract YouTube channel video metadata and transcripts",
    entry_points={
        "console_scripts": [
            "channel-videos-to-csv=youtube_transcripts.scripts.channel_videos_to_csv:main",
            "extract-video-transcript=youtube_transcripts.scripts.extract_video_transcript:main",
        ],
    },
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
