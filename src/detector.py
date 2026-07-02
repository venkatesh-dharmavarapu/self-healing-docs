import os
import re
from git import Repo
import chromadb
from indexer import CodeIndexer

class ChangeDetector:
    def __init__(self, repo_path="."):
        self.repo = Repo(repo_path)
        self.indexer = CodeIndexer()

    def get_staged_diff_functions(self):
        """Parses the local git diff to detect which files have uncommitted changes."""
        changed_files = set()
        
        # Check both unstaged changes and staged changes against HEAD
        diffs = self.repo.index.diff(None) + self.repo.index.diff("HEAD")
        
        for d in diffs:
            # We only care about Python source code updates
            if d.a_path and d.a_path.endswith('.py'):
                print(f"🎯 Detected uncommitted code modification in: {d.a_path}")
                changed_files.add(d.a_path)
                
        return list(changed_files)

    def identify_suspects(self, changed_files):
        """Queries ChromaDB to locate documentation blocks contextually linked to changed files."""
        suspects = []
        for file_path in changed_files:
            print(f"🔍 Querying ChromaDB for vectors linked to: {file_path}")
            
            # Contextual vector query using the file path string
            results = self.indexer.query_codebase(query_text=f"File path: {file_path}", n_results=3)
            
            for doc, match_id in zip(results['documents'][0], results['ids'][0]):
                suspects.append({"id": match_id, "content": doc})
        return suspects

if __name__ == "__main__":
    detector = ChangeDetector()
    
    print("--- 🚀 Running Git Change Detection Engine 🚀 ---")
    changed_items = detector.get_staged_diff_functions()
    
    if changed_items:
        print(f"Modified scopes detected: {changed_items}")
        impacted_docs = detector.identify_suspects(changed_items)
        
        print(f"\n🚨 ChromaDB flagged {len(impacted_docs)} documentation scopes for validation:")
        for idx, doc in enumerate(impacted_docs, 1):
            print(f"\n[{idx}] Suspect ID: {doc['id']}")
            print(f"    Context Sneak-Peek: {doc['content'][:120]}...")
    else:
        print("\n✅ Clean workspace: No uncommitted code changes detected.")