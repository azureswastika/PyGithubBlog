from pathlib import Path
from re import search

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("gitblog/__init__.py", encoding="utf-8") as f:
    version = search(r"__version__ = '(.*?)'", f.read()).group(1)

BASE_DIR = Path(__file__).parent
README = BASE_DIR.joinpath("README.md").read_text(encoding="utf-8")

setup(
    name="PyGithubBlog",
    version=version,
    description="PyGithubBlog",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/azureswastika/PyGithubBlog",
    download_url="https://github.com/azureswastika/PyGithubBlog/archive/{}.tar.gz".format(
        version
    ),
    author="azureswastika",
    license="MIT license",
    packages=["gitblog"],
    keywords=["PyGithubBlog", "Github", "Git", "Blog", "Github pages"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    entry_points={"console_scripts": ["gitblog = gitblog.__init__:main"]},
    install_requires=["bs4", "jinja2", "markdown"],
    python_requires=">=3.5",
)
