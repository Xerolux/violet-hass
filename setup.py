from setuptools import setup, find_packages
setup(
    name="violet-poolController-api",
    version="0.0.19",
    author="Basti (Xerolux)",
    author_email="git@xerolux.de",
    description="Asynchronous Python client for the Violet Pool Controller.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Xerolux/violet-poolController-api",
    packages=find_packages(),
    license="AGPL-3.0-or-later",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Home Automation",
    ],
    python_requires=">=3.12",
    install_requires=[
        "aiohttp>=3.11.0",
    ],
    extras_require={
        "test": [
            "aioresponses>=0.7.6",
            "pytest>=8.0",
            "pytest-asyncio>=0.23",
        ],
    },
    project_urls={
        "Bug Tracker": "https://github.com/Xerolux/violet-poolController-api/issues",
        "License": "https://www.gnu.org/licenses/agpl-3.0.html",
    },
)
