from random import randrange
from datetime import datetime
import requests, trafilatura, re, os, time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
"""
https://github.com/proxifly/free-proxy-list/tree/main?tab=readme-ov-file
{datetime.today().strftime('%Y_%m_%d')}
"""

class SourceMeta: # This class is used to store objects in dictionaries specific to individual websites - These are called in the NetOps class
    cisa_advise = {'url_strings': ['news-events/alerts', 'news-events/ics-advisories/', '/news-events/analysis-reports'], 
                     'base_url': 'https://www.cisa.gov/news-events/cybersecurity-advisories?page=',
                     'url_prefix': 'https://www.cisa.gov',
                     'home_dir': 'cisa_advisories',
                     'filename_re': 4,
                     'log_name' : 'cisa_'
    }
    
    bleeping_comp = {'url_strings': ['/tutorials/', '/news/', '/virus-removal/', '/guides/'], #The website puts old articles embedded with new ones, so you will see a lot of 'File Already Exists' messages
                     'base_url': 'https://www.bleepingcomputer.com/page/',
                     'url_prefix': 'https://bleepingcomputer.com',
                     'home_dir': 'bleeping_computer',
                     'filename_re': 3,
                     'log_name' : 'bleeping_'
    }
    
    the_register = {'url_strings': ['/2025/', '/2024/'], # NEEDS ATTENTION Uses the days date in MM/DD numeric format eg /2025/04/07/asia_tech_news_in_brief/ - use date substraction equation from wayback downloader script
                     'base_url': 'https://www.theregister.com/earlier/',
                     'url_prefix': 'https://www.theregister.com',
                     'home_dir': 'the_register',
                     'filename_re': 5,
                     'log_name' : 'register_'
    }
    
    dark_reading = {'url_strings': ['/cyberattacks-data-breaches/', '/threat-intelligence/', '/vulnerabilities-threats/', '/cloud-security/', # These fuckers....
                                    '/endpoint-security/', '/cybersecurity-operations/', 'application-security'], 
                     'base_url': 'https://www.darkreading.com/latest-news?page=',
                     'url_prefix': 'https://www.darkreading.com/',
                     'home_dir': 'dark_reading',
                     'filename_re': 4,
                     'log_name' : 'dark_'
    }
    
    tenable_cves = {'url_strings': ['.com/cve/CVE-'], 
                     'base_url': 'https://www.tenable.com/cve/newest?page=',
                     'url_prefix': 'https://www.tenable.com/',
                     'home_dir': 'tenable_cves',
                     'filename_re': 1,
                     'log_name' : 'tenable_'
    }
    
    talos_intel_vuln = {'url_strings': ['/vulnerability_reports/TALOS'],
                     'base_url': 'https://talosintelligence.com/vulnerability_reports/',
                     'url_prefix': 'https://talosintelligence.com',
                     'home_dir': 'talos_intel_vuln',
                     'filename_re': 1,
                     'log_name' : 'talos_vuln'
    }

    talos_intel = {'url_strings': ['-'], # Add spesh code for this source
                     'base_url': 'https://blog.talosintelligence.com/page/',
                     'url_prefix': 'https://blog.talosintelligence.com',
                     'home_dir': 'talos_intel',
                     'filename_re': 2,
                     'log_name' : 'talos_'
    }
    
    nsa_advise = {'url_strings': ['https://media.defense.gov/'], # These are all PDFs. Make a PDF scraper.
                     'base_url': 'https://www.nsa.gov/Press-Room/Cybersecurity-Advisories-Guidance/smdpage16681/',
                     'url_prefix': 'https://www.nsa.gov',
                     'home_dir': 'nsa_advise',
                     'filename_re': 1,
                     'log_name' : 'nsa_'
    }
    
    data_breach = {'url_strings': ['/2025/', '/2024/'], 
                     'base_url': 'https://www.databreachtoday.com/latest-news/p-',
                     'url_prefix': 'https://www.databreachtoday.com/',
                     'home_dir': 'databreach_today',
                     'filename_re': 1,
                     'log_name' : 'databreach_'
    }

    fbi_advise = {'url_strings': ['/contact-us/'], # Needs to use selenium as well, does not use PDFs
                    'base_url': 'https://www.fbi.gov/investigate/cyber/news',
                    'url_prefix': 'https://fbi.gov/contact-us/field-offices/',
                    'home_dir': 'fbi_advise',
                    'filename_re': 3,
                    'log_name' : 'fbi_'
    }
    
    regex_patterns = {
                     'general_url' : r'href="([^"]*)"',
                     'alt_url' : r'<a\s+href=["\'](.*?)["\']', # Works with talos_intel_vuln and talos_intel
                     'pdf_url' : r'(?:http\:|https\:)?\/\/.*\.(?:pdf)',
                     'pic_url' : r'(?:http\:|https\:)?\/\/.*\.(?:png|jpg|tiff|bmp|jpeg|gif)',
                     'punc_dedup' : r'[\.\?\!]{2,}',
                     'punc_aggresive' : r'[^\w\s]',
                     'databreach_reg' : r"https://www\.databreachtoday\.com/[a-zA-Z0-9-]+-(?:c|a)-\d+(?!(\.jpg|\.jpeg|\.png|\.gif))",
                     'talos_reg' : r'www.\.talosintelligence\.com/[\w-]+/(?!.*\.(jpg|jpeg|png|gif)$)',
                     'fbi_reg' : r'www.\.fbi\.gov/[\w-]+/(?!.*\.(jpg|jpeg|png|gif)$)'
    }
    
class GetParams():
        
    def __init__(self): # Pick random agents for get request
        self.user_agents = [
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.3',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.10 Safari/605.1.1',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.3',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.3']
        self.http_proxy_list = []
        self.https_proxy_list = []
        self.headers = None
    
    def change_agents(self):
        agent_index = randrange(0, len(self.user_agents))
        self.headers = {"user-agent": f"{self.user_agents[agent_index]}"}
        """self.headers = {
        'referer': 'https://www.fbi.gov',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        "user-agent": f"{self.user_agents[agent_index]}",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8'
        }"""
        return self.headers
    
    def get_http_prox(self): # Pulls from an actively maintained proxy list and selects random proxy servers to for get request in the NetOps class
        resp = requests.get('https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.txt', verify=True).text.split('\n')
        for i in range(0,101):
            index = randrange(0, len(resp))
            self.http_proxy_list.append(resp[index])
        system_ops.logging('New HTTP proxy list generated')
        self.get_https_prox()
        return
    
    def get_https_prox(self): # Pulls from same source as above function, except it's a much shorter list for HTTPS proxies
        resp = requests.get('https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/https/data.txt', verify=True).text.split('\n')
        for i in range(0, len(resp)):
            index = randrange(0, len(resp))
            self.https_proxy_list.append(resp[index])
        system_ops.logging('New HTTPS proxy list generated')
        return
    
    def build_proxy_obj(self): # Builds proxy object to be used in GET requests in the NetOps class
        http_proxy_index = randrange(0, len(self.http_proxy_list))
        https_proxy_index = randrange(0, len(self.https_proxy_list))
        proxies = {
            'http' : self.http_proxy_list[http_proxy_index],
            #'https': self.https_proxy_list[https_proxy_index]
        }
        system_ops.logging(f'{get_params.http_proxy_list[http_proxy_index]} & {get_params.https_proxy_list[https_proxy_index]}')
        return proxies

class NetOps():

    def __init__(self, source, urlpat):
        self.urlpat = urlpat
        self.flat_data = None
        self.page_urls = []
        self.file_name = None
        self.page_num = 1
        self.source = source
        self.static_url = []

    def get_resp(self, url):
        try:
            if SourceMeta.bleeping_comp["base_url"] in url:
                url = f'{url}/'
            system_ops.logging(f'GET request sent to {url}')
            return requests.get(url, verify=True, timeout=10, proxies=get_params.build_proxy_obj(), headers=get_params.change_agents())
        except Exception as e:
            system_ops.logging(f'Error with GET request to {url}: {e}')
    
    def traf_func(self, downloaded):
        try:
            return trafilatura.extract(downloaded, with_metadata=True, deduplicate=True, include_tables=True, include_comments=True, include_links=False).split('\n')
        except Exception as e:
            system_ops.logging(f'Error with response object: {e}')
        
    def iterator(self):
        for i in range(0,5): # It all starts here dawg
            try:
                time.sleep(1)
                if self.source["home_dir"] == 'talos_intel_vuln':
                    main_page = self.get_resp(f'{self.source["base_url"]}')
                elif self.source["home_dir"] == 'fbi_advise':
                    main_page = self.get_resp(f'{self.source["base_url"]}')  
                else:
                    main_page = self.get_resp(f'{self.source["base_url"]}{str(self.page_num)}') # Concatenates base url and incrementally increasing page number
                system_ops.logging(f'Status Code: {main_page.status_code}')
                self.page_num=self.page_num+1
                self.url_rip(main_page.text)
            except Exception as e:
                system_ops.logging(f'Error with stuff: {e}')
                self.purgatory()
                continue
        return
    
    def url_rip(self, main_page):
        for m in re.findall(self.urlpat, main_page): # Add if else condition for regex url matches that already have the base url
            if m in self.static_url:
                continue
            elif self.source["home_dir"] == 'talos_intel' and 'https://' in m:
                continue
            for i in self.source["url_strings"]:
                if i in m:
                    self.static_url.append(m)
                    if 'https://' in m: # For urls that are in html code that already have the domain in place, this prevents duplicate concatenation
                        m = f'{m}'
                    else:
                        m = f'{self.source["url_prefix"]}{m}'
                    self.page_urls.append(m)
                else:
                    continue
        system_ops.logging(f'{len(self.page_urls)} Articles Extracted')
        self.url_iterator()
        return
        
    def url_iterator(self):
        for j in self.page_urls:
            self.file_name = system_ops.filename_creator(j, self.source["filename_re"])
            if system_ops.file_check():
                system_ops.logging(f'{self.file_name} - File already exists')
                continue
            time.sleep(2.5)
            system_ops.logging(j)
            article = self.get_resp(j)
            extracted_article = self.traf_func(article.text)
            if article.status_code == 404:
                system_ops.logging(f'{j} Responded with 404 error.')
                continue
            self.result_parse(extracted_article)
        self.page_urls.clear() # Clear scraped urls object for next iteration
        return
    
    def result_parse(self, result):
        tenable = False
        clean_data = []
        for i in result:
            i = i.strip() # Add .lower() method to remove capitaliztion, however current LLM documentation states keeping caps is useful to establish context and acronyms for RAG
            if 'url: https://www.tenable.com/cve' in i: # if statement sets tenable condition to True to prevent duplication in text files for Tenable
                tenable = True
            elif 'date:' in i:
                clean_data.append(f'{i}')
            elif "---" in i: # Consider removal or specifying CISA Advisories
                continue
            elif tenable == True and 'description:' in i:
                continue
            else:
                i = i.replace('®', '').replace('©', '').replace('™', '').replace('—', '').replace('—', '').replace('-', '').replace('- ', '')
                i = re.sub(SourceMeta.regex_patterns["punc_dedup"], '', i) # Uses regex to clean data of any punctuation
                clean_data.append(f'{i}')
        self.flat_data = '\n'.join(clean_data).strip() # Join all items in list with a newline separator to give LLM more context
        system_ops.file_writer(self.flat_data)
        return
    
    def get_file(self, file_url): # Pulls PDF files and downloads them to pdf_temp directory
        response = net_ops.get_resp(file_url)
        file_name = file_url.split('/')[-1]
        file_path = os.path.join(f'{os.getcwd()}/pdf_temp/', file_name)
        with open(f'{file_path}', 'wb') as file:
            file.write(response.content) #writes data from request to actual picture file
        return
    
    def purgatory(self): # Resets proxy list and waits a bit when connections get squirrely
        system_ops.logging('Sitting in purgatory for 2 minutes... :(')
        get_params.get_http_prox()
        system_ops.logging('Refreshed proxy list...')
        time.sleep(120)
        system_ops.logging('Time to go back to work.')
        self.page_num = self.page_num-1
        return
    
    def selenium(self, url):
        options = Options()
        options.add_argument("--window-size=`120,120`")
        driver = webdriver.Firefox(options=options)
        return driver.get(url)

class SystemOps():

    def __init__(self):
        pass

    def filename_creator(self, url, space):
        url = url.split('/')[-space:]
        return '_'.join(url).strip('_')

    def file_writer(self, clean_data): # Write that shit to a txt file for future embedding and vectorizing operations
        self.dir_check()
        with open(f'{os.getcwd()}/source_files/{self.get_date()}/{net_ops.file_name}.txt', 'w', encoding='utf-8') as file:
            file.write(clean_data)
        self.logging(f'{net_ops.file_name} processing completed.')
        return
    
    def dir_check(self):
        if not os.path.exists(f'source_files/{self.get_date()}'):
            os.makedirs(f'source_files/{self.get_date()}')
            self.logging(f'Directory created: /{self.get_date()}')
        else:
            pass
        return
    
    def file_check(self): # Picks back up where you left off if scraping is interrupted
        file_list = []
        for (root, dirs, file) in os.walk(f'{os.getcwd()}/source_files'):
            for f in file:
                if '.txt' in f:
                    file_list.append(f'{root}/{f}')
        for m in file_list:
            if net_ops.file_name in m:
                return True
        return False

    def get_time(self):
        return datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    
    def get_date(self):
        return datetime.today().strftime('%Y%m%d')
    
    def logging(self, message):
        log_time = self.get_time()
        with open(f'{net_ops.source["log_name"]}hist_dl.log', 'a', encoding='utf-8') as alert_file:
            alert_file.write(f'{log_time}:{message}\n')
        print(f'{log_time}:{message}')
        return

if __name__ == '__main__':
    get_params = GetParams()
    net_ops = NetOps(SourceMeta.bleeping_comp, SourceMeta.regex_patterns["general_url"]) # Change the object passed to NetOps to change the website that is targeted
    system_ops = SystemOps()
    get_params.get_http_prox()
    net_ops.iterator()