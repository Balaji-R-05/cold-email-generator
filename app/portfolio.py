import os
import pandas as pd
import chromadb
import uuid


class Portfolio:
    def __init__(self, file_name="my_portfolio.csv"):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        self.file_path = os.path.join(base_dir, file_name)
        self.vectorstore_path = os.path.join(base_dir, "vectorstore")

        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"❌ Portfolio file not found: {self.file_path}")

        self.data = pd.read_csv(self.file_path)

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
        metadata_groups = results.get("metadatas", [])
        
        relevant_links = []
        seen_links = set()
        for group in metadata_groups:
            for item in group:
                if isinstance(item, dict) and 'links' in item:
                    link = item['links']
                    if link not in seen_links:
                        relevant_links.append(link)
                        seen_links.add(link)
        return relevant_links
