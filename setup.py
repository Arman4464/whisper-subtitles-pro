from setuptools import setup, find_packages

setup(
    name="whisper-subtitles-pro",
    version="1.0.0",
    description="Universal 100% Accurate Audio-to-Subtitles & Alignment Engine",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Arman4464",
    url="https://github.com/Arman4464/whisper-subtitles-pro",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "google-genai>=0.1.0",
        "requests>=2.28.0",
    ],
    extras_require={
        "local": [
            "faster-whisper>=1.0.0",
            "torch>=2.0.0",
        ],
        "all": [
            "faster-whisper>=1.0.0",
            "torch>=2.0.0",
            "rich>=13.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "whisper-subtitles-pro=whisper_subtitles.cli:main",
            "wsub=whisper_subtitles.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
)
