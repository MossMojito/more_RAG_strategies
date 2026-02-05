import chromadb
from chromadb.utils import embedding_functions
from ..config import VECTOR_DB_DIR
from .cleaner import flatten_metadata

class VectorStore:
    def __init__(self, persist_directory=VECTOR_DB_DIR):
        self.persist_directory = str(persist_directory)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="intfloat/multilingual-e5-base"
        )
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="all_sports",
            embedding_function=self.embedding_fn
        )

    def add_chunks(self, chunks):
        """
        Add chunks to the vector DB.
        chunks: List of specific chunk objects (dict with chunk_id, content, metadata)
        """
        if not chunks:
            return

        documents = [c['content'] for c in chunks]
        metadatas = [flatten_metadata(c['metadata']) for c in chunks]
        ids = [c['chunk_id'] for c in chunks]

        # Batch add
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            self.collection.add(
                documents=documents[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
                ids=ids[i:i+batch_size]
            )
            print(f"   📦 Indexed {len(documents[i:i+batch_size])} items")
            
    def get_collection(self):
        return self.collection

    def count(self):
        return self.collection.count()
    
    def reset(self):
        try:
            self.client.delete_collection("all_sports")
        except:
            pass
        self.collection = self.client.create_collection(
            name="all_sports",
            embedding_function=self.embedding_fn
        )
