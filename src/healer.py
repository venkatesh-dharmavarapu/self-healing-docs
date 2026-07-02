import ollama
from detector import ChangeDetector

class DocHealer:
    def __init__(self):
        self.detector = ChangeDetector()

    def check_and_heal(self):
        print("--- 🩺 Starting Self-Healing Documentation Engine 🩺 ---")
        
        # 1. Fetch modified files
        changed_files = self.detector.get_staged_diff_functions()
        if not changed_files:
            print("✅ Codebase is clean. No documentation healing needed.")
            return

        # 2. Extract at-risk code chunks from ChromaDB
        suspects = self.detector.identify_suspects(changed_files)
        
        for suspect in suspects:
            print(f"\nEvaluating stability for scope: {suspect['id']}...")
            
            # 3. Formulate an engineering prompt for your local LLM
            prompt = f"""
            You are an expert AI software engineer. Review the following Python component data retrieved from a vector database:
            
            {suspect['content']}
            
            Task:
            Check if the current 'Docstring' accurately reflects what the implementation in 'Code' is doing.
            - If the docstring is missing or outdated based on the code snippet, generate a beautifully descriptive, updated docstring.
            - Respond ONLY with the updated docstring wrapped in triple quotes, or say 'VALID' if it requires no changes.
            """
            
            # 4. Use a local smart model (like llama3 or mistral) to run the audit
            # Change model="llama3" to match whatever model you currently have installed in Ollama
            response = ollama.generate(model="llama3", prompt=prompt)
            verdict = response['response'].strip()
            
            print(f"🤖 LLM Analysis Verdict for [{suspect['id']}]:")
            print(f"{verdict}\n" + "-"*50)

if __name__ == "__main__":
    healer = DocHealer()
    healer.check_and_heal()