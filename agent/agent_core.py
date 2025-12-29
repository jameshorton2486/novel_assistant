"""
Agent Core - Main entry point for the Novel Assistant CLI.
"""

import logging
from typing import Dict
from agent.spec_loader import load_all_specs

logger = logging.getLogger(__name__)


def run() -> None:
    """Main entry point for the Novel Assistant CLI."""
    logger.info("Starting Novel Assistant CLI")
    print("\n=== NOVEL ASSISTANT — LOCAL CLI VERSION ===\n")

    specs: Dict[str, str] = load_all_specs()

    print("Loaded specifications:")
    for name in specs:
        print(f" - {name}: {len(specs[name])} characters")
        logger.debug(f"Loaded spec: {name} ({len(specs[name])} chars)")

    print("\nType a request for your Novel Assistant:")
    print("(Example: 'Write the opening paragraph of Chapter 1 in my style.')\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                logger.info("User requested exit")
                print("Exiting Novel Assistant.")
                break

            logger.info(f"User input: {user_input[:50]}...")
            print("\n--- ASSISTANT RESPONSE ---")
            print("Your assistant would respond here using the loaded specifications.")
            print("(Real AI integration will be added later.)\n")

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            print("\nExiting Novel Assistant.")
            break


if __name__ == "__main__":
    run()
