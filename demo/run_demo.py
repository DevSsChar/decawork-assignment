"""
Demo runner — executes 3 IT tasks end-to-end for Loom recording.
Run AFTER starting the panel: uvicorn panel.main:app --port 8000
"""

import asyncio
import sys
import os

# Add the parent directory to sys.path so we can import 'agent'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.agent import ITSupportAgent

DEMO_TASKS = [
    # Task 1: Simple password reset (pre-existing user)
    "Reset the password for bob@company.com and tell me the new temporary password.",

    # Task 2: Create a new user then assign a license
    (
        "Create a new user with email diana@company.com, full name 'Diana Prince', "
        "department 'Security'. Then assign her the 'Microsoft 365' license."
    ),

    # Task 3: Conditional multi-step (check → create if missing → onboard)
    (
        "Check if eve@company.com exists in the system. "
        "If she does not exist, create her with full name 'Eve Torres' and department 'Legal'. "
        "Then reset her password and assign her 'Microsoft 365' and 'Slack Pro' licenses. "
        "Report the temporary password and confirm all steps completed."
    ),
]

async def run_demo():
    agent = ITSupportAgent()
    for i, task in enumerate(DEMO_TASKS, 1):
        print(f"\n{'='*70}")
        print(f"DEMO TASK {i}/{len(DEMO_TASKS)}")
        print(f"{'='*70}")
        print(f"Request: {task}\n")
        result = await agent.execute(task)
        print("\n[RESULT]")
        print(result["result"])
        print(f"\n✓ Task {i} complete. Waiting 3 seconds before next task...")
        await asyncio.sleep(3)

    print(f"\n{'='*70}")
    print("ALL DEMO TASKS COMPLETE")
    print(f"{'='*70}")

if __name__ == "__main__":
    asyncio.run(run_demo())