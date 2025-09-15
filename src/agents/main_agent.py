"""
AWS Documentation Search Agent using Strands Agents v1.8.0
"""
import os
import logging
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models import BedrockModel
from src.tools.browser_tool import browse_url

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# System prompt for the agent
SYSTEM_PROMPT = """You are an AWS Documentation Expert Assistant.

Your task is to help users with AWS-related questions by browsing official AWS documentation.

Use the browse_url tool to:
- Navigate to AWS documentation pages (start with https://docs.aws.amazon.com if needed)
- Search for specific information
- Extract relevant content, code examples, and best practices

Always provide accurate, comprehensive answers based on the official AWS documentation.
"""


@tool
async def browse_url_tool(url: str, instruction: str = "Extract the main content") -> str:
    """
    Browse any URL with specific instructions.

    Args:
        url: The URL to browse
        instruction: Natural language instruction for what to do on the page

    Returns:
        Result of the browsing action
    """
    logger.info(f"Browsing URL: {url}")
    return await browse_url(url, instruction)


def create_agent():
    """
    Create and configure the AWS Docs Agent.

    Returns:
        Configured Strands Agent instance
    """
    # Initialize Bedrock model
    model = BedrockModel(
        model_id=os.getenv('BEDROCK_MODEL_ID',
                           'us.anthropic.claude-sonnet-4-20250514-v1:0'),
        params={
            "max_tokens": 2048,
            "temperature": 0.3,
            "top_p": 0.8
        },
        region=os.getenv('AWS_REGION', 'us-west-2'),
        read_timeout=600,
    )

    # Create Strands Agent with browser tools
    agent = Agent(
        name="aws_docs_agent",
        model=model,
        tools=[browse_url_tool],
        system_prompt=SYSTEM_PROMPT
    )

    return agent


def process_query(query: str) -> str:
    """
    Process a user query synchronously.

    Args:
        query: User's question about AWS services or configurations

    Returns:
        Answer based on AWS documentation
    """
    try:
        agent = create_agent()
        # Use synchronous invocation
        result = agent(query)
        return str(result)
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return f"Error processing query: {str(e)}"


# For testing purposes
if __name__ == "__main__":
    import asyncio

    async def test_agent():
        """Test the agent with sample queries."""
        test_queries = [
            "How do I create an S3 bucket lifecycle policy?",
            "What are the best practices for Lambda cold start optimization?",
        ]

        agent = create_agent()

        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            try:
                # Use async invocation for testing
                result = await agent.invoke_async(query)
                print(f"📋 Answer: {result}")
            except Exception as e:
                print(f"❌ Error: {e}")

    asyncio.run(test_agent())
