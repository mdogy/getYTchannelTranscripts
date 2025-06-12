from setuptools import setup, find_packages
from os import path

# It's better practice to read the README file this way
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="youtube_transcripts",
    version="0.1.1",
    description="A tool to extract video metadata and transcripts from YouTube.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Michael Grossberg",
    author_email="mgrossberg@ccny.cuny.edu",
    url="https://www.ccny.cuny.edu/profiles/michael-grossberg",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "yt-dlp>=2023.12.30",
        "pandas>=2.1.0",
        "python-dotenv>=0.21.0",
        "google-generativeai>=0.3.0",
        "PyYAML>=6.0",
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
            "summarize-videos=youtube_transcripts.scripts.summarize_videos:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
# This setup script is designed to package the youtube_transcripts module
