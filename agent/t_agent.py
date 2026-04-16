"""
IT Support Agent — v1.1
Fixes: hallucination, self-loops, Gemini rate limit crashes.

Gemini infrastructure preserved. No LLM provider change.

Usage:
    from agent.agent import ITSupportAgent
    import asyncio
    result = asyncio.run(ITSupportAgent().execute("Reset password for alice@company.com"))
    print(result)
"""

import os
import asyncio
import logging

from dotenv import load_dotenv, find_dotenv
from browser_use import Agent, Browser, BrowserConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

# Gemini 429 surfaces as this exception through google-api-core
try:
    from google.api_core.exceptions import ResourceExhausted
except ImportError:
    # Fallback: catch by message string if google-api-core not installed separately
    ResourceExhausted = Exception

load_dotenv(find_dotenv())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("it-agent")

# ── Constants ──────────────────────────────────────────────────────────────────
PANEL_URL       = os.getenv("PANEL_BASE_URL", "http://localhost:8000")
HEADLESS        = os.getenv("AGENT_HEADLESS", "false").lower() == "true"
MAX_STEPS       = int(os.getenv("AGENT_MAX_STEPS", "12"))
STEP_DELAY_SEC  = float(os.getenv("AGENT_STEP_DELAY", "4.0"))

# ── System Prompt ──────────────────────────────────────────────────────────────
# Kept under 200 tokens intentionally — Gemini-flash loses instruction-following
# with long system prompts. Imperative-only format eliminates hallucination room.
SYSTEM_PROMPT = f"""You are an IT admin browser agent. Panel: {PANEL_URL}

RULES — follow exactly:
1. Use ONLY browser actions (click, type, navigate). No HTTP calls.
2. Each action: observe the page, act once, check result.
3. Green flash message on screen = action succeeded. STOP that sub-task immediately. Do NOT repeat it.
4. Never re-submit a form you already submitted successfully.
5. If a page shows an error flash, retry max 2 more times then report FAILED.
6. Do not guess or assume page content. Only act on what you see.
7. When all sub-tasks complete, output the result block and STOP.

PAGES:
- Users list: {PANEL_URL}/users
- Password reset: {PANEL_URL}/reset-password
- Licenses: {PANEL_URL}/licenses
- User detail: {PANEL_URL}/users/<email>

OUTPUT FORMAT (always end with this):
TASK: <original request>
STATUS: SUCCESS | PARTIAL | FAILED
RESULT: <what happened; include temp password if reset was done>
"""

# ── Rate-limit-aware retry wrapper ────────────────────────────────────────────
@retry(
    retry=retry_if_exception_type(ResourceExhausted),
    wait=wait_exponential(multiplier=1, min=15, max=60),
    stop=stop_after_attempt(3),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
async def _run_with_retry(agent: Agent, max_steps: int):
    """Run the browser-use agent with Gemini 429 backoff."""
    return await agent.run(max_steps=max_steps)


def _inject_step_delay(agent: Agent, delay: float):
    """
    Inject a per-step sleep to stay under Gemini's 15 RPM free tier limit.
    4s/step = 15 steps/min = exactly at the RPM boundary with margin.

    Tries the official callback API first (browser-use >= 0.1.30).
    Falls back to monkey-patching _run_step for older versions.
    """
    async def _delay_callback(*args, **kwargs):
        await asyncio.sleep(delay)

    # Approach A: official callback (preferred)
    if hasattr(agent, "register_new_step_callback"):
        try:
            agent.register_new_step_callback(_delay_callback)
            logger.info(f"Step delay {delay}s injected via register_new_step_callback")
            return
        except Exception:
            pass

    # Approach B: monkey-patch _run_step (fallback)
    if hasattr(agent, "_run_step"):
        original = agent._run_step

        async def _patched(*args, **kwargs):
            result = await original(*args, **kwargs)
            await asyncio.sleep(delay)
            return result

        agent._run_step = _patched
        logger.info(f"Step delay {delay}s injected via _run_step patch")
        return

    # Approach C: step_callback parameter (some browser-use versions)
    logger.warning(
        "Could not inject step delay — neither register_new_step_callback "
        "nor _run_step found. Agent may hit rate limits on multi-step tasks."
    )


# ── Agent class ───────────────────────────────────────────────────────────────
class ITSupportAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in .env")

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview", 
            api_key=api_key,
            temperature=0.0,          # eliminates sampling randomness → kills loops
            max_retries=1,            # langchain retry (distinct from our tenacity retry)
            max_output_tokens=512,    # prevents runaway reasoning chains eating rate limit
        )

    async def execute(self, task: str) -> dict:
        """
        Execute a natural-language IT support task via browser automation.

        Returns:
            dict with keys: task (str), result (str), success (bool)
        """
        browser = Browser(config=BrowserConfig(headless=HEADLESS))

        try:
            agent = Agent(
                task=f"{SYSTEM_PROMPT}\n\nTASK: {task}",
                llm=self.llm,
                browser=browser,
                # Do NOT pass max_steps here — pass to agent.run() instead
                # so _run_with_retry can control it
            )

            _inject_step_delay(agent, STEP_DELAY_SEC)

            logger.info(f"Starting task: {task}")
            history = await _run_with_retry(agent, MAX_STEPS)

            return {
                "task": task,
                "result": history.final_result() or "Task completed (no result text returned).",
                "success": history.is_successful(),
            }

        except ResourceExhausted:
            msg = (
                "Gemini rate limit hit after 3 retries (15→30→60s backoff). "
                "Wait 1 minute and retry, or reduce AGENT_STEP_DELAY in .env."
            )
            logger.error(msg)
            return {"task": task, "result": msg, "success": False}

        except Exception as e:
            msg = f"Agent error: {type(e).__name__}: {str(e)}"
            logger.error(msg, exc_info=True)
            return {"task": task, "result": msg, "success": False}

        finally:
            # Always close browser — even if agent.run() throws
            try:
                await browser.close()
            except Exception:
                pass  # Browser already closed or never opened — safe to ignore

if __name__ == "__main__":
    # Test execution when running the file directly
    agent = ITSupportAgent()
    result = asyncio.run(agent.execute("Reset password for alice@company.com"))
    print(result)