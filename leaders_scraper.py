from ast import Dict, List, Str
import requests
from bs4 import BeautifulSoup
import re
import json
from pprint import pprint


# Function to scrape leaders data from a website and process it
def get_leaders():
    """_summary_
    Function to requests all leaders of countries available in the database

    Returns:
        _type_: _description_
        return a dictionnary of the different leaders information per country with wikipedia URL
    """
    root_url = "https://country-leaders.onrender.com"
    cookie_url = "/cookie"
    countries_url, leaders_url = "/countries", "/leaders"
    cookies = requests.get(f"{root_url}{cookie_url}").cookies
    countries = requests.get(f"{root_url}{countries_url}", cookies=cookies).json()
    leader_per_country = {}

    with requests.Session() as session:
        for country in countries:
            try:
                response = requests.get(f"{root_url}{leaders_url}", cookies=cookies, params={"country": country})
                if response.status_code == 403:  # Forbidden --> cookie issues
                    print(f"Cookie expired. Getting new cookies for country {country}.")
                    cookies = requests.get(f"{root_url}{cookie_url}").cookies
                    response = requests.get(f"{root_url}{leaders_url}", cookies=cookies, params={"country": country})
                leaders = response.json()
                for leader in leaders:
                    wikipedia_url = leader.get('wikipedia_url')
                    if wikipedia_url:
                        first_paragraph = get_first_paragraph(wikipedia_url, session)
                        leader['first_paragraph'] = first_paragraph
                leader_per_country[country] = leaders
            except requests.exceptions.RequestException as e:
                print(f"Request failed for country {country}: {e}")
                leader_per_country[country] = []

    return leader_per_country

# Function for the sqcraping of the first paragraph from Wikipedia
def get_first_paragraph(wikipedia_url: str, session) -> str:
    """_summary_
    In this function = request of each wikipedia URL for the different leaders and return the first paragraph
    cleaned of wikipedia description

    Args:
        wikipedia_url (_type_): _description_
        session (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        wiki_data = session.get(wikipedia_url).text
        soup = BeautifulSoup(wiki_data, 'html.parser')
        first_paragraph = next(paragraph.text for paragraph in soup.find("table", attrs={"class": "infobox"}).find_next_siblings("p"))
        paragraph_clean = re.sub(r' \[.*?\]\[.*?\]|\([^)]*Écouter\)|\ Écouter|\[\w]', '', first_paragraph)
        paragraph_clean = re.sub(r'\s+,', ',', paragraph_clean)
        return paragraph_clean
    except Exception as e:
        print(f"Error fetching first paragraph from {wikipedia_url}: {e}")
        return ""


# Function to save data to a JSON file
def save(data, file_path):
    """_summary_
    Save into a json file
    Args:
        data (_type_): _description_
        file_path (_type_): _description_
    """
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {file_path}")

if __name__ == "__main__":
    # Fetch leaders data
    leader_per_country = get_leaders()

    # Save data to JSON file
    save(leader_per_country, 'leaders.json')
    print("leaders_per_country")

