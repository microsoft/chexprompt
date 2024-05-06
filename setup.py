from setuptools import setup, find_packages

setup(
    name="chexprompt",
    version="0.1",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=[
        "openai==0.28.0",
        "aiolimiter==1.1.0",
    ],
    python_requires=">=3.9",
    author="JMZAM",
    author_email="jmz@stanford.edu",
    description="Expert radiology report evaluation using GPT.",
    url="https://github.com/microsoft/CheXprompt",
)
