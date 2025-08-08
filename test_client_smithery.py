import mcp
from mcp.client.streamable_http import streamablehttp_client
import os
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
import asyncio

# Load environment variables from .env file
load_dotenv()

smithery_api_key = os.environ.get("SMITHERY_API_KEY")
smithery_profile = os.environ.get("SMITHERY_PROFILE")

if not smithery_api_key or not smithery_profile:
    print(
        "❌ Error: SMITHERY_API_KEY and SMITHERY_PROFILE environment variables must be set"
    )
    print(
        "Please set these environment variables in your .env file or environment and try again."
    )
    exit(1)

url = f"https://server.smithery.ai/@iamfaham/investor-data-deploy-mcp/mcp?api_key={smithery_api_key}&profile={smithery_profile}"


async def test_mcp_direct():
    """Test direct MCP connection"""
    print("=== Testing Direct MCP Connection ===")
    try:
        async with streamablehttp_client(url) as (read_stream, write_stream, _):
            async with mcp.ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools_result = await session.list_tools()
                print(
                    f"Available tools: {', '.join([t.name for t in tools_result.tools])}"
                )
                return True
    except Exception as e:
        print(f"Direct MCP connection failed: {e}")
        return False


async def test_with_langchain():
    """Test with LangChain MCP client and ChatGroq"""
    print("\n=== Testing with LangChain MCP Client and ChatGroq ===")

    # Set up the MCP client with Smithery URL
    client = MultiServerMCPClient(
        {
            "vc_data": {
                "url": url,
                "transport": "streamable_http",
            }
        }
    )

    # Set up ChatGroq
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("⚠️ GROQ_API_KEY environment variable not set. Skipping LangChain tests.")
        return False

    model = ChatGroq(model="openai/gpt-oss-120b")

    try:
        tools = await client.get_tools()
        agent = create_react_agent(model, tools)

        print(f"Successfully connected! Found {len(tools)} tools")
        print("Available tools:")
        for tool in tools:
            print(f"- {tool.name}")

        # Test 1: Basic investor data retrieval
        print("\n1. Testing basic investor data retrieval...")
        investor_response = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "Show me the top 5 investors from the database",
                    }
                ]
            }
        )
        print(
            "Investor data response:",
            investor_response["messages"][-1].content[:200] + "...\n",
        )

        # Test 2: Search by criteria (Angel investors in USA)
        print("2. Testing search by criteria...")
        search_response = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "Find me angel investors in the United States",
                    }
                ]
            }
        )
        print(
            "Search response:", search_response["messages"][-1].content[:200] + "...\n"
        )

        # Test 3: Investment stage analysis
        print("3. Testing investment stage analysis...")
        stage_analysis_response = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "Analyze the distribution of investment stages across all investors",
                    }
                ]
            }
        )
        print(
            "Stage analysis response:",
            stage_analysis_response["messages"][-1].content[:200] + "...\n",
        )

        # Test 4: Database statistics
        print("4. Testing database statistics...")
        stats_response = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "Get comprehensive statistics about the investor database",
                    }
                ]
            }
        )
        print(
            "Statistics response:",
            stats_response["messages"][-1].content[:200] + "...\n",
        )

        # Test 5: Available investor types
        print("5. Testing available investor types...")
        types_response = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "Show me all available investor types in the database",
                    }
                ]
            }
        )
        print(
            "Available types response:",
            types_response["messages"][-1].content[:200] + "...\n",
        )

        print("=== All LangChain tests completed successfully! ===")
        return True

    except Exception as e:
        print(f"LangChain test failed: {e}")
        return False


async def main():
    print("=== VC Data MCP Server Smithery Test Client ===\n")

    # Test direct MCP connection
    direct_success = await test_mcp_direct()

    # Test with LangChain and ChatGroq
    langchain_success = await test_with_langchain()

    # Summary
    print("\n=== Test Summary ===")
    print(f"Direct MCP Connection: {'✅ PASSED' if direct_success else '❌ FAILED'}")

    if langchain_success is False and not os.getenv("GROQ_API_KEY"):
        print("LangChain + ChatGroq: ⏭️ SKIPPED (GROQ_API_KEY not set)")
    else:
        print(
            f"LangChain + ChatGroq: {'✅ PASSED' if langchain_success else '❌ FAILED'}"
        )

    if direct_success and (langchain_success or not os.getenv("GROQ_API_KEY")):
        print(
            "\n🎉 Core MCP functionality is working! Your Smithery deployment is accessible."
        )
        if not os.getenv("GROQ_API_KEY"):
            print(
                "💡 To test full AI functionality, set the GROQ_API_KEY environment variable."
            )
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")


if __name__ == "__main__":
    asyncio.run(main())
