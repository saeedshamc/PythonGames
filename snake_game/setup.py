from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'Readme.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name="snake-game",
    version="2.0.0",
    author="Saeed Shamsi",
    author_email="saeedshams2024@gmail.com",
    description="A feature-rich Snake game with multiple game modes, power-ups, and statistics",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/saeedshamc/PythonGames",
    py_modules=["snake_game"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment :: Arcade Games",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pygame-ce>=2.5.0",
    ],
    entry_points={
        "console_scripts": [
            "snake-game=snake_game:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
