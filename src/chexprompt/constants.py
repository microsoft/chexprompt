import os

OPENAI_API_TYPE="azure"
OPENAI_API_VERSION=os.getenv("OPENAI_API_VERSION")  # e.g. 2023-07-01-preview
OPENAI_API_BASE=os.getenv("OPENAI_API_BASE")  # i.e. https://{your-resource-name}.openai.azure.com/
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")