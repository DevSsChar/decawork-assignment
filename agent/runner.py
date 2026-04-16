"""
CLI entry point for the IT Support Agent.

Usage:
    python -m agent.runner "Reset password for alice@company.com"
    python -m agent.runner "Create user john@company.com named John Doe in Engineering"
    python -m agent.runner "Check if dave@company.com exists, create if not, then assign Slack Pro"
"""

import asyncio
import sys
from agent.agent import ITSupportAgent

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m agent.runner '<natural language task>'")
        print("\nExamples:")
        print("  python -m agent.runner \"Reset password for alice@company.com\"")
        print("  python -m agent.runner \"Create new user john@company.com\"")
        sys.exit(1)

    task = " ".join(sys.argv[1:])
    print(f"\n[IT Support Agent] Executing task: {task}\n")
    print("=" * 60)

    agent = ITSupportAgent()
    result = asyncio.run(agent.execute(task))

    print("\n" + "=" * 60)
    print("[AGENT RESULT]")
    print(result["result"])

if __name__ == "__main__":
    main()