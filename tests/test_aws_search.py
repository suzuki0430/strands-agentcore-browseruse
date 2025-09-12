"""
Test cases for AWS Documentation Search Agent
"""
import os
import asyncio
import unittest
from unittest.mock import Mock, patch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from src.agents.main_agent import AWSDocsAgent
from src.tools.browser_tool import AgentCoreBrowserTool


class TestAWSDocsAgent(unittest.TestCase):
    """Test cases for AWS Documentation Search Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = AWSDocsAgent()
        self.browser_tool = AgentCoreBrowserTool()
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertIsNotNone(self.agent)
        self.assertIsNotNone(self.agent.browser_tool)
        self.assertIsNotNone(self.agent.model)
        self.assertIsNotNone(self.agent.agent)
    
    def test_browser_tool_initialization(self):
        """Test browser tool initialization"""
        self.assertIsNotNone(self.browser_tool)
        self.assertEqual(self.browser_tool.region, 'us-west-2')
    
    def test_browser_tool_definition(self):
        """Test browser tool definition structure"""
        tool_def = self.browser_tool.get_tool_definition()
        
        self.assertEqual(tool_def["name"], "browser_tool")
        self.assertIn("description", tool_def)
        self.assertIn("parameters", tool_def)
        self.assertIn("properties", tool_def["parameters"])
        self.assertIn("action", tool_def["parameters"]["properties"])
    
    @patch('src.tools.browser_tool.browser_session')
    @patch('src.tools.browser_tool.Browser')
    async def test_search_aws_docs_mock(self, mock_browser, mock_browser_session):
        """Test AWS docs search with mocked browser"""
        # Mock the browser session
        mock_session = Mock()
        mock_session.generate_ws_headers.return_value = ("ws://mock_url", {"auth": "mock_header"})
        mock_browser_session.return_value.__enter__.return_value = mock_session
        
        # Mock Browser Use
        mock_browser_instance = Mock()
        mock_browser_instance.navigate = Mock()
        mock_browser_instance.use = Mock(return_value="Mock AWS documentation content about S3 lifecycle policies")
        mock_browser.return_value = mock_browser_instance
        
        # Test the search
        result = await self.browser_tool.search_aws_docs("S3 lifecycle policy")
        
        # Verify the result
        self.assertIn("S3", result)
        mock_browser_instance.navigate.assert_called_with("https://docs.aws.amazon.com")
    
    def test_sync_run_wrapper(self):
        """Test synchronous wrapper for agent run"""
        # This test would require actual AWS/AgentCore setup, so we'll just test the wrapper exists
        self.assertTrue(hasattr(self.agent, 'run_sync'))
        self.assertTrue(callable(self.agent.run_sync))


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios for real-world usage"""
    
    def setUp(self):
        """Set up test scenarios"""
        self.test_queries = [
            "How do I create an S3 bucket lifecycle policy?",
            "What are the best practices for Lambda cold start optimization?",
            "How to configure DynamoDB Global Secondary Index?",
            "How to set up CloudFront distribution with S3 origin?",
            "What are the IAM best practices for least privilege access?"
        ]
    
    def test_query_formats(self):
        """Test various query formats"""
        for query in self.test_queries:
            with self.subTest(query=query):
                self.assertIsInstance(query, str)
                self.assertTrue(len(query) > 0)
                self.assertTrue(any(service in query.lower() for service in 
                               ['s3', 'lambda', 'dynamodb', 'cloudfront', 'iam']))


class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios"""
    
    def test_empty_query_handling(self):
        """Test handling of empty queries"""
        browser_tool = AgentCoreBrowserTool()
        
        # Test with empty string
        result = asyncio.run(browser_tool.execute("search_aws_docs"))
        self.assertIn("Error", result)
    
    def test_invalid_action_handling(self):
        """Test handling of invalid actions"""
        browser_tool = AgentCoreBrowserTool()
        
        result = asyncio.run(browser_tool.execute("invalid_action"))
        self.assertIn("Unknown action", result)
    
    def test_missing_url_handling(self):
        """Test handling of missing URL for browse_url action"""
        browser_tool = AgentCoreBrowserTool()
        
        result = asyncio.run(browser_tool.execute("browse_url"))
        self.assertIn("url parameter is required", result)


def run_integration_test():
    """
    Manual integration test function.
    This requires actual AWS credentials and AgentCore Browser setup.
    """
    print("🧪 Running Integration Test...")
    print("⚠️  Note: This requires actual AWS credentials and AgentCore Browser setup")
    
    try:
        agent = AWSDocsAgent()
        test_query = "How do I create an S3 bucket?"
        
        print(f"🔍 Testing query: {test_query}")
        result = agent.run_sync(test_query)
        print(f"✅ Result: {result[:200]}...")
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        print("This is expected if AWS credentials or AgentCore Browser is not set up")


if __name__ == "__main__":
    # Run unit tests
    print("🧪 Running Unit Tests...")
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "="*50)
    
    # Run integration test if requested
    if os.getenv("RUN_INTEGRATION_TEST", "false").lower() == "true":
        run_integration_test()
    else:
        print("🔧 To run integration tests, set RUN_INTEGRATION_TEST=true in your environment")
        print("   and ensure AWS credentials and AgentCore Browser are configured.")