# LLM Demos and Samples using Llama-Index

Demos and samples using [Llama-Index](https://docs.llamaindex.ai/en/stable/index.html).

## Contents

- [secAgentChat](./secAgentChat.py) A chat application using SEC Edgar filing documents
- [SecFilingReader](./SecFilingReader.py) A Llama-Index Data Reader using the SEC's Edgar API and document archive
- [SmartEdgarClient](./SmartEdgarClient.py) A light wrapper around the SEC Edgar API that adds caching and handles loading the actual filing documents
- [agent](./agent.ipynb) Simple example of a Llama-Index Agent
- [vectorStore](./vectorStore.ipynb) Sample example of building a Vector Store in Llama-Index

## Instructions

Copy [.env.sample](./.env.sample) to `.env` and set your OpenAI API key and email address (required for calling the SEC Edgar APIs).
