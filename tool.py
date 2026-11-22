from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv
load_dotenv()


tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query:str) -> str:
    '''Search the web for recent and reliable information on a topic. Returns Titles , urls and snippets.'''
    results = tavily.search(query=query,max_results=5)

    out = []

    for result in results['results']:
        title = result['title']
        url = result['url']
        snippet = result['content']
        out.append(f'title:{title}\n url: {url} \n snippet: {snippet}\n')

        return "\n".join(out)

# print(web_search.invoke("What is the latest news on AI from times of India?"))

@tool
def web_scrapper(url:str)->str :
    '''Scrape the web and return clean text from the given url for clean reading '''
    res = requests.get(url , timeout=10 ,headers={"User-Agent" : "Mozilla/5.0"})
    soup = BeautifulSoup(res.content , 'html.parser')
    for tag in soup(['script' , 'style' , 'header' , 'footer']):
        tag.decompose()
    return soup.get_text(separator=" ", strip =True)[:3000]    

# print(web_scrapper.invoke("https://en.wikipedia.org/wiki/Wikipedia"))
