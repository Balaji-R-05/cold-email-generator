import os
import pandas as pd
import chromadb
import uuid


class Portfolio:
    def __init__(self, file_name="my_portfolio.csv"):
        # Get absolute path to app directory (where this file lives)
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # CSV and vectorstore live alongside portfolio.py
        self.file_path = os.path.join(base_dir, file_name)
        self.vectorstore_path = os.path.join(base_dir, "vectorstore")

        # Ensure file exists
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"❌ Portfolio file not found: {self.file_path}")

        # Load data
        self.data = pd.read_csv(self.file_path)

        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=self.vectorstore_path)
        self.collection = self.chroma_client.get_or_create_collection(
            name="portfolio",
        )

    def load_portfolio(self):
        if not self.collection.count():
            for _, row in self.data.iterrows():
                self.collection.add(
                    documents=[row["Techstack"]],
                    metadatas=[{"links": row["Links"]}],
                    ids=[str(uuid.uuid4())]
                )

    def query_links(self, skills):
        results = self.collection.query(query_texts=skills, n_results=2)
        return results.get("metadatas", [])
