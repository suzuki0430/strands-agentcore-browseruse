# AWS Documentation Search Agent

An AI agent that combines **Strands Agents**, **Amazon Bedrock AgentCore Runtime**, and **Browser Use** to automatically search and summarize AWS official documentation.

Ask questions like "How do I create a lifecycle policy for an S3 bucket?" and the agent will automatically browse AWS official documentation and provide a comprehensive summary of the key points.

## Architecture

```
┌─────────────────────────────────┐
│   Bedrock AgentCore Runtime     │  ← AWS Managed Execution Environment
│  ┌───────────────────────────┐  │
│  │     Strands Agent         │  │  ← Using Claude Sonnet 4
│  │   (browse_url_tool)       │  │
│  └─────────────┬─────────────┘  │
└────────────────┼─────────────────┘
                 │ Tool Execution
                 ▼
       ┌─────────────────────┐
       │    Browser Use      │        ← LLM-driven Browser Automation
       │ (Natural Language)  │
       └──────────┬──────────┘
                  │ CDP WebSocket
                  ▼
   ┌──────────────────────────────┐
   │   AgentCore Browser          │  ← AWS Managed Browser
   │ - Session Isolation          │
   │ - Live View Feature          │
   │ - CloudTrail Auditing        │
   └──────────────────────────────┘
```

## Quick Start

### Prerequisites

- **Python 3.11+**
- **AWS Account with credentials configured**
- **Region: us-west-2** (AgentCore availability)
- **Claude Sonnet 4 foundation model access** enabled in Bedrock

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/suzuki0430/strands-agentcore-browseruse.git
cd strands-agentcore-browseruse

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root (optional for local development):

```bash
# AWS Configuration
AWS_REGION=us-west-2
AWS_DEFAULT_REGION=us-west-2

# Bedrock Model Configuration
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0

# AgentCore Browser Configuration
AGENTCORE_BROWSER_REGION=us-west-2

# AWS Credentials (optional if using IAM roles/profiles)
# AWS_ACCESS_KEY_ID=your_access_key_id
# AWS_SECRET_ACCESS_KEY=your_secret_access_key
# AWS_SESSION_TOKEN=your_session_token  # if using temporary credentials
```

### 3. AWS Credentials Setup

Configure AWS credentials using one of these methods:

#### Option 1: AWS CLI (Recommended)

```bash
aws configure
# Enter your Access Key ID, Secret Access Key, and default region
```

#### Option 2: Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_DEFAULT_REGION=us-west-2
```

#### Option 3: IAM Roles (For EC2/Lambda)

Use IAM roles for service-to-service authentication in production.

### 4. AgentCore Runtime Configuration

```bash
# Configure deployment settings
agentcore configure --entrypoint src/runtime/agentcore_app.py --region us-west-2
```

### 5. IAM Policy Setup

Add the following policy to the IAM role created by `agentcore configure` (role name starts with `AmazonBedrockAgentCoreSDKRuntime-us-west-2-`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BrowserAccess",
      "Effect": "Allow",
      "Action": [
        "bedrock-agentcore:StartBrowserSession",
        "bedrock-agentcore:StopBrowserSession",
        "bedrock-agentcore:ConnectBrowserAutomationStream",
        "bedrock-agentcore:ConnectBrowserLiveViewStream",
        "bedrock-agentcore:ListBrowserSessions",
        "bedrock-agentcore:GetBrowserSession",
        "bedrock-agentcore:ListBrowsers",
        "bedrock-agentcore:GetBrowser"
      ],
      "Resource": "*"
    }
  ]
}
```

### 6. Deploy to AgentCore Runtime

```bash
# Initial deployment
agentcore launch

# Re-deployment with conflict resolution
agentcore launch --auto-update-on-conflict
```

## Usage

### Basic Query

```bash
agentcore invoke '{"prompt": "How can I create a lifecycle policy for an S3 bucket?"}'
```

### Sample Queries

- "What are the best practices for Lambda cold start optimization?"
- "How to create a DynamoDB Global Secondary Index?"
- "CloudFront and S3 integration setup steps"
- "IAM least privilege access best practices"

### Local Development Testing

```bash
# Test agent locally (before deployment)
python src/agents/main_agent.py
```

## 📁 Project Structure

```
src/
├── agents/
│   └── main_agent.py      # Main agent implementation (Strands Agents)
├── runtime/
│   └── agentcore_app.py   # AgentCore Runtime integration
└── tools/
    └── browser_tool.py    # Browser automation tool
tests/
└── test_aws_search.py     # Test cases
requirements.txt           # Python dependencies
Dockerfile                 # Container configuration
.env                       # Environment variables (not tracked)
```

## Technical Specifications

### Technology Stack

- **Strands Agents v1.8.0** - Agent framework
- **Browser Use <0.3.3** - Browser automation library
- **Amazon Bedrock AgentCore** - Managed execution and browser environment
- **Claude Sonnet 4** - LLM model
- **Python 3.11+**

## References

- [Amazon Bedrock AgentCore](https://aws.amazon.com/blogs/aws/introducing-amazon-bedrock-agentcore-securely-deploy-and-operate-ai-agents-at-any-scale/)
- [Strands Agents Documentation](https://strandsagents.com/latest/)
- [Browser Use GitHub](https://github.com/browser-use/browser-use)
- [AgentCore Browser Workshop](https://catalog.us-east-1.prod.workshops.aws/workshops/015a2de4-9522-4532-b2eb-639280dc31d8/en-US/60-agentcore-tools/62-browser-tool)
