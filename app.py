import streamlit as st
import os
import time
import json
import requests
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai.like import OpenAILike
from agno.tools.duckduckgo import DuckDuckGoTools

# Load environment variables
load_dotenv()

# Add current date information to query
def add_date_to_query(query):
    current_date = time.strftime("%Y-%m-%d")
    enhanced_query = f"{query}\n\nToday's date is {current_date}. Please provide the most up-to-date information available."
    return enhanced_query

# Search for recent information using DuckDuckGo
def search_with_duckduckgo(query, num_results=5, max_retries=2):
    try:
        # Import the search function
        from duckduckgo_search import DDGS
        
        # Create a new DDGS instance with a timeout and proxies
        ddgs = DDGS(timeout=20)
        
        # Add retry logic
        for attempt in range(max_retries):
            try:
                # Search for the query
                results = list(ddgs.text(query, max_results=num_results))
                
                # If we got results, return them
                if results and len(results) > 0:
                    return results
                
                # If no results but no error, wait and retry
                time.sleep(2)  # Wait 2 seconds before retrying
            except Exception as inner_e:
                # If this is the last attempt, raise the error
                if attempt == max_retries - 1:
                    raise inner_e
                
                # Otherwise wait longer and retry
                time.sleep(3)
        
        # If we got here with no results, return empty list
        return []
    except Exception as e:
        st.error(f"Error searching with DuckDuckGo: {str(e)}")
        return None

# Create AI agent with tools
@st.cache_resource
def create_agent():
    try:
        # Initialize the Agent with Sutra model via OpenAILike wrapper
        agent = Agent(
            model=OpenAILike(
                id="sutra-v2",
                api_key=os.getenv("SUTRA_API_KEY"),
                base_url="https://api.two.ai/v2"
            ),
            markdown=True
        )
        
        # Create the agent with the model
        return agent
    except Exception as e:
        st.error(f"Failed to create agent: {str(e)}")
        return None

# Sample questions for news summarization
SAMPLE_QUESTIONS = [
    "Summarize the latest global economic news in Hindi",
    "What are the recent tech industry developments? Respond in French.",
    "Summarize today's top sports headlines in German"
]

# Render sidebar content
def render_sidebar():
    with st.sidebar:
        # Add Sutra logo
        st.image("https://framerusercontent.com/images/3Ca34Pogzn9I3a7uTsNSlfs9Bdk.png", use_column_width=True)
        st.header("Multilingual News Summarizer")
        st.divider()
        
        # API Key input
        st.markdown("🔑 Get your API key from [Two AI Sutra](https://www.two.ai/sutra/api)")
        sutra_api_key = st.text_input("Enter your SUTRA API Key", 
                                    value="", 
                                    type="password",
                                    key="sutra_api_key")
        
        if sutra_api_key:
            # Update the environment variable
            os.environ["SUTRA_API_KEY"] = sutra_api_key
        else:
            st.sidebar.warning("Please enter your Sutra API key to use the app")
            
        # Search Settings
        st.markdown("#### Search Settings")
        use_search = st.checkbox("Use DuckDuckGo search for recent information", value=True, key="use_search")
        
        st.divider()
        
        st.markdown("#### About")
        st.markdown("""
        AI-powered news summarization in multiple languages:
        - Global news
        - Business and finance
        - Technology
        - Sports
        - Politics
        - Entertainment
        - Science and health
        """)
        
        st.markdown("---")
        st.markdown("#### Settings")
        show_tool_calls = st.checkbox("Show tool calls", value=True, key="show_tool_calls")
        return show_tool_calls, st.session_state.use_search

