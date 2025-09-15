"""
Browser Tool that integrates AgentCore Browser and Browser Use
"""
import os
import logging
import contextlib
from typing import Optional
from bedrock_agentcore.tools.browser_client import BrowserClient
from browser_use import Agent as BrowserUseAgent
from browser_use.browser.session import BrowserSession
from browser_use.browser import BrowserProfile
from langchain_aws import ChatBedrockConverse

# Set up logging
logger = logging.getLogger(__name__)


async def execute_browser_task(
    instruction: str,
    starting_url: str = "https://docs.aws.amazon.com",
    region: str = None
) -> str:
    """
    Execute a browser automation task using AgentCore Browser and Browser Use.

    Args:
        instruction: Natural language instruction for the browser task
        starting_url: Initial URL to navigate to
        region: AWS region for AgentCore Browser (defaults to AGENTCORE_BROWSER_REGION env var)

    Returns:
        Result of the browser task execution
    """
    region = region or os.getenv('AGENTCORE_BROWSER_REGION', 'us-west-2')

    logger.info(f"Starting browser task: {instruction[:100]}...")
    logger.info(f"Initial URL: {starting_url}")

    client = BrowserClient(region=region)
    browser_session = None

    try:
        # Start AgentCore Browser session
        client.start()
        ws_url, headers = client.generate_ws_headers()

        logger.info(f"Browser session created in region {region}")
        logger.debug(f"CDP WebSocket URL: {ws_url[:100]}...")

        # Create browser profile with headers (CRITICAL: headers go in BrowserProfile, not BrowserSession)
        browser_profile = BrowserProfile(
            headers=headers,
            timeout=180000,  # 3 minutes timeout
        )

        # Create Browser Use session (CRITICAL: Do NOT pass headers parameter here)
        browser_session = BrowserSession(
            cdp_url=ws_url,
            browser_profile=browser_profile,
            keep_alive=True  # Keep browser alive for multiple operations
        )

        logger.info("Starting Browser Use session...")
        await browser_session.start()
        logger.info("Browser Use session started successfully")

        # Initialize Bedrock LLM for Browser Use
        bedrock_chat = ChatBedrockConverse(
            model_id=os.getenv('BEDROCK_MODEL_ID',
                               'us.anthropic.claude-sonnet-4-20250514-v1:0'),
            region_name=region
        )

        # Create Browser Use agent with the task
        task = f"""
        Navigate to {starting_url} and then perform the following task:
        {instruction}

        Please provide a clear and concise summary of the results.
        """

        browser_use_agent = BrowserUseAgent(
            task=task,
            llm=bedrock_chat,
            browser_session=browser_session,
        )

        logger.info("Executing Browser Use task...")
        result = await browser_use_agent.run()

        logger.info("Task completed successfully")
        return result

    except Exception as e:
        logger.error(f"Error executing browser task: {str(e)}", exc_info=True)
        return f"Error executing browser task: {str(e)}"

    finally:
        # Clean up browser session
        if browser_session:
            with contextlib.suppress(Exception):
                await browser_session.close()
                logger.info("Browser session closed")

        # Stop AgentCore Browser client
        with contextlib.suppress(Exception):
            client.stop()
            logger.info("Browser client stopped")


async def browse_url(url: str, instruction: str = "Extract the main content", region: str = None) -> str:
    """
    Browse a specific URL and perform an action.

    Args:
        url: The URL to browse
        instruction: What to do on the page
        region: AWS region for AgentCore Browser

    Returns:
        Result of the browsing action
    """
    return await execute_browser_task(
        instruction=instruction,
        starting_url=url,
        region=region
    )
