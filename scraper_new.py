from bs4 import BeautifulSoup
import pandas as pd
import unicodedata
import itertools
import requests
import time
import re


def get_soup(url):
    """create a tree structure (BeautifulSoup) out of a get request's html """
    r = requests.get(url)
    return BeautifulSoup(r.content, "html5lib")

def scrape_talk_urls(conference_url):
    """retreive a list of urls for each talk in a bi-annual conference 
    
    Per session of conference there are generally 5-8 talks given and 
    around 5 sessions per conference
    """

    soup = get_soup(conference_url)

    a_tags = soup.find_all("a", {"class": "omeqik-0 cxIGgI list-tile listTile-3yP_N"})

    all_links = ["https://www.churchofjesuschrist.org" + a_tag.get('href') 
        for a_tag in a_tags 
        if re.search("^/study/general-conference/\d{4}/(04|10)/\d{1}", a_tag["href"])]

    return all_links

def scrape_talk_data(url):
    """scrapes a single talk for data such as: 
    
    title: name of the talk 
    conference: "April or October - <year>" 
    calling: speaker's calling in Church 
    speaker: name of the speaker 
    content: the text of the entire talk presented 

    It is possible for some of the urls to fail for multiple reasons. The specific 
    logic provided allows a majority of the data to come through without problems. 
    """
    try:
        soup = get_soup(url)

        title = soup.find("h1").text

        year = url.split('/')[6]
        month = url.split('/')[5] 

        conference = str(year) + "-" + str(month)

        speaker = soup.find('p', {"class": "author-name"}).text

        calling = soup.find('p', {"class": "author-role"}).text

        content_array = soup.find("div", {"class": "body-block"}).find_all("p")
     
        content = ""

        for paragraph in content_array:
            content = content + paragraph.text + "\n\n "


        return {
            "title": title,
            "speaker": speaker,
            "calling": calling,
            "conference": conference,
            "url": url,
            "talk": content,
        }
    except Exception as e:
        print(f"\n\n\nURL: {url} FAILED")
        print(f"Exception: {e}\n\n\n")
        return dict()


# create all permutations of urls from 1971-2018
#   landing pages for a bi-annual session of conference always follow the same structure:
#   https://www.lds.org/general-conference/<year>/<month>?lang=eng
urls = [f"https://www.churchofjesuschrist.org/general-conference/{year}/{month}?lang=eng"
        # for year in range(1971, 2020)
        # for month in ["04", "10"]]
        for year in range(2021)
        for month in ["10"]]

urls = [f"https://www.churchofjesuschrist.org/general-conference/2021/10?lang=eng"]

start = time.time()

# create a list of all the urls for every talk 
all_urls = [scrape_talk_urls(url) for url in urls]

all_urls = list(itertools.chain(*all_urls)) # flatten into single list from a list of lists
print(len(all_urls))  # validate total number of urls

conference_talks = []
for i, url in enumerate(all_urls):
    print(f"Talk number {i+1}")
    conference_talks.append(scrape_talk_data(url))

conference_df = pd.DataFrame(conference_talks)

# simple cleaning
for col in conference_df.columns:
    conference_df[col] = conference_df[col].apply(lambda x: unicodedata.normalize("NFD", x) if pd.notnull(x) else x)
    # conference_df[col] = conference_df[col].apply(lambda x: x.replace("\n", "") if pd.notnull(x) else x)
    conference_df[col] = conference_df[col].apply(lambda x: x.replace("\t", "") if pd.notnull(x) else x)
    print(conference_df[col])

print(conference_df)
# finish
conference_df.to_csv("conference_talks_2021.csv", index=False)

end = time.time()
print(end - start)




