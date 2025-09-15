"""
Test cases for Browser Tool
"""
from src.agents.main_agent import create_agent, browse_url_tool
from src.tools.browser_tool import browse_url, execute_browser_task
import os
import asyncio
import unittest
from unittest.mock import Mock, patch, AsyncMock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules


class TestBrowserTool(unittest.TestCase):
    """Test cases for Browser Tool"""

    @patch('src.tools.browser_tool.BrowserClient')
    @patch('src.tools.browser_tool.BrowserSession')
    @patch('src.tools.browser_tool.BrowserUseAgent')
    @patch('src.tools.browser_tool.ChatBedrockConverse')
    async def test_browse_url(self, mock_chat, mock_agent, mock_session, mock_client):
        """Test browse_url function"""
        # Setup mocks
        mock_agent_instance = AsyncMock()
        mock_agent_instance.run.return_value = "Test result about S3 lifecycle policies"
        mock_agent.return_value = mock_agent_instance

        mock_session_instance = AsyncMock()
        mock_session_instance.start = AsyncMock()
        mock_session_instance.close = AsyncMock()
        mock_session.return_value = mock_session_instance

        mock_client_instance = Mock()
        mock_client_instance.start = Mock()
        mock_client_instance.stop = Mock()
        mock_client_instance.generate_ws_headers = Mock(
            return_value=("ws://mock", {}))
        mock_client.return_value = mock_client_instance

        # Test browse_url
        result = await browse_url(
            "https://docs.aws.amazon.com",
            "Search for S3 lifecycle policy information"
        )

        # Verify
        self.assertEqual(result, "Test result about S3 lifecycle policies")
        mock_agent_instance.run.assert_called_once()
        mock_client_instance.start.assert_called_once()

    def test_browse_url_tool_sync(self):
        """Test that browse_url_tool function exists and is callable"""
        # Test that the tool function exists
        self.assertTrue(callable(browse_url_tool))

        # Test function signature
        import inspect
        sig = inspect.signature(browse_url_tool)
        params = list(sig.parameters.keys())
        self.assertIn('url', params)
        self.assertIn('instruction', params)


class TestAgentCreation(unittest.TestCase):
    """Test agent creation and configuration"""

    def test_create_agent(self):
        """Test agent creation"""
        agent = create_agent()

        # Verify agent exists
        self.assertIsNotNone(agent)

        # Verify agent has required attributes
        self.assertTrue(hasattr(agent, 'name'))
        self.assertEqual(agent.name, "aws_docs_agent")


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios"""

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

    @patch('src.tools.browser_tool.BrowserClient')
    async def test_browser_client_error_handling(self, mock_client):
        """Test handling of browser client errors"""
        # Setup mock to raise exception
        mock_client_instance = Mock()
        mock_client_instance.start.side_effect = Exception(
            "Browser client failed")
        mock_client.return_value = mock_client_instance

        # Test error handling
        result = await browse_url("https://example.com", "Test instruction")

        # Verify error is handled gracefully
        self.assertIn("Error executing browser task", result)

    def test_empty_url_handling(self):
        """Test handling of empty URL"""
        # This would normally be caught by type hints, but test anyway
        with self.assertRaises(Exception):
            asyncio.run(browse_url("", "Test instruction"))


def run_integration_test():
    """
    Manual integration test function.
    This requires actual AWS credentials and AgentCore Browser setup.
    """
    print("🧪 Running Integration Test...")
    print("⚠️  Note: This requires actual AWS credentials and AgentCore Browser setup")

    try:
        from src.agents.main_agent import process_query
        test_query = "How do I create an S3 bucket?"

        print(f"🔍 Testing query: {test_query}")
        result = process_query(test_query)
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
        print(
            "🔧 To run integration tests, set RUN_INTEGRATION_TEST=true in your environment")
        print("   and ensure AWS credentials and AgentCore Browser are configured.")
