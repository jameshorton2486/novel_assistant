import os

def load_file(path):
    """Safely load any spec or prompt file."""
    if not os.path.exists(path):
        return f"[Missing file: {path}]"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_specs():
    """Loads all system spec documents into memory."""
    base = os.path.join(os.path.dirname(__file__), "..", "specs")

    specs = {
        "master_spec": load_file(os.path.join(base, "NOVEL_ASSISTANT_MASTER_SPEC.md")),
        "system_prompt": load_file(os.path.join(base, "SYSTEM_PROMPT.md")),
        "token_strategy": load_file(os.path.join(base, "TOKEN_STRATEGY.md")),
        "workflow": load_file(os.path.join(base, "WORKFLOW_PIPELINE.md")),
    }

    return specs

def run():
    """Main entry point for the Novel Assistant."""
    print("\n=== NOVEL ASSISTANT — LOCAL CLI VERSION ===\n")

    specs = load_specs()

    print("Loaded specifications:")
    for name in specs:
        print(f" - {name}: {len(specs[name])} characters")

    print("\nType a request for your Novel Assistant:")
    print("(Example: “Write the opening paragraph of Chapter 1 in my style.”)\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting Novel Assistant.")
                break

            print("\n--- ASSISTANT RESPONSE ---")
            print("Your assistant would respond here using the loaded specifications.")
            print("(Real AI integration will be added later.)\n")

        except KeyboardInterrupt:
            print("\nExiting Novel Assistant.")
            break

if __name__ == "__main__":
    run()
