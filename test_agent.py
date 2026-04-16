import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig
import os, asyncio
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

async def test_agent():
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.0
    )
    browser = Browser(config=BrowserConfig(headless=True))
    agent = Agent(task="Go to example.com", llm=llm, browser=browser)
    try:
        history = await agent.run(max_steps=2)
        print("Final history:", history)
        for step in history.history:
            print("Step result:", step.result)
            for m in step.state.interacted_element:
                print(m)
    except Exception as e:
        print("AGENT EXCEPTION:", e)
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_agent())
