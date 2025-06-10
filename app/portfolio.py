import pandas as pd
import chromadb
import uuid


class Portfolio:
    def __init__(self, file_path="my_portfolio.csv"):
        self.file_path = file_path
        self.data = pd.read_csv(file_path)

        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path="vectorstore")
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
                # print(f"✅ Added: {row['Techstack']}")

    def query_links(self, skills):
        results = self.collection.query(query_texts=skills, n_results=2)
        return results.get("metadatas", [])
        