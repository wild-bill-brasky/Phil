import requests, json, data_parse, ai_call, phil_report
from collections import Counter

class malware_info:
    malware_list = []
    count_list = []

def recent_ioc():
    
    headers = abuse_header()
    data = { 
        "query": "get_iocs", 
        "days": 1, 
        }
    data = json.dumps(data)

    response = requests.post('https://threatfox-api.abuse.ch/api/v1/', headers=headers, data=data)
    list_malware(response.text)
    return

def list_malware(lines):
    for line in lines.split('\n'):
        if 'malware_printable' not in line:
            continue
        else:
            line = line.split(':')
            line = line[1].strip().replace('"', '').replace(',', '')
            if 'Unknown malware' in line:
                continue
            else:
                malware_info.malware_list.append(line)
    mal_counter()
    return

def mal_counter():
    freqs = Counter(malware_info.malware_list)
    top_5 = freqs.most_common(5)
    item_split(top_5)
    return

def item_split(item_list):
    for i in item_list:
        i = str(i).split(',')
        i = i[0].strip("('").strip()
        malware_info.count_list.append(i)
    tag_loop()
    return

def tag_loop():
    with open(f'{phil_report.getcwd()}/misc/ai_article.txt', 'a') as file:
        file.write(f'\n<u><b>Malware Roundup: 5 Most Active Malware in the Wild</u></b>\n\n')
    for j in malware_info.count_list:
        mal_loop(j)
    return

def mal_loop(malware):
    headers = abuse_header()
    data = {
        'query': 'malwareinfo',
        'malware': f'{malware}',
        'limit': 10
    }
    data = json.dumps(data)
    response = requests.post('https://threatfox-api.abuse.ch/api/v1/', headers=headers, data=data, timeout=60)
    results_writer(response, malware)
    return

def results_writer(response, malware):
    ioc_list = []
    counter = 0
    with open(f'{phil_report.getcwd()}/misc/ai_article.txt', 'a') as file:
        for i in response.iter_lines():
            i = i.decode()
            if '"ioc"' in i:
                i = i.split('ioc":')
                i = i[1].strip().replace('\\', '').replace('"', '').replace(',', '')
                ioc_list.append(i)
            elif counter == 0:
                if '"malware_malpedia"' in i:
                    counter = counter +1
                    mal_url = url_parser(i)
                else:
                    continue
            else:
                continue
        file.write('\n')
        data_parse.web_extract(mal_url)
        ai_call.pre_load()
        ai_call.build_call('user', 'As a cybersecurity analyst, analyze the malware that is discussed in the ingested text, which will be used in a CTI report. Discuss any specific threat actors or TTPs mentioned. Your analysis should be no more than 7 sentences. Refer to the ingested text as "currently available data".')
        ai_resp = ai_call.ollama_call(ai_call.listed_items.short_mem)
        ai_call.listed_items.short_mem.clear()
        ai_call.listed_items.scraped_data.clear()
        file.write(f'<u>{malware} Analysis:</u>\n{ai_resp}\n\n<u>{malware} IOCs:</u>\n')
        for i in ioc_list:
            file.write(f'{i}\n')
    return

def url_parser(i):
    i = str(i).split(':')
    i = i[2].replace(',', '').strip('"').replace('\\', '')
    i = f'https:{i}'
    return i

def abuse_header():
    headers = {
        'Auth-Key': '33dbb277a037697a9435055c2c6ce0f251e86f166261b3c2',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    return headers

if __name__ == '__main__':
    recent_ioc()