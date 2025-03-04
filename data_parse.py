import trafilatura, requests, re, ai_call
from random import randrange

class random_agents():  
        user_agents = ["Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0",
        "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
        "Dalvik/2.1.0 (Linux; U; Android 9; ADT-2 Build/PTT5.181126.002"]
        
        def change_agents():
            agent_index = randrange(0, len(random_agents.user_agents))
            return {f'user-agent': f'{random_agents.user_agents[agent_index]}'}
        
def get_req(url):
    try:
        return requests.get(url, headers=random_agents.change_agents(), timeout=5, verify=True).text
    except Exception as e:
        print(f'Error in scraping {url} due to {e}\n')
        return
    
def web_extract(web_url): # Make external calls to this function
    try:
        downloaded = get_req(web_url)
        result = traf_func(downloaded)
        result_parse(result)
        ai_call.build_call('system', f'Ingest this text for analysis: {ai_call.listed_items.scraped_data}')
    except Exception as e:
        print(f'Error scraping {web_url} due to {e}\n')
    return

def result_parse(result):
    cut_list = []
    for i in result:
        i = i.lower()
        if 'url:' in i or 'date:' in i:
            cut_list.append(f'{i} ')
        elif 'https://' in i:
            i = i.replace('[', '').replace(']', '').replace(')', '').replace('(', '').replace('→', '')
            cut_list.append(f'{i} ')
        else:
            i = re.sub(r'[^\w\s]', '', i) # Uses regex to clean data of any punctuation
            cut_list.append(f'{i} ')
    ai_call.listed_items.scraped_data.append(''.join(cut_list))
    return

def traf_func(downloaded):
    return trafilatura.extract(downloaded, with_metadata=True, deduplicate=True, include_tables=True, include_comments=True, include_links=True).split('\n')