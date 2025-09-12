"""
Browser Tool that integrates AgentCore Browser and Browser Use
"""
import asyncio
import os
from typing import Dict, Any
from browser_use import Browser
from bedrock_agentcore.tools.browser_client import browser_session


class AgentCoreBrowserTool:
    """
    A tool that combines AWS AgentCore Browser (remote browser environment)
    with Browser Use (browser automation client) for web scraping and interaction.
    """
    
    def __init__(self, region: str = None):
        self.region = region or os.getenv('AGENTCORE_BROWSER_REGION', 'us-west-2')
    
    async def search_aws_docs(self, query: str) -> str:
        """
        Search AWS documentation using natural language query.
        
        Args:
            query: The search query in natural language
            
        Returns:
            Extracted content from AWS documentation
        """
        try:
            # Create AgentCore Browser session and get CDP URL
            with browser_session(self.region) as client:
                ws_url, headers = client.generate_ws_headers()
                
                # Initialize Browser Use with CDP connection
                browser = Browser(
                    cdp_url=ws_url,
                    headers=headers
                )
                
                # Navigate to AWS Documentation
                await browser.navigate("https://docs.aws.amazon.com")
                
                # Use Browser Use's natural language interface to search
                search_instruction = f"Search for '{query}' in the search box and extract the main content from the first relevant result"
                result = await browser.use(search_instruction)
                
                return result
                
        except Exception as e:
            return f"Error searching AWS docs: {str(e)}"
    
    async def browse_url(self, url: str, instruction: str) -> str:
        """
        Browse any URL with specific instructions.
        
        Args:
            url: The URL to browse
            instruction: Natural language instruction for what to do on the page
            
        Returns:
            Result of the browsing action
        """
        try:
            with browser_session(self.region) as client:
                ws_url, headers = client.generate_ws_headers()
                
                browser = Browser(
                    cdp_url=ws_url,
                    headers=headers
                )
                
                await browser.navigate(url)
                result = await browser.use(instruction)
                
                return result
                
        except Exception as e:
            return f"Error browsing {url}: {str(e)}"
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Return tool definition for Strands Agents integration.
        """
        return {
            "name": "browser_tool",
            "description": "Search AWS documentation or browse web pages using natural language instructions",
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
    
    async def execute(self, action: str, **kwargs) -> str:
        """
        Execute the specified action with given parameters.
        """
        if action == "search_aws_docs":
            query = kwargs.get("query", "")
            if not query:
                return "Error: query parameter is required for search_aws_docs action"
            return await self.search_aws_docs(query)
        
        elif action == "browse_url":
            url = kwargs.get("url", "")
            instruction = kwargs.get("instruction", "extract main content")
            if not url:
                return "Error: url parameter is required for browse_url action"
            return await self.browse_url(url, instruction)
        
        else:
            return f"Error: Unknown action '{action}'"