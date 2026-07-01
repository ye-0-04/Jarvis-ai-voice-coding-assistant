import os
import ollama
import chromadb
from chromadb.utils import embedding_functions
import time

# ===== CONFIGURATION =====
# CHANGE THIS to your project path!
PROJECT_PATH = r"D:\Document\GitHub\ML-framework-in-c"  # <<< EDIT THIS

# Where to store the index on D: drive
INDEX_PATH = "D:/Ollama/CodeIndex"

# File types to scan
EXTENSIONS = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', 
              '.go', '.rs', '.rb', '.php', '.cs', '.html', '.css', '.json', '.yaml',
              '.toml', '.ini', '.sh', '.bash', '.ps1', '.sql', '.vue', '.svelte'}

EMBEDDING_MODEL = "nomic-embed-text"
# =========================

print("="*70)
print("📚 JARVIS - Codebase Indexer")
print("="*70)
print(f"📂 Project: {PROJECT_PATH}")
print(f"💾 Index: {INDEX_PATH}")
print("="*70 + "\n")

# Check if project exists
if not os.path.exists(PROJECT_PATH):
    print(f"❌ ERROR: Project path not found: {PROJECT_PATH}")
    print("\nPlease update PROJECT_PATH in the script to your actual project folder.")
    exit(1)

# Initialize ChromaDB
print("🔧 Initializing database...")
chroma_client = chromadb.PersistentClient(path=INDEX_PATH)
collection = chroma_client.get_or_create_collection(
    name="my_codebase",
    embedding_function=embedding_functions.OllamaEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )
)

# Check if already indexed
if collection.count() > 0:
    print(f"⚠️ Index already has {collection.count()} chunks!")
    response = input("Delete and re-index? (y/n): ")
    if response.lower() != 'y':
        print("Keeping existing index. Exiting...")
        exit()
    else:
        chroma_client.delete_collection("my_codebase")
        collection = chroma_client.create_collection(
            name="my_codebase",
            embedding_function=embedding_functions.OllamaEmbeddingFunction(
                model_name=EMBEDDING_MODEL
            )
        )

def get_code_files(folder_path):
    """Scan project and extract code chunks"""
    code_blocks = []
    total_files = 0
    
    for root, dirs, files in os.walk(folder_path):
        # Skip common folders
        skip_dirs = ['node_modules', '__pycache__', '.git', 'venv', 'env', 
                     'dist', 'build', 'target', '.idea', '.vscode', 'bin',
                     'obj', 'out', 'coverage', '.pytest_cache', 'logs', 'tmp']
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in EXTENSIONS):
                total_files += 1
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Split into chunks (by function/class blocks)
                        chunks = content.split('\n\n')
                        
                        for i, chunk in enumerate(chunks):
                            chunk = chunk.strip()
                            if len(chunk) > 50:  # Ignore tiny fragments
                                code_blocks.append({
                                    'content': chunk,
                                    'file': file_path,
                                    'chunk_id': i
                                })
                        
                except:
                    pass
                
                # Progress indicator
                if total_files % 20 == 0:
                    print(f"   Scanned {total_files} files, found {len(code_blocks)} chunks...")
    
    return code_blocks, total_files

# Start scanning
print("🔍 Scanning your project...")
start_time = time.time()

code_blocks, total_files = get_code_files(PROJECT_PATH)

if not code_blocks:
    print(f"❌ No code found in: {PROJECT_PATH}")
    print(f"   Check that the path is correct and contains files with these extensions: {EXTENSIONS}")
    exit(1)

print(f"\n📊 Found {total_files} files, {len(code_blocks)} code chunks")
print(f"⏱️  Scan took {time.time() - start_time:.1f} seconds")

# Add to database in batches
print("\n💾 Indexing to D: drive...")
batch_size = 100
index_start = time.time()

for i in range(0, len(code_blocks), batch_size):
    batch = code_blocks[i:i+batch_size]
    ids = [f"{block['file']}_{block['chunk_id']}" for block in batch]
    documents = [block['content'] for block in batch]
    metadatas = [{'file': block['file']} for block in batch]
    
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    progress = min(i+batch_size, len(code_blocks))
    print(f"   Indexed {progress}/{len(code_blocks)} chunks ({progress/len(code_blocks)*100:.1f}%)")

print(f"\n✅ INDEXING COMPLETE!")
print(f"📊 {collection.count()} chunks indexed")
print(f"⏱️  Total time: {time.time() - index_start:.1f} seconds")
print(f"💾 Location: {INDEX_PATH}")

# Test query
print("\n🔍 Testing retrieval...")
test_query = "main function"
results = collection.query(query_texts=[test_query], n_results=2)
if results['documents'] and results['documents'][0]:
    print(f"✅ Found {len(results['documents'][0])} chunks for '{test_query}'")
    print(f"   First result from: {results['metadatas'][0][0]['file']}")
else:
    print("⚠️ No results found for test query. This is normal if your code doesn't have 'main'.")