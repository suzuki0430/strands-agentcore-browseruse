"""
AWS Documentation Search Agent using Strands Agents v1.8.0
"""
import os
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv
from strands import Agent
from strands.integrations.bedrock import BedrockChatModel
from src.tools.browser_tool import AgentCoreBrowserTool

# Load environment variables
load_dotenv()


class AWSDocsAgent:
    """
    An agent that can search AWS documentation and answer questions
    using AgentCore Browser and Browser Use.
    """

    def __init__(self):
        self.browser_tool = AgentCoreBrowserTool()

        # Initialize Bedrock model
        self.model = BedrockChatModel(
            model_id=os.getenv('BEDROCK_MODEL_ID',
                               'anthropic.claude-sonnet-4-20250514-v1:0'),
            region=os.getenv('AWS_REGION', 'us-west-2')
        )

        # Create Strands Agent with browser tool
        self.agent = Agent(
            name="aws_docs_agent",
            model=self.model,
            tools=[self.create_browser_tool()],
            instructions="""
            You are an AWS documentation expert assistant. Your role is to help users find information 
            from AWS documentation using web browsing capabilities.
            
            When users ask questions about AWS services, configurations, or best practices:
            1. Use the browser tool to search AWS documentation
            2. Extract relevant information from the search results
            3. Provide clear, accurate answers based on the official documentation
            4. Include links to relevant documentation when possible
            
            Always prioritize official AWS documentation as your source of truth.
            """
        )

    def create_browser_tool(self) -> Dict[str, Any]:
        """
        Create browser tool definition for Strands Agent.
        """
        async def browser_tool_handler(action: str, **kwargs) -> str:
            """Handle browser tool execution."""
            return await self.browser_tool.execute(action, **kwargs)

        return {
            "name": "browser_tool",
            "description": "Search AWS documentation or browse web pages using natural language instructions",
            "function": browser_tool_handler,
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["search_aws_docs", "browse_url"],
                        "description": "The action to perform"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query for AWS docs (when action is search_aws_docs)"
                    },
                    "url": {
                        "type": "string",
                        "description": "URL to browse (when action is browse_url)"
                    },
                    "instruction": {
                        "type": "string",
                        "description": "Natural language instruction for browsing (when action is browse_url)"
                    }
                },
                "required": ["action"]
            }
        }

    async def run(self, query: str) -> str:
        """
        Process a user query and return an answer based on AWS documentation.

        Args:
            query: User's question about AWS services or configurations

        Returns:
            Answer based on AWS documentation
        """
        try:
            # Run the agent with the user query
            result = await self.agent.run(query)
            return result
        except Exception as e:
            return f"Error processing query: {str(e)}"

    def run_sync(self, query: str) -> str:
        """
        Synchronous wrapper for the async run method.
        """
        return asyncio.run(self.run(query))


async def main():
    """
    Example usage of the AWS Docs Agent.
    """
    agent = AWSDocsAgent()

    # Example queries
    test_queries = [
        "How do I create an S3 bucket lifecycle policy?",
        "What are the best practices for Lambda cold start optimization?",
        "How to configure DynamoDB Global Secondary Index?"
    ]

    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        result = await agent.run(query)
        print(f"📋 Answer: {result}")


if __name__ == "__main__":
    asyncio.run(main())
