"""
AgentCore Runtime Application
"""
import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from src.agents.main_agent import create_agent

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set timeout for long-running browser operations
os.environ['UVICORN_TIMEOUT_KEEP_ALIVE'] = '28800'
os.environ['UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN'] = '28800'

# Initialize the AgentCore app
app = BedrockAgentCoreApp()


@app.entrypoint
async def invoke(payload: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Main entrypoint for AgentCore Runtime.
    Note: This must be async and accept a context parameter for AgentCore compatibility.
    
    Args:
        payload: Request payload containing the user prompt
        context: AgentCore runtime context (required by framework)
        
    Returns:
        Response dictionary with the agent's result
    """
    try:
        # Extract the prompt from payload
        prompt = payload.get("prompt", "")
        if not prompt:
            return {
                "error": "No prompt provided in the request payload",
                "status": "error"
            }
        
        logger.info(f"Processing request: {prompt[:100]}...")
        
        # Create and invoke the agent
        agent = create_agent()
        
        # Use synchronous invocation (the agent handles it internally)
        result = agent(prompt)
        
        logger.info("Request processed successfully")
        
        return {
            "result": str(result),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return {
            "error": f"Error processing request: {str(e)}",
            "status": "error"
        }


@app.ping
def ping():
    """
    Custom ping endpoint to avoid the dict attribute error.
    """
    return {"status": "healthy", "message": "Agent is running"}


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