from setuptools import setup, find_packages

setup(
    name="violet-pool-api",
    version="1.0.0",
    author="Basti (Xerolux)",
    description="Asynchronous Python client for the Violet Pool Controller.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Xerolux/violet_pool_api",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    install_requires=[
        "aiohttp>=3.9.0",
    ],
)
