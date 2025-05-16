import os  # Import the os module for interacting with the operating system (e.g., environment variables)
from typing import Type  # Import Type for type hinting generic classes
from dotenv import load_dotenv  # Import load_dotenv to load environment variables from a .env file
from pydantic import BaseModel, Field  # Import BaseModel and Field for data validation and schema definition
from linkup import LinkupClient  # Import LinkupClient to interact with the LinkUp search API
from crewai import Agent, Task, Crew, Process, LLM  # Import core classes from the crewai framework
from crewai.tools import BaseTool  # Import BaseTool to create custom tools for agents

# Load environment variables (for non-LinkUp settings)
load_dotenv()  # Loads environment variables from a .env file into the process environment

def get_llm_client():
    """Initialize and return the LLM client"""
    return LLM(
        model="ollama/deepseek-r1:7b",  # Specify the model to use for the LLM
        base_url="http://localhost:11434"  # Specify the base URL for the LLM API
    )

# Define LinkUp Search Tool

class LinkUpSearchInput(BaseModel):
    """Input schema for LinkUp Search Tool."""
    query: str = Field(description="The search query to perform")  # The search query string
    depth: str = Field(default="standard",
                       description="Depth of search: 'standard' or 'deep'")  # Search depth option
    output_type: str = Field(
        default="searchResults", description="Output type: 'searchResults', 'sourcedAnswer', or 'structured'")  # Output format

class LinkUpSearchTool(BaseTool):
    name: str = "LinkUp Search"  # Name of the tool
    description: str = "Search the web for information using LinkUp and return comprehensive results"  # Tool description
    args_schema: Type[BaseModel] = LinkUpSearchInput  # Input schema for the tool

    def __init__(self):
        super().__init__()  # Initialize the parent BaseTool class

    def _run(self, query: str, depth: str = "standard", output_type: str = "searchResults") -> str:
        """Execute LinkUp search and return results."""
        try:
            # Initialize LinkUp client with API key from environment variables
            linkup_client = LinkupClient(api_key=os.getenv("LINKUP_API_KEY"))

            # Perform search
            search_response = linkup_client.search(
                query=query,  # The search query
                depth=depth,  # The depth of the search
                output_type=output_type  # The output format
            )

            return str(search_response)  # Return the search results as a string
        except Exception as e:
            return f"Error occurred while searching: {str(e)}"  # Return error message if search fails

def create_research_crew(query: str):
    """Create and configure the research crew with all agents and tasks"""
    # Initialize tools
    linkup_search_tool = LinkUpSearchTool()  # Create an instance of the LinkUp search tool

    # Get LLM client
    client = get_llm_client()  # Initialize the LLM client

    web_searcher = Agent(
        role="Web Searcher",  # Role name
        goal="Find the most relevant information on the web, along with source links (urls).",  # Agent's goal
        backstory="An expert at formulating search queries and retrieving relevant information. Passes the results to the 'Research Analyst' only.",  # Agent's background
        verbose=True,  # Enable verbose output for debugging
        allow_delegation=True,  # Allow this agent to delegate tasks
        tools=[linkup_search_tool],  # Assign the LinkUp search tool to this agent
        llm=client,  # Assign the LLM client to this agent
    )

    # Define the research analyst
    research_analyst = Agent(
        role="Research Analyst",  # Role name
        goal="Analyze and synthesize raw information into structured insights, along with source links (urls) as citations.",  # Agent's goal
        backstory="An expert at analyzing information, identifying patterns, and extracting key insights. If required, can delagate the task of fact checking/verification to 'Web Searcher' only. Passes the final results to the 'Technical Writer' only.",  # Agent's background
        verbose=True,  # Enable verbose output
        allow_delegation=True,  # Allow this agent to delegate tasks
        llm=client,  # Assign the LLM client
    )

    # Define the technical writer
    technical_writer = Agent(
        role="Technical Writer",  # Role name
        goal="Create well-structured, clear, and comprehensive responses in markdown format, with citations/source links (urls).",  # Agent's goal
        backstory="An expert at communicating complex information in an accessible way.",  # Agent's background
        verbose=True,  # Enable verbose output
        allow_delegation=False,  # Do not allow this agent to delegate tasks
        llm=client,  # Assign the LLM client
    )

    # Define tasks
    search_task = Task(
        description=f"Search for comprehensive information about: {query}.",  # Task description
        agent=web_searcher,  # Assign the web_searcher agent to this task
        expected_output="Detailed raw search results including sources (urls).",  # Expected output from this task
        tools=[linkup_search_tool]  # Tools available for this task
    )

    analysis_task = Task(
        description="Analyze the raw search results, identify key information, verify facts and prepare a structured analysis.",  # Task description
        agent=research_analyst,  # Assign the research_analyst agent
        expected_output="A structured analysis of the information with verified facts and key insights, along with source links",  # Expected output
        context=[search_task]  # This task depends on the output of search_task
    )

    writing_task = Task(
        description="Create a comprehensive, well-organized response based on the research analysis.",  # Task description
        agent=technical_writer,  # Assign the technical_writer agent
        expected_output="A clear, comprehensive response that directly answers the query with proper citations/source links (urls).",  # Expected output
        context=[analysis_task]  # This task depends on the output of analysis_task
    )

    # Create the crew
    crew = Crew(
        agents=[web_searcher, research_analyst, technical_writer],  # List of all agents in the crew
        tasks=[search_task, analysis_task, writing_task],  # List of all tasks to be performed
        verbose=True,  # Enable verbose output for the crew
        process=Process.sequential  # Specify that tasks should be executed sequentially
    )

    return crew  # Return the configured crew

def run_research(query: str):
    """Run the research process and return results"""
    try:
        crew = create_research_crew(query)  # Create the research crew for the given query
        result = crew.kickoff()  # Start the research process and get the result
        return result.raw  # Return the raw result from the crew
    except Exception as e:
        return f"Error: {str(e)}"  # Return error message if something goes wrong
