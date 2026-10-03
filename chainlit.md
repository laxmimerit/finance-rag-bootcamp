# Production RAG for Finance

Ask questions about the 2024 annual filings for **Amazon** and **Alphabet**. The whole pipeline runs on your own machine: Ollama for the model and the embeddings, Qdrant for the vectors.

**What this app does**

- Picks its own metadata filters, so a question about one company does not pull pages from the other
- Answers only from the retrieved pages, and cites the file and the page every time
- Refuses when the sources do not hold the answer, instead of guessing

**Questions to start with**

- How much did Amazon spend on research and development in 2024?
- Compare AWS operating income with Google Cloud for 2024.
- Which companies and years does this collection hold?

Each step of the agent streams as it runs, so you can watch which tool it calls and what it retrieves.

Built for the KGP Talkie bootcamp. [YouTube](https://www.youtube.com/@KGPTalkie) · [kgptalkie.com](https://kgptalkie.com)
