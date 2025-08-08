from mcp.server.fastmcp import FastMCP
import os
from typing import Dict, List, Any, Optional

# from dotenv import load_dotenv
from supabase import create_client, Client

# load_dotenv()

port = int(os.environ.get("PORT", "8000"))

mcp = FastMCP(
    name="VC Data Server",
    host="0.0.0.0",
    port=port,
    stateless_http=True,
)


def fetch_data_from_supabase(
    table_name: str,
    select_columns: Optional[List[str]] = None,
    filters: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Fetch data from OpenVC database.

    Args:
        table_name (str): Name of the table to fetch data from
        select_columns (Optional[List[str]]): List of columns to select. If None, selects all columns
        filters (Optional[Dict[str, Any]]): Dictionary of filters to apply (column: value)
        limit (Optional[int]): Maximum number of records to return

    Returns:
        List[Dict[str, Any]]: List of records from the table

    Raises:
        ValueError: If Supabase credentials are not configured
        Exception: If there's an error connecting to Supabase or fetching data
    """
    # Get Supabase credentials from environment variables
    # supabase_url = os.environ.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
    supabase_url = os.environ.get("SUPABASE_URL")
    # supabase_key = os.environ.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")
    supabase_key = os.environ.get("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError(
            "Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_KEY "
            "environment variables or add them to your .env file."
        )

    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)

        # Build the query
        if select_columns is None:
            query = supabase.table(table_name).select("*")
        else:
            # Handle column names with spaces by wrapping them in quotes
            quoted_columns = [f'"{col}"' for col in select_columns]
            query = supabase.table(table_name).select(", ".join(quoted_columns))

        # Apply filters if provided
        if filters:
            for column, value in filters.items():
                # Handle column names with spaces by wrapping them in quotes
                quoted_column = f'"{column}"'
                query = query.eq(quoted_column, value)

        # Apply limit if provided
        if limit:
            query = query.limit(limit)

        # Execute the query
        response = query.execute()

        # Return the data
        return response.data

    except Exception as e:
        raise Exception(f"Error fetching data from Supabase: {str(e)}")


@mcp.tool()
async def get_investor_data(limit: Optional[int] = None) -> str:
    """
    Fetches investor data from the OpenVC database.
    Use this tool when a user asks for investor information, VC data, or startup funding data.

    Args:
        limit (Optional[int]): Maximum number of records to return. If None, fetches all records.

    Returns:
        str: Formatted string containing investor records with the following information:
        - Investor name
        - Website
        - Global HQ
        - Countries of investment
        - Stage of investment
        - Investment thesis
        - Investor type
        - First cheque minimum and maximum
    """
    try:
        data = fetch_data_from_supabase(
            table_name="dec-2024",
            select_columns=[
                "Investor name",
                "Website",
                "Global HQ",
                "Countries of investment",
                "Stage of investment",
                "Investment thesis",
                "Investor type",
                "First cheque minimum",
                "First cheque maximum",
            ],
            limit=limit,
        )

        if not data:
            return "No investor data found."

        # Format the data into a clean string for the LLM
        formatted_response = f"Found {len(data)} investor records:\n\n"

        for i, investor in enumerate(data[:10], 1):  # Show top 10 by default
            formatted_response += f"{i}. {investor.get('Investor name', 'N/A')}\n"
            formatted_response += f"   Website: {investor.get('Website', 'N/A')}\n"
            formatted_response += f"   Global HQ: {investor.get('Global HQ', 'N/A')}\n"
            formatted_response += (
                f"   Countries: {investor.get('Countries of investment', 'N/A')}\n"
            )
            formatted_response += (
                f"   Stage: {investor.get('Stage of investment', 'N/A')}\n"
            )
            formatted_response += f"   Type: {investor.get('Investor type', 'N/A')}\n"
            formatted_response += f"   First Cheque: {investor.get('First cheque minimum', 'N/A')} - {investor.get('First cheque maximum', 'N/A')}\n"
            thesis = investor.get("Investment thesis", "N/A")
            if len(thesis) > 100:
                thesis = thesis[:100] + "..."
            formatted_response += f"   Thesis: {thesis}\n"
            formatted_response += "-" * 80 + "\n\n"

        if len(data) > 10:
            formatted_response += f"... and {len(data) - 10} more records."

        return formatted_response

    except Exception as e:
        return f"An error occurred while fetching investor data: {e}"


@mcp.tool()
async def search_investors_by_criteria(
    investor_type: Optional[str] = None,
    stage: Optional[str] = None,
    country: Optional[str] = None,
    hq_location: Optional[str] = None,
    limit: Optional[int] = None,
) -> str:
    """
    Search for investors based on specific criteria.
    Use this tool when a user wants to find investors by type, investment stage, country, or HQ location.

    Args:
        investor_type (Optional[str]): Type of investor (e.g., "Angel", "VC", "PE")
        stage (Optional[str]): Investment stage (e.g., "Seed", "Series A", "Growth")
        country (Optional[str]): Country of investment (uses country codes like "USA")
        hq_location (Optional[str]): Global HQ location (can be city, state, or country)
        limit (Optional[int]): Maximum number of records to return

    Returns:
        str: Formatted string containing matching investor records
    """
    try:
        # Map common investor type names to database values
        investor_type_mapping = {
            "angel": "Angel network",
            "angel network": "Angel network",
            "vc": "VC",
            "venture capital": "VC",
            "pe": "PE",
            "private equity": "PE",
            "cvc": "CVC",
            "corporate venture capital": "CVC",
        }

        # Map common country names to database values
        country_mapping = {
            "united states": "USA",
            "usa": "USA",
            "us": "USA",
            "america": "USA",
            "united kingdom": "UK",
            "uk": "UK",
            "england": "UK",
            "great britain": "UK",
            "germany": "Germany",
            "france": "France",
            "canada": "Canada",
            "australia": "Australia",
            "japan": "Japan",
            "china": "China",
            "india": "India",
            "singapore": "Singapore",
            "netherlands": "Netherlands",
            "sweden": "Sweden",
            "switzerland": "Switzerland",
            "israel": "Israel",
        }

        filters = {}
        if investor_type:
            # Convert to lowercase for case-insensitive matching
            investor_type_lower = investor_type.lower()
            # Use mapping if available, otherwise use original value
            mapped_type = investor_type_mapping.get(investor_type_lower, investor_type)
            filters["Investor type"] = mapped_type
        if stage:
            filters["Stage of investment"] = stage
        if country:
            # Convert to lowercase for case-insensitive matching
            country_lower = country.lower()
            # Use mapping if available, otherwise use original value
            mapped_country = country_mapping.get(country_lower, country)
            filters["Countries of investment"] = mapped_country
        if hq_location:
            # For HQ location, we'll do a case-insensitive search
            # This allows searching for cities, states, or countries in the address
            filters["Global HQ"] = hq_location

        data = fetch_data_from_supabase(
            table_name="dec-2024",
            select_columns=[
                "Investor name",
                "Website",
                "Global HQ",
                "Countries of investment",
                "Stage of investment",
                "Investment thesis",
                "Investor type",
                "First cheque minimum",
                "First cheque maximum",
            ],
            filters=filters,
            limit=limit,
        )

        if not data:
            filter_desc = []
            if investor_type:
                filter_desc.append(f"type: {investor_type}")
            if stage:
                filter_desc.append(f"stage: {stage}")
            if country:
                filter_desc.append(f"country: {country}")
            if hq_location:
                filter_desc.append(f"HQ location: {hq_location}")

            filter_str = (
                ", ".join(filter_desc) if filter_desc else "the specified criteria"
            )
            return f"No investors found matching {filter_str}."

        # Format the data
        formatted_response = f"Found {len(data)} investors matching your criteria:\n\n"

        for i, investor in enumerate(data[:10], 1):  # Show top 10 by default
            formatted_response += f"{i}. {investor.get('Investor name', 'N/A')}\n"
            formatted_response += f"   Website: {investor.get('Website', 'N/A')}\n"
            formatted_response += f"   Global HQ: {investor.get('Global HQ', 'N/A')}\n"
            formatted_response += (
                f"   Countries: {investor.get('Countries of investment', 'N/A')}\n"
            )
            formatted_response += (
                f"   Stage: {investor.get('Stage of investment', 'N/A')}\n"
            )
            formatted_response += f"   Type: {investor.get('Investor type', 'N/A')}\n"
            formatted_response += f"   First Cheque: {investor.get('First cheque minimum', 'N/A')} - {investor.get('First cheque maximum', 'N/A')}\n"
            thesis = investor.get("Investment thesis", "N/A")
            if len(thesis) > 100:
                thesis = thesis[:100] + "..."
            formatted_response += f"   Thesis: {thesis}\n"
            formatted_response += "-" * 80 + "\n\n"

        if len(data) > 10:
            formatted_response += f"... and {len(data) - 10} more records."

        return formatted_response

    except Exception as e:
        return f"An error occurred while searching investors: {e}"


@mcp.tool()
async def get_available_investor_types() -> str:
    """
    Get a list of all available investor types in the database.
    Use this tool when a user wants to know what investor types are available for searching.

    Returns:
        str: List of all unique investor types in the database
    """
    try:
        # Get all investor types from the database
        data = fetch_data_from_supabase(
            table_name="dec-2024",
            select_columns=["Investor type"],
            limit=None,  # Get all records to find unique types
        )

        if not data:
            return "No investor data found."

        # Extract unique investor types
        investor_types = set()
        for record in data:
            investor_type = record.get("Investor type")
            if investor_type:
                investor_types.add(investor_type)

        if not investor_types:
            return "No investor types found in the database."

        # Format the response
        formatted_response = "Available investor types in the database:\n\n"
        for i, investor_type in enumerate(sorted(investor_types), 1):
            formatted_response += f"{i}. {investor_type}\n"

        formatted_response += f"\nTotal: {len(investor_types)} unique investor types"
        return formatted_response

    except Exception as e:
        return f"An error occurred while fetching investor types: {e}"


@mcp.tool()
async def get_available_countries() -> str:
    """
    Get a list of all available countries in the database.
    Use this tool when a user wants to know what countries are available for searching.

    Returns:
        str: List of all unique countries in the database
    """
    try:
        # Get all countries from the database
        data = fetch_data_from_supabase(
            table_name="dec-2024",
            select_columns=["Countries of investment"],
            limit=None,  # Get all records to find unique countries
        )

        if not data:
            return "No investor data found."

        # Extract unique countries
        countries = set()
        for record in data:
            country = record.get("Countries of investment")
            if country:
                # Handle cases where multiple countries might be comma-separated
                if "," in country:
                    for single_country in country.split(","):
                        countries.add(single_country.strip())
                else:
                    countries.add(country.strip())

        if not countries:
            return "No countries found in the database."

        # Format the response
        formatted_response = "Available countries in the database:\n\n"
        for i, country in enumerate(sorted(countries), 1):
            formatted_response += f"{i}. {country}\n"

        formatted_response += f"\nTotal: {len(countries)} unique countries"
        return formatted_response

    except Exception as e:
        return f"An error occurred while fetching countries: {e}"


@mcp.tool()
async def get_location_search_guide() -> str:
    """
    Provides guidance on how to search for investors by location.
    Use this tool when a user wants to understand the difference between country and HQ location searches.

    Returns:
        str: Explanation of location search options
    """
    return """
    Location Search Guide:
    
    There are two different ways to search for investors by location:
    
    1. COUNTRY OF INVESTMENT (country parameter):
       - Uses country codes like "USA", "UK", "Germany"
       - Shows where the investor makes investments
       - Example: "Find VCs in USA" or "Angel investors in UK"
    
    2. GLOBAL HQ LOCATION (hq_location parameter):
       - Uses full addresses like "San Francisco, CA" or "New York, NY"
       - Shows where the investor's headquarters is located
       - Example: "Investors headquartered in San Francisco" or "VCs in New York"
    
    Tips:
    - Use "country" for broad geographic investment areas
    - Use "hq_location" for specific city/state searches
    - You can search for cities, states, or countries in HQ location
    - Country searches are more precise, HQ searches are more flexible
    """


@mcp.tool()
async def analyze_investment_stages() -> str:
    """
    Analyze the distribution of investment stages across all investors.
    Use this tool when a user wants to understand what investment stages are most common or get insights about the investment landscape.

    Returns:
        str: Analysis of investment stages with statistics and insights
    """
    try:
        data = fetch_data_from_supabase(
            table_name="dec-2024",
            select_columns=["Stage of investment"],
            limit=None,
        )

        if not data:
            return "No investor data found."

        # Count stages
        stage_counts = {}
        for record in data:
            stage = record.get("Stage of investment")
            if stage:
                stage_counts[stage] = stage_counts.get(stage, 0) + 1

        if not stage_counts:
            return "No investment stage data found."

        # Sort by count
        sorted_stages = sorted(stage_counts.items(), key=lambda x: x[1], reverse=True)

        formatted_response = "Investment Stage Analysis:\n\n"
        total_investors = sum(stage_counts.values())

        for stage, count in sorted_stages:
            percentage = (count / total_investors) * 100
            formatted_response += f"• {stage}: {count} investors ({percentage:.1f}%)\n"

        formatted_response += f"\nTotal investors analyzed: {total_investors}"
        formatted_response += f"\nUnique investment stages: {len(stage_counts)}"

        return formatted_response

    except Exception as e:
        return f"An error occurred while analyzing investment stages: {e}"


@mcp.tool()
async def find_investors_by_cheque_size(
    min_amount: Optional[str] = None,
    max_amount: Optional[str] = None,
    limit: Optional[int] = None,
) -> str:
    """
    Find investors based on their typical investment size (first cheque range).
    Use this tool when a user wants to find investors that invest within a specific amount range.

    Args:
        min_amount (Optional[str]): Minimum investment amount (e.g., "100k", "1M", "10M")
        max_amount (Optional[str]): Maximum investment amount (e.g., "500k", "5M", "50M")
        limit (Optional[int]): Maximum number of records to return

    Returns:
        str: Formatted string containing matching investor records
    """
    try:
        # Get all investors with cheque size data
        data = fetch_data_from_supabase(
            table_name="dec-2024",
            select_columns=[
                "Investor name",
                "Website",
                "Global HQ",
                "Countries of investment",
                "Stage of investment",
                "Investment thesis",
                "Investor type",
                "First cheque minimum",
                "First cheque maximum",
            ],
            limit=None,
        )

        if not data:
            return "No investor data found."

        # Filter by cheque size if specified
        filtered_data = []
        for investor in data:
            min_cheque = investor.get("First cheque minimum")
            max_cheque = investor.get("First cheque maximum")

            # Skip if no cheque data
            if not min_cheque or not max_cheque:
                continue

            # Apply filters if specified
            include_investor = True

            if min_amount:
                # Simple comparison - in a real implementation, you'd want to parse amounts
                if min_cheque.lower() < min_amount.lower():
                    include_investor = False

            if max_amount and include_investor:
                if max_cheque.lower() > max_amount.lower():
                    include_investor = False

            if include_investor:
                filtered_data.append(investor)

        if not filtered_data:
            filter_desc = []
            if min_amount:
                filter_desc.append(f"minimum: {min_amount}")
            if max_amount:
                filter_desc.append(f"maximum: {max_amount}")

            filter_str = (
                ", ".join(filter_desc) if filter_desc else "the specified criteria"
            )
            return f"No investors found matching {filter_str}."

        # Apply limit
        if limit:
            filtered_data = filtered_data[:limit]

        # Format the response
        formatted_response = (
            f"Found {len(filtered_data)} investors matching your criteria:\n\n"
        )

        for i, investor in enumerate(filtered_data[:10], 1):  # Show top 10 by default
            formatted_response += f"{i}. {investor.get('Investor name', 'N/A')}\n"
            formatted_response += f"   Website: {investor.get('Website', 'N/A')}\n"
            formatted_response += f"   Global HQ: {investor.get('Global HQ', 'N/A')}\n"
            formatted_response += (
                f"   Countries: {investor.get('Countries of investment', 'N/A')}\n"
            )
            formatted_response += (
                f"   Stage: {investor.get('Stage of investment', 'N/A')}\n"
            )
            formatted_response += f"   Type: {investor.get('Investor type', 'N/A')}\n"
            formatted_response += f"   First Cheque: {investor.get('First cheque minimum', 'N/A')} - {investor.get('First cheque maximum', 'N/A')}\n"
            thesis = investor.get("Investment thesis", "N/A")
            if len(thesis) > 100:
                thesis = thesis[:100] + "..."
            formatted_response += f"   Thesis: {thesis}\n"
            formatted_response += "-" * 80 + "\n\n"

        if len(filtered_data) > 10:
            formatted_response += f"... and {len(filtered_data) - 10} more records."

        return formatted_response

    except Exception as e:
        return f"An error occurred while searching by cheque size: {e}"


@mcp.tool()
async def analyze_investment_thesis() -> str:
    """
    Analyze investment thesis patterns across all investors.
    Use this tool when a user wants to understand common investment themes, focus areas, or strategies.

    Returns:
        str: Analysis of investment thesis patterns and common themes
    """
    try:
        data = fetch_data_from_supabase(
            table_name="dec-2024",
            select_columns=[
                "Investment thesis",
                "Investor type",
                "Stage of investment",
            ],
            limit=None,
        )

        if not data:
            return "No investor data found."

        # Extract thesis data
        thesis_data = []
        for record in data:
            thesis = record.get("Investment thesis")
            investor_type = record.get("Investor type")
            stage = record.get("Stage of investment")

            if thesis and thesis != "N/A":
                thesis_data.append(
                    {"thesis": thesis, "type": investor_type, "stage": stage}
                )

        if not thesis_data:
            return "No investment thesis data found."

        # Analyze common themes (simplified analysis)
        common_keywords = [
            "AI",
            "artificial intelligence",
            "machine learning",
            "ML",
            "fintech",
            "financial technology",
            "healthtech",
            "healthcare",
            "SaaS",
            "software",
            "enterprise",
            "B2B",
            "B2C",
            "ecommerce",
            "marketplace",
            "platform",
            "mobile",
            "biotech",
            "biotechnology",
            "clean energy",
            "sustainability",
            "cybersecurity",
            "security",
            "blockchain",
            "crypto",
            "edtech",
            "education",
            "real estate",
            "proptech",
        ]

        keyword_counts = {}
        for keyword in common_keywords:
            count = sum(
                1 for item in thesis_data if keyword.lower() in item["thesis"].lower()
            )
            if count > 0:
                keyword_counts[keyword] = count

        # Sort by count
        sorted_keywords = sorted(
            keyword_counts.items(), key=lambda x: x[1], reverse=True
        )

        formatted_response = "Investment Thesis Analysis:\n\n"
        formatted_response += (
            f"Total investors with thesis data: {len(thesis_data)}\n\n"
        )

        formatted_response += "Most Common Investment Themes:\n"
        for keyword, count in sorted_keywords[:10]:  # Top 10
            percentage = (count / len(thesis_data)) * 100
            formatted_response += (
                f"• {keyword}: {count} investors ({percentage:.1f}%)\n"
            )

        # Analysis by investor type
        type_thesis = {}
        for item in thesis_data:
            investor_type = item["type"]
            if investor_type not in type_thesis:
                type_thesis[investor_type] = []
            type_thesis[investor_type].append(item["thesis"])

        formatted_response += f"\nThesis Analysis by Investor Type:\n"
        for investor_type, theses in type_thesis.items():
            if len(theses) > 5:  # Only show types with enough data
                formatted_response += f"• {investor_type}: {len(theses)} investors\n"

        return formatted_response

    except Exception as e:
        return f"An error occurred while analyzing investment thesis: {e}"


@mcp.tool()
async def get_investor_statistics() -> str:
    """
    Get comprehensive statistics about the investor database.
    Use this tool when a user wants to understand the overall composition and distribution of investors.

    Returns:
        str: Comprehensive statistics about the investor database
    """
    try:
        data = fetch_data_from_supabase(
            table_name="dec-2024",
            select_columns=[
                "Investor name",
                "Investor type",
                "Stage of investment",
                "Countries of investment",
                "Global HQ",
                "First cheque minimum",
                "First cheque maximum",
            ],
            limit=None,
        )

        if not data:
            return "No investor data found."

        # Calculate statistics
        total_investors = len(data)

        # Investor types
        type_counts = {}
        for record in data:
            investor_type = record.get("Investor type")
            if investor_type:
                type_counts[investor_type] = type_counts.get(investor_type, 0) + 1

        # Investment stages
        stage_counts = {}
        for record in data:
            stage = record.get("Stage of investment")
            if stage:
                stage_counts[stage] = stage_counts.get(stage, 0) + 1

        # Countries
        country_counts = {}
        for record in data:
            countries = record.get("Countries of investment")
            if countries:
                if "," in countries:
                    for country in countries.split(","):
                        country = country.strip()
                        country_counts[country] = country_counts.get(country, 0) + 1
                else:
                    country_counts[countries] = country_counts.get(countries, 0) + 1

        # Cheque size analysis
        cheque_data = []
        for record in data:
            min_cheque = record.get("First cheque minimum")
            max_cheque = record.get("First cheque maximum")
            if (
                min_cheque
                and max_cheque
                and min_cheque != "N/A"
                and max_cheque != "N/A"
            ):
                cheque_data.append((min_cheque, max_cheque))

        # Format response
        formatted_response = "Investor Database Statistics:\n\n"
        formatted_response += f"Total Investors: {total_investors}\n\n"

        # Top investor types
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        formatted_response += "Top Investor Types:\n"
        for investor_type, count in sorted_types[:5]:
            percentage = (count / total_investors) * 100
            formatted_response += f"• {investor_type}: {count} ({percentage:.1f}%)\n"

        # Top investment stages
        sorted_stages = sorted(stage_counts.items(), key=lambda x: x[1], reverse=True)
        formatted_response += f"\nTop Investment Stages:\n"
        for stage, count in sorted_stages[:5]:
            percentage = (count / total_investors) * 100
            formatted_response += f"• {stage}: {count} ({percentage:.1f}%)\n"

        # Top countries
        sorted_countries = sorted(
            country_counts.items(), key=lambda x: x[1], reverse=True
        )
        formatted_response += f"\nTop Investment Countries:\n"
        for country, count in sorted_countries[:5]:
            percentage = (count / total_investors) * 100
            formatted_response += f"• {country}: {count} ({percentage:.1f}%)\n"

        # Cheque size info
        if cheque_data:
            formatted_response += f"\nCheque Size Data:\n"
            formatted_response += f"• Investors with cheque data: {len(cheque_data)}\n"
            formatted_response += f"• Percentage with cheque data: {(len(cheque_data) / total_investors) * 100:.1f}%\n"

        return formatted_response

    except Exception as e:
        return f"An error occurred while getting statistics: {e}"


@mcp.tool()
async def find_similar_investors(
    investor_name: str,
    limit: Optional[int] = None,
) -> str:
    """
    Find investors similar to a given investor based on type, stage, and location.
    Use this tool when a user wants to find investors similar to a specific one.

    Args:
        investor_name (str): Name of the investor to find similar ones for
        limit (Optional[int]): Maximum number of records to return

    Returns:
        str: Formatted string containing similar investor records
    """
    try:
        # First, find the target investor
        target_data = fetch_data_from_supabase(
            table_name="dec-2024",
            select_columns=[
                "Investor name",
                "Investor type",
                "Stage of investment",
                "Countries of investment",
                "Global HQ",
            ],
            filters={"Investor name": investor_name},
            limit=1,
        )

        if not target_data:
            return f"No investor found with name '{investor_name}'."

        target_investor = target_data[0]
        target_type = target_investor.get("Investor type")
        target_stage = target_investor.get("Stage of investment")
        target_countries = target_investor.get("Countries of investment")

        # Find similar investors
        similar_data = fetch_data_from_supabase(
            table_name="dec-2024",
            select_columns=[
                "Investor name",
                "Website",
                "Global HQ",
                "Countries of investment",
                "Stage of investment",
                "Investment thesis",
                "Investor type",
                "First cheque minimum",
                "First cheque maximum",
            ],
            limit=None,
        )

        if not similar_data:
            return "No investor data found."

        # Score and rank similar investors
        scored_investors = []
        for investor in similar_data:
            if investor.get("Investor name") == investor_name:
                continue  # Skip the target investor

            score = 0
            similarity_factors = []

            # Same investor type
            if investor.get("Investor type") == target_type:
                score += 3
                similarity_factors.append("same investor type")

            # Same investment stage
            if investor.get("Stage of investment") == target_stage:
                score += 2
                similarity_factors.append("same investment stage")

            # Same countries
            if investor.get("Countries of investment") == target_countries:
                score += 2
                similarity_factors.append("same investment countries")

            # Similar HQ location (simplified check)
            target_hq = target_investor.get("Global HQ", "")
            investor_hq = investor.get("Global HQ", "")
            if (
                target_hq
                and investor_hq
                and any(word in investor_hq for word in target_hq.split())
            ):
                score += 1
                similarity_factors.append("similar HQ location")

            if score > 0:
                scored_investors.append(
                    {
                        "investor": investor,
                        "score": score,
                        "factors": similarity_factors,
                    }
                )

        # Sort by score
        scored_investors.sort(key=lambda x: x["score"], reverse=True)

        if not scored_investors:
            return f"No similar investors found for '{investor_name}'."

        # Apply limit
        if limit:
            scored_investors = scored_investors[:limit]

        # Format response
        formatted_response = f"Similar investors to '{investor_name}':\n\n"

        for i, item in enumerate(scored_investors[:10], 1):  # Show top 10
            investor = item["investor"]
            score = item["score"]
            factors = item["factors"]

            formatted_response += f"{i}. {investor.get('Investor name', 'N/A')} (Similarity Score: {score})\n"
            formatted_response += f"   Website: {investor.get('Website', 'N/A')}\n"
            formatted_response += f"   Global HQ: {investor.get('Global HQ', 'N/A')}\n"
            formatted_response += (
                f"   Countries: {investor.get('Countries of investment', 'N/A')}\n"
            )
            formatted_response += (
                f"   Stage: {investor.get('Stage of investment', 'N/A')}\n"
            )
            formatted_response += f"   Type: {investor.get('Investor type', 'N/A')}\n"
            formatted_response += f"   First Cheque: {investor.get('First cheque minimum', 'N/A')} - {investor.get('First cheque maximum', 'N/A')}\n"
            formatted_response += f"   Similarity Factors: {', '.join(factors)}\n"
            thesis = investor.get("Investment thesis", "N/A")
            if len(thesis) > 100:
                thesis = thesis[:100] + "..."
            formatted_response += f"   Thesis: {thesis}\n"
            formatted_response += "-" * 80 + "\n\n"

        if len(scored_investors) > 10:
            formatted_response += (
                f"... and {len(scored_investors) - 10} more similar investors."
            )

        return formatted_response

    except Exception as e:
        return f"An error occurred while finding similar investors: {e}"


@mcp.resource("docs://vc_data_guide")
def get_vc_data_guide() -> str:
    """Provides guidance on interpreting VC investor data."""
    return """
    Understanding VC Investor Data:
    
    Investor Types:
    - Angel network: Individual investors who invest their own money
    - VC (Venture Capital): Professional investment firms
    - PE (Private Equity): Firms that invest in more mature companies
    - CVC (Corporate Venture Capital): Investment arms of large corporations
    
    Investment Stages:
    - Pre-seed: Very early stage, often just an idea
    - Seed: Early stage with some traction
    - Series A: First significant institutional round
    - Series B: Growth stage with proven business model
    - Series C+: Later stage funding for scaling
    - Growth: Large rounds for established companies
    
    First Cheque Ranges:
    - Indicate the typical investment size range for each investor
    - Useful for understanding if an investor fits your funding needs
    
    Investment Thesis:
    - Describes the investor's strategy and focus areas
    - Helps determine if there's a good fit for your startup
    """


@mcp.prompt()
def analyze_investor_data(investor_data: str) -> str:
    """
    Analyzes VC investor data and provides insights about the investment landscape.
    The input should be a string containing multiple investor records.
    """
    return f"""
    Analyze the following VC investor data and provide insights about the investment landscape.
    Consider:
    1. Geographic distribution of investors
    2. Investment stage preferences
    3. Typical investment sizes
    4. Investment thesis patterns
    5. Any notable trends or insights

    Investor data to analyze:
    ---
    {investor_data}
    ---

    Provide a structured analysis with key insights and trends.
    """


if __name__ == "__main__":
    # Use streamable HTTP transport with MCP endpoint
    print(f"VC Data Server running on http://localhost:{port}")
    print("MCP endpoint available at:")
    print(f"- http://localhost:{port}/mcp")

    mcp.run(transport="streamable-http")
