import streamlit as st
from crewai import Agent, Task, Crew
from bs4 import BeautifulSoup
import requests

# Helper functions
def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching URL: {e}"

def parse_html(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string if soup.title else "No Title"
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag['content'] if description_tag and 'content' in description_tag.attrs else "No Description"
        links = [a['href'] for a in soup.find_all('a', href=True)]
        text = soup.get_text(separator=' ', strip=True)
        return {
            "title": title,
            "description": description,
            "links": links,
            "text": text[:1000]  # Truncate for readability
        }
    except Exception as e:
        return {"error": f"Error parsing HTML: {e}"}

def format_data(data):
    if "error" in data:
        return data
    return {
        "Page Title": data["title"],
        "Meta Description": data["description"],
        "Links Found": data["links"],
        "Page Text (truncated)": data["text"]
    }

# Define agents
crawler_agent = Agent(name="Crawler Agent", role="Fetches HTML content from the URL")
parser_agent = Agent(name="Parser Agent", role="Extracts meaningful content from HTML")
formatter_agent = Agent(name="Formatter Agent", role="Formats extracted data for display")

# Define tasks
def create_tasks(url):
    html_content = fetch_html(url)
    parsed_data = parse_html(html_content)
    formatted_output = format_data(parsed_data)

    crawler_task = Task(agent=crawler_agent, description="Fetched HTML content.")
    parser_task = Task(agent=parser_agent, description="Parsed HTML content.")
    formatter_task = Task(agent=formatter_agent, description="Formatted parsed data.")

    return formatted_output, [crawler_task, parser_task, formatter_task]

# Streamlit UI
st.title("Agentic Web Crawler with CrewAI")
url = st.text_input("Enter a URL to crawl")

if url:
    with st.spinner("Crawling and processing..."):
        result, tasks = create_tasks(url)
        crew = Crew(agents=[crawler_agent, parser_agent, formatter_agent], tasks=tasks)
        crew.run()
        st.subheader("Extracted Information")
        st.json(result)
