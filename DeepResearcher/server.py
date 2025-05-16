import asyncio  # Import the asyncio library for asynchronous programming
from mcp.server.fastmcp import FastMCP  # Import the FastMCP class from the mcp.server.fastmcp module
from agents import run_research  # Import the run_research function from the agents module

# Create FastMCP instance
mcp = FastMCP("crew_research")  # Instantiate FastMCP with the name "crew_research"

@mcp.tool()  # Register the following function as a tool with the FastMCP instance
async def crew_research(query: str) -> str:  # Define an asynchronous function that takes a query string and returns a string
    """Run CrewAI-based research system for given user query. Can do both standard and deep web search.

    Args:
        query (str): The research query or question.

    Returns:
        str: The research response from the CrewAI pipeline.
    """
    return run_research(query)  # Call the run_research function with the query and return its result


# Run the server
if __name__ == "__main__":  # Check if this script is being run directly (not imported)
    mcp.run(transport="stdio")  # Start the FastMCP server using standard input/output as the transport
