from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self.text_chunks = []

    def add_texts(self, chunks):
        embeddings = self.model.encode(chunks)
        self.index.add(np.array(embeddings).astype("float32"))
        self.text_chunks.extend(chunks)

    def search(self, query, k=5):
        query_vector = self.model.encode([query])
        distances, indices = self.index.search(
            np.array(query_vector).astype("float32"), k
        )
        return [self.text_chunks[i] for i in indices[0]]