"""
AWS Documentation Search Agent using Strands Agents v1.8.0
"""
import os
import logging
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models import BedrockModel
from src.tools.browser_tool import search_aws_docs, browse_url

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# System prompt for the agent
SYSTEM_PROMPT = """You are an AWS documentation expert assistant. Your role is to help users find information 
from AWS documentation using web browsing capabilities.

When users ask questions about AWS services, configurations, or best practices:
1. Use the search_aws_docs tool to search AWS documentation
2. Use the browse_url tool to access specific URLs if needed
3. Provide clear, accurate answers based on the official documentation
4. Include links to relevant documentation when possible

Always prioritize official AWS documentation as your source of truth.
"""


@tool
async def search_aws_docs_tool(query: str) -> str:
    """
    Search AWS documentation using natural language query.

    Args:
        query: The search query for AWS documentation

    Returns:
        Extracted content from AWS documentation
    """
    logger.info(f"Searching AWS docs for: {query}")
    return await search_aws_docs(query)


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
        model_id=os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-sonnet-4-20250514-v1:0'),
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
        tools=[search_aws_docs_tool, browse_url_tool],
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