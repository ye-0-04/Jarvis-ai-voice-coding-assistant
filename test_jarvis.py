from jarvis import Jarvis

print("🔧 Testing Jarvis setup...\n")

# Create Jarvis instance
j = Jarvis()

# Test questions
questions = [
    "What does this codebase do?",
    "Find the main entry point",
    "What functions are defined?"
]

for q in questions:
    print(f"\n{'='*50}")
    print(f"❓ {q}")
    print('='*50)
    j.process_question(q)
    input("\nPress Enter for next question...")