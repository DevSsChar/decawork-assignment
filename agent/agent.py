"""
Core IT Support Agent.

Usage:
    from agent.agent import ITSupportAgent
    import asyncio

    agent = ITSupportAgent()
    result = asyncio.run(agent.execute("Reset password for alice@company.com"))
    print(result)
"""

import os
import asyncio
from dotenv import load_dotenv, find_dotenv
from browser_use import Agent, Browser, BrowserConfig
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(find_dotenv())

PANEL_URL = os.getenv("PANEL_BASE_URL", "http://localhost:8000")
HEADLESS = os.getenv("AGENT_HEADLESS", "false").lower() == "true"
MAX_STEPS = int(os.getenv("AGENT_MAX_STEPS", "25"))

SYSTEM_CONTEXT = f"""
You are an IT support agent operating a corporate IT admin panel at {PANEL_URL}.

CRITICAL RULES:
1. You interact ONLY through the browser — click buttons, fill forms, navigate links. 
2. Never attempt direct HTTP calls or API shortcuts.
3. Always start at {PANEL_URL} (the dashboard).
4. Before performing an action on a user, navigate to the Users page first to verify the user exists.
5. If a user does not exist and the task requires them to exist, create them first.
6. Always wait for page load confirmation before reading results.
7. After completing a task, report exactly what you did, what the outcome was, and any temp passwords generated.
8. If an action fails (e.g., user not found), report the failure clearly.

NAVIGATION GUIDE:
- Dashboard: {PANEL_URL}/
- All Users: {PANEL_URL}/users  
- Password Reset: {PANEL_URL}/reset-password
- License Management: {PANEL_URL}/licenses
- User Detail: {PANEL_URL}/users/{{email}}

TASK COMPLETION FORMAT:
When done, output a summary in this format:
TASK: <original request>
STATUS: SUCCESS | PARTIAL | FAILED
ACTIONS_TAKEN: <bullet list of each step>
RESULT: <what actually happened, including any generated passwords>
"""

class ITSupportAgent:
    def __init__(self):
        if not os.getenv("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY not set in .env")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview", 
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.0,
            max_retries=2,
        )

    async def execute(self, task: str) -> dict:
        browser = Browser(
            config=BrowserConfig(
                headless=HEADLESS,
            )
        )
        
        full_task = f"{SYSTEM_CONTEXT}\n\nYOUR TASK: {task}"
        
        agent = Agent(
            task=full_task,
            llm=self.llm,
            browser=browser,
        )
        
        history = await agent.run(max_steps=MAX_STEPS)
        await browser.close()
        
        return {
            "task": task,
            "result": history.final_result(),
            "success": history.is_successful(),
        }

if __name__ == "__main__":
    # Test execution when running the file directly
    async def run_all():
        agent = ITSupportAgent()
        
        # Task 1
        print("\n--- Running Task 1: Reset Password ---")
        t1 = await agent.execute("Reset password for alice@company.com")
        print("Result 1:", t1["result"])
        await asyncio.sleep(2)
        
        # Task 2
        print("\n--- Running Task 2: Create User & Assign License ---")
        t2 = await agent.execute("Create a new user diana@company.com named 'Diana Prince' in 'Security'. Then assign her the 'Microsoft 365' license.")
        print("Result 2:", t2["result"])
        await asyncio.sleep(2)
        
        # Task 3
        print("\n--- Running Task 3: Conditional Multi-step Onboarding ---")
        t3 = await agent.execute("Check if eve@company.com exists. If not, create her (Eve Torres in Legal). Then reset her password and assign her 'Slack Pro'.")
        print("Result 3:", t3["result"])
        
        print("\nAll 3 tasks completed successfully. Shutting down.")
        import sys
        sys.exit(0)

    asyncio.run(run_all())
