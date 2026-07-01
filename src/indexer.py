import chromadb
import ollama
from parser import CodeParser

class CodeIndexer:
    def __init__(self, host="localhost", port=8000):
        # Point the client directly to the active Docker container
        self.chroma_client = chromadb.HttpClient(host=host, port=str(port))
        self.collection = self.chroma_client.get_or_create_collection(name="codebase_chunks")

    def get_ollama_embedding(self, text):
        """Generates a vector embedding using your local Ollama instance."""
        response = ollama.embeddings(model="nomic-embed-text", prompt=text)
        return response["embedding"]

    def index_codebase(self, root_dir):
        """Parses the codebase, embeds each chunk, and saves it to ChromaDB."""
        parser = CodeParser(root_dir=root_dir)
        chunks = parser.parse_all()
        
        print(f"Starting Dockerized ChromaDB indexing for {len(chunks)} code chunks...")

        for i, chunk in enumerate(chunks):
            text_to_embed = f"Type: {chunk['type']}\nName: {chunk['name']}\nDocstring: {chunk['docstring']}\nCode:\n{chunk['code']}"
            embedding = self.get_ollama_embedding(text_to_embed)
            
            self.collection.add(
                ids=[chunk["id"]],
                embeddings=[embedding],
                metadatas=[{
                    "type": chunk["type"],
                    "name": chunk["name"],
                    "file": chunk["file"]
                }],
                documents=[text_to_embed]
            )
            print(f"[{i+1}/{len(chunks)}] Indexed in Docker Chroma: {chunk['id']}")
            
        print("🎉 Codebase successfully indexed into Docker-hosted ChromaDB!")

    def query_codebase(self, query_text, n_results=1):
        """Queries the ChromaDB vector database using semantic text."""
        query_embedding = self.get_ollama_embedding(query_text)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results

if __name__ == "__main__":
    indexer = CodeIndexer()
    indexer.index_codebase(root_dir=".")
    
    print("\n--- Testing ChromaDB Semantic Search Query ---")
    search_query = "Find the method that creates vector embeddings using ollama models"
    search_results = indexer.query_codebase(search_query, n_results=1)
    
    for doc, match_id in zip(search_results['documents'][0], search_results['ids'][0]):
        print(f"\n[Chroma Match ID]: {match_id}")
        print(f"[Content Found]:\n{doc[:250]}...")