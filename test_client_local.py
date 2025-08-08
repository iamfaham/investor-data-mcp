from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()


async def main():
    # Try with potential authentication headers
    headers = {}

    # If you have an API key for Smithery, add it here
    # headers["Authorization"] = "Bearer YOUR_API_KEY"

    client = MultiServerMCPClient(
        {
            "vc_data": {
                "url": "http://localhost:8000/mcp",  # VC Data server endpoint
                "transport": "streamable_http",
                "headers": headers,  # Add headers if needed
            }
        }
    )

    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

    tools = await client.get_tools()
    model = ChatGroq(model="openai/gpt-oss-120b")
    agent = create_react_agent(model, tools)

    print("=== VC Data MCP Server Test Client ===\n")

    # Test 1: Basic investor data retrieval
    print("1. Testing basic investor data retrieval...")
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
    print("Search response:", search_response["messages"][-1].content[:200] + "...\n")

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

    # Test 4: Cheque size search
    print("4. Testing cheque size search...")
    cheque_response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Find investors that invest between 100k and 1M",
                }
            ]
        }
    )
    print(
        "Cheque size response:", cheque_response["messages"][-1].content[:200] + "...\n"
    )

    # Test 5: Investment thesis analysis
    print("5. Testing investment thesis analysis...")
    thesis_response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Analyze investment thesis patterns and find common themes",
                }
            ]
        }
    )
    print(
        "Thesis analysis response:",
        thesis_response["messages"][-1].content[:200] + "...\n",
    )

    # Test 6: Database statistics
    print("6. Testing database statistics...")
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
        "Statistics response:", stats_response["messages"][-1].content[:200] + "...\n"
    )

    # Test 7: Similar investors (using a well-known investor)
    print("7. Testing similar investors search...")
    similar_response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Find investors similar to Y Combinator",
                }
            ]
        }
    )
    print(
        "Similar investors response:",
        similar_response["messages"][-1].content[:200] + "...\n",
    )

    # Test 8: Available investor types
    print("8. Testing available investor types...")
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

    # Test 9: Available countries
    print("9. Testing available countries...")
    countries_response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Show me all available countries in the database",
                }
            ]
        }
    )
    print(
        "Available countries response:",
        countries_response["messages"][-1].content[:200] + "...\n",
    )

    # Test 10: Location search guide
    print("10. Testing location search guide...")
    guide_response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Explain the difference between country and HQ location searches",
                }
            ]
        }
    )
    print(
        "Location guide response:",
        guide_response["messages"][-1].content[:200] + "...\n",
    )

    # Test 11: Complex search (multiple criteria)
    print("11. Testing complex search with multiple criteria...")
    complex_response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Find VC investors in USA that invest in Series A stage and are headquartered in California",
                }
            ]
        }
    )
    print(
        "Complex search response:",
        complex_response["messages"][-1].content[:200] + "...\n",
    )

    # Test 12: Thesis keyword search
    print("12. Testing thesis-based search...")
    thesis_search_response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Find investors that mention AI or artificial intelligence in their thesis",
                }
            ]
        }
    )
    print(
        "Thesis search response:",
        thesis_search_response["messages"][-1].content[:200] + "...\n",
    )

    print("=== All tests completed! ===")


if __name__ == "__main__":
    asyncio.run(main())
