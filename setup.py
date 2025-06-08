from setuptools import setup, find_packages

setup(
    name="youtube_transcripts",
    version="0.1.0",
    description="A tool to extract video metadata and transcripts from YouTube.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Your Name",  # You can change this
    author_email="your.email@example.com",  # And this
    url="https://github.com/yourusername/getYTchannelTranscripts",  # And this
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "yt-dlp>=2023.12.30",
        "pandas>=2.1.0",
        # Add other core dependencies here from your requirements.txt
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
        ]
    },
    entry_points={
        "console_scripts": [
            "channel-videos-to-csv=youtube_transcripts.scripts.channel_videos_to_csv:main",
            "extract-video-transcript=youtube_transcripts.scripts.extract_video_transcript:main",
            "process-videos-from-csv=youtube_transcripts.scripts.process_videos_from_csv:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