# Main app
def main():
    # Page config
    st.set_page_config(
        page_title="Multilingual News Summarizer",
        page_icon="🇰"
    )
    
    # No custom styling needed
    
    # Render sidebar
    show_tool_calls, use_search = render_sidebar()
    
    # Main content
    st.markdown(
        '<h1><img src="https://framerusercontent.com/images/9vH8BcjXKRcC5OrSfkohhSyDgX0.png" width="60"/> SUTRA Multilingual News Summarizer</h1>',
        unsafe_allow_html=True
    )
    
    st.markdown("Get AI-powered news summaries in multiple languages using Agno's advanced capabilities.")
    
    # Initialize agent
    if "sutra_api_key" not in st.session_state or not st.session_state.sutra_api_key:
        st.warning("Please enter your Sutra API key in the sidebar to continue.")
        agent = None
        return
    else:
        agent = create_agent()
        if not agent:
            st.error("Failed to initialize the AI agent. Please check your API key.")
            return
    
    # Input form
    with st.form("query_form"):
        query = st.text_area(
            "What news would you like summarized? You can specify a language for the response.", 
            height=100, 
            placeholder="e.g., Summarize today's top business news in French.",
            key="query_input"
        )
        submit = st.form_submit_button("Get Summary", use_container_width=True)
    
    # Sample questions
    st.subheader("Sample questions")
    for i, question in enumerate(SAMPLE_QUESTIONS):
        if st.button(question, key=f"sample_{i}"):
            query = question
            submit = True
    
    # Handle submission
    if submit and query.strip():
        st.subheader("🌐 News Summary")
        
        # Create a placeholder for the streaming output
        response_container = st.empty()
        
        # Configure the agent
        agent.show_tool_calls = show_tool_calls
        
        # Initialize or reset the response in session state
        if "response" not in st.session_state or submit:
            st.session_state.response = ""
        
        # If a response is being generated, show a single processing spinner
        if "full_response" not in st.session_state or submit:
            # Reset full_response if this is a new submission
            if submit:
                st.session_state.pop("full_response", None)
                
            # Single spinner for all processing
            with st.spinner("Processing your request..."):
                # Get recent information if enabled
                if use_search:
                    # Show debug info
                    st.info(f"Searching for recent information about: {query}")
                    
                    try:
                        # Use DuckDuckGo search with retry logic
                        search_results = search_with_duckduckgo(query, max_retries=2)
                        
                        if search_results and len(search_results) > 0:
                            # Show success message
                            st.success(f"Found {len(search_results)} recent results from DuckDuckGo")
                            
                            # Extract relevant information from search results
                            recent_info = "\n\nRecent information from search results:\n"
                            
                            for idx, result in enumerate(search_results[:3]):
                                recent_info += f"\n{idx+1}. {result.get('title', '')}: {result.get('body', '')}\n"
                                
                            # Append recent information to the query
                            enhanced_query = f"{query}\n\nUse this recent information to provide an up-to-date response: {recent_info}\n\nToday's date is {time.strftime('%Y-%m-%d')}"
                            st.session_state.full_response = agent.run(enhanced_query, stream=False)
                        else:
                            # Fallback: Just add date information
                            st.warning("Could not retrieve recent information from DuckDuckGo. Using date-enhanced query.")
                            date_enhanced_query = add_date_to_query(query)
                            st.session_state.full_response = agent.run(date_enhanced_query, stream=False)
                    except Exception as e:
                        # Handle any unexpected errors
                        st.error(f"Error during search: {str(e)}")
                        # Fallback: Just add date information
                        st.warning("Using date-enhanced query as fallback.")
                        date_enhanced_query = add_date_to_query(query)
                        st.session_state.full_response = agent.run(date_enhanced_query, stream=False)
                else:
                    # No search enabled - just run with original query
                    st.session_state.full_response = agent.run(query, stream=False)
                
                # Get the response from the agent
                response = st.session_state.full_response
                
                # Extract only the content from the RunResponse object
                if hasattr(response, 'content'):
                    # If it's a RunResponse object with content attribute
                    clean_content = response.content
                else:
                    # Fallback to string representation but clean it up
                    response_str = str(response)
                    # Try to extract just the content part if it's a RunResponse string representation
                    if "RunResponse(content='" in response_str:
                        try:
                            # Extract content between the first single quotes after content=
                            start_idx = response_str.find("content='") + 9
                            end_idx = response_str.find("'", start_idx)
                            clean_content = response_str[start_idx:end_idx]
                        except:
                            clean_content = response_str
                    else:
                        clean_content = response_str
                
                # Format the content based on its structure
                if '1.' in clean_content and '2.' in clean_content:
                    # It's likely a numbered list, keep the formatting
                    response_container.markdown(clean_content)
                else:
                    # For regular text, add some paragraph spacing
                    paragraphs = clean_content.split('\n\n')
                    formatted_content = '\n\n'.join([f"<p>{p}</p>" for p in paragraphs])
                    response_container.markdown(formatted_content, unsafe_allow_html=True)
                
                # Store for display
                st.session_state.response = clean_content
                

        
    # Simple action button
    if st.button("New Query"):
        st.session_state.response = ""
        st.session_state.full_response = ""
        st.experimental_rerun()
    
    elif submit and not query.strip():
        st.warning("Please enter a valid question.")

if __name__ == "__main__":
    main()
