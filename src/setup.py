from setuptools import setup, find_packages

setup(
    name="CheXprompt",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "openai==0.28.0",
        "aiolimiter==1.1.0",
    ],
    python_requires=">=3.10",
    author="JMZAM",
    author_email="jmz@stanford.edu",
    description="Expert radiology report evaluation using GPT.",
    url="https://github.com/microsoft/CheXprompt",
)
