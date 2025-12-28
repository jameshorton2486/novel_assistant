"""
Agent Core - Main entry point for the Novel Assistant CLI.
"""

from agent.spec_loader import load_all_specs


def run():
    """Main entry point for the Novel Assistant CLI."""
    print("\n=== NOVEL ASSISTANT — LOCAL CLI VERSION ===\n")

    specs = load_all_specs()

    print("Loaded specifications:")
    for name in specs:
        print(f" - {name}: {len(specs[name])} characters")

    print("\nType a request for your Novel Assistant:")
    print("(Example: 'Write the opening paragraph of Chapter 1 in my style.')\n")

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
