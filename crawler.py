import re
import requests
from bs4 import BeautifulSoup
import urlparse
from collections import OrderedDict
import Queue

BASE_URL = "https://en.wikipedia.org"
SEED_URLS = ["https://en.wikipedia.org/wiki/Time_zone", "https://en.wikipedia.org/wiki/Electric_car",
             "https://en.wikipedia.org/wiki/Carbon_footprint"]
# seed_dict = OrderedDict()


def is_redirected(next_url):
    return seed_dict.get(next_url)


def get_all_links(seed):
    page = requests.get(seed, allow_redirects=False)
    soup = BeautifulSoup(page.text, "html.parser")
    all_anchors = [all_a['href'] for all_p in soup.find_all('p') for all_a in all_p.find_all('a')]
    # filter out links containing '#' and ':'
    all_anchors = filter(lambda x: re.search('^/wiki/.+$', x), all_anchors)
    all_anchors = filter(lambda x: str('#') not in x or str(':') not in x, all_anchors)
    return all_anchors


for seed_url in SEED_URLS:
    seed_dict = OrderedDict()
    frontier = Queue.Queue()
    seed_dict[seed_url] = 1
    frontier.put(seed_url)
    depth = 2
    while (not frontier.empty() or depth <= 6):
        seed_url = frontier.get()
        all_links = get_all_links(seed_url)
        for link in all_links:
            link = urlparse.urljoin(BASE_URL, link)
            page = requests.get(link, allow_redirects=False)
            soup = BeautifulSoup(page.text, "html.parser")
            canonical_link = soup.find_all('link', attrs={"rel": "canonical"})
            next_url = canonical_link[0]['href']
            if (not is_redirected(next_url)):
                seed_dict[link] = depth
                frontier.put(link)
        depth = depth + 1

