"""
AgentCore Runtime Application
"""
import os
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from src.agents.main_agent import AWSDocsAgent

# Load environment variables
load_dotenv()

# Initialize the AgentCore app
app = BedrockAgentCoreApp()

# Initialize the AWS Docs Agent
aws_docs_agent = AWSDocsAgent()


@app.entrypoint
def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entrypoint for AgentCore Runtime.
    
    Args:
        payload: Request payload containing the user prompt
        
    Returns:
        Response dictionary with the agent's result
    """
    try:
        # Extract the prompt from payload
        prompt = payload.get("prompt", "")
        if not prompt:
            return {
                "error": "No prompt provided in the request payload"
            }
        
        # Run the agent synchronously (AgentCore Runtime expects sync functions)
        result = aws_docs_agent.run_sync(prompt)
        
        return {
            "result": result,
            "status": "success"
        }
        
    except Exception as e:
        return {
            "error": f"Error processing request: {str(e)}",
            "status": "error"
        }


@app.health_check
def health_check() -> Dict[str, str]:
    """
    Health check endpoint for AgentCore Runtime.
    """
    return {
        "status": "healthy",
        "service": "AWS Docs Agent",
        "version": "1.0.0"
    }


def main():
    """
    Start the AgentCore Runtime application.
    """
    print("🚀 Starting AWS Docs Agent on AgentCore Runtime...")
    print("📋 Agent capabilities:")
    print("   - Search AWS documentation")
    print("   - Browse web pages with natural language")
    print("   - Extract information from web content")
    print()
    print("🌐 Server starting on port 8080...")
    
    # Run the app (this will start the HTTP server on port 8080)
    app.run()


if __name__ == "__main__":
    main()