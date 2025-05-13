"""
TITLE: Phil Philson, the AI Intel Analyst

DATE: 2024-12-8

AUTHOR: Bick

PURPOSE: Utilize the open source AI model Llama3.2 (or others) to generate high level intelligence reports.


Dev Notes: Separate functions into classes
Add more hyperparameters in API call for fine tuning
Incorporate schedule library for automation - Create .service files for startup
Add gpu and cpu monitoring and cut off at certain temp
Needs logging
Needs try except blocks
Add mailing groups for different report types
"""

import ollama, re, output_parse, threat_fox_mal, data_parse
from os import getcwd, path
from sys import argv
from random import randrange
from datetime import datetime

class random_agents():  
    user_agents = ["Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0",
        "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
        "Dalvik/2.1.0 (Linux; U; Android 9; ADT-2 Build/PTT5.181126.002"]
        
    def change_agents():
        agent_index = randrange(0, len(random_agents.user_agents))
        return {f'user-agent': f'{random_agents.user_agents[agent_index]}'}

class config_items():
    source_list = []
    short_mem = []
    scraped_data = []
    source_type = ''
    set_llm = ''
    repeat_last_n = 0
    set_num_ctx = 0
    set_temp = .0
    set_keep_alive = 0
    send_mail = ''
    mail_ip = ''
    mail_port = ''
    p_type = ''

def sources_read():
    try:
        append = False
        s_type = config_items.source_type
        with open(f'{getcwd()}/config/web_urls.config', 'r') as source_file:
            lines = source_file.readlines()
            for line in lines:
                if '#' in line:
                    continue
                elif '$' in line and s_type in line:
                    append = True
                    continue
                elif append == False:
                    continue
                else:
                    if '}' in line:
                        break
                    config_items.source_list.append(line.strip())
    except Exception as e:
        exit_app(f'Error with web_urls.config file: {e}\nCheck file parameters.\nExiting.\n')
    return

def config_read():
    try:
        with open(f'{getcwd()}/config/phil.config', 'r') as config_file:
            lines = config_file.readlines()
            for line in lines:
                if '#' in line:
                    continue
                elif 'set_llm' in line:
                    line = line.split('=')
                    config_items.set_llm = line[1].strip()
                elif 'num_ctx' in line:
                    line = line.split('=')
                    config_items.set_num_ctx = int(line[1].strip())
                elif 'repeat_last_n' in line:
                    line = line.split('=')
                    config_items.repeat_last_n = int(line[1].strip())
                elif 'temp' in line:
                    line = line.split('=')
                    config_items.set_temp = float(line[1].strip())
                elif 'keep_alive' in line:
                    line = line.split('=')
                    config_items.set_keep_alive = int(line[1].strip())
                elif 'mail_forwarding' in line:
                    line = line.split('=')
                    config_items.send_mail = line[1].strip()
                elif 'mail_ip' in line:
                    line = line.split('=')
                    config_items.mail_ip = line[1].strip()
                elif 'mail_port' in line:
                    line = line.split('=')
                    config_items.mail_port = int(line[1].strip())
        sources_read()
    except Exception as e:
        exit_app(f'Error with phil.config file: {e}\nCheck file parameters.\nExiting.\n')
    return

def web_extract(sources, p_type):
    print('\nScraping web data, please wait...')
    with open(f'{getcwd()}/raw_data/{p_type}_scrape_data_{get_time()}.txt', 'w') as file:
        file.write('')
    for i in sources:
        try:
            downloaded = data_parse.get_req(i)
            result = data_parse.traf_func(downloaded)
            result_parse(result, p_type)
        except Exception as e:
            print(f'Error scraping {i} due to {e}, continuing...\n')
            continue
    build_call('system', f'Ingest this data for analysis: {config_items.scraped_data}')
    print('\nScraping completed...')
    return

def result_parse(result, p_type):
    try:
        cut_list = []
        for i in result:
            i = i.lower()
            if 'url:' in i or 'date:' in i:
                cut_list.append(f'{i} ')
            elif 'https://' in i:
                i = i.replace('[', '').replace(']', '').replace(')', '').replace('(', '').replace('→', '')
                cut_list.append(f'{i} ')
            elif len(i) < 36:
                continue
            else:
                i = re.sub(r'[^\w\s]', '', i)
                cut_list.append(f'{i} ')

            with open(f'{getcwd()}/raw_data/{p_type}_scrape_data_{get_time()}.txt', 'a') as file:
                file.write(f'{i}\n')
        config_items.scraped_data.append(''.join(cut_list))
    except Exception as e:
        print(f'Error parsing web scraped results: {e}\n')
    return

def read_prompt(p_type):
    try:
        if p_type == 'mail':
            del config_items.short_mem[2]
        with open(f'{get_cwd()}/prompts/{p_type}_prompt.md', 'r') as file:
            prompt_read = file.read()
        build_call('user', prompt_read)
        print('\nReponse being generated, please wait...\n')
        ollama_call(config_items.short_mem, p_type)
    except KeyboardInterrupt:
        exit_app()
    return

def build_call(role, content):
    config_items.short_mem.append(
    {
      'role': role,
      'content': content,
    })
    return

def ollama_call(call_message, p_type):
    static = ollama.chat(model=f'{config_items.set_llm}', options={
        'temperature': config_items.set_temp, 
        'num_ctx': config_items.set_num_ctx,
        'keep_alive': config_items.set_keep_alive, 
        'repeat_last_n': config_items.repeat_last_n
        }, 
        messages=call_message)
    build_response(static, p_type)
    return

def build_response(static, p_type):
    static_response = static['message']['content']
    if p_type == 'mail': # Initiates final call to Ollama API for email body
        with open(f'{getcwd()}/misc/last_email.txt', 'w') as f:
            f.write(static_response)
        forwarder(config_items.p_type)
        return
    else:
        with open(f'{getcwd()}/misc/ai_article.txt', 'w') as file:
            file.write(static_response)
        print('Done writing article...')
    return

def forwarder(p_type):
    output_parse.build_article(p_type, config_items.send_mail, config_items.mail_ip, config_items.mail_port)
    return # End of the line

def script_start():
    if argv[1] == '-cyber':
        config_items.source_type = 'Counter Threat Intelligence'
        config_items.p_type = 'cyber'
    elif argv[1] == '-finance':
        config_items.source_type ='Finance'
        config_items.p_type = 'finance'
    elif argv[1] == '-defense':
        config_items.source_type = 'Defense'
        config_items.p_type = 'defense'
    elif argv[1] == '-aerospace':
        config_items.source_type = 'Aerospace'
        config_items.p_type = 'aerospace'
    else:
        exit_app('Invalid argument.\nValid arguments include -cyber, -defense, -finance, -msm, -breaches, or -russia\n')
    config_read()
    exist_check(config_items.p_type)
    pre_load(config_items.p_type)
    web_extract(config_items.source_list, config_items.p_type)
    read_prompt(config_items.p_type)
    if config_items.p_type == 'cyber':
        threat_fox_mal.recent_ioc()
    read_prompt('mail')
    return

def exist_check(p_type): # Fix the sent file variable
    if path.exists(f'{getcwd()}/reports/{get_time()}_{p_type}_report.html'):
        print('Report already exists...\n')
        output_parse.send_connect(f'{get_time()}_{p_type}_report.html', config_items.send_mail, config_items.mail_ip, config_items.mail_port)
        exit_app('BYEEEEEE')
    return

def pre_load(p_type): #preload some settings
    if p_type == 'msm':
        p_type = 'main stream media'
    build_call('system', f'You are an Intelligence Analyst named Phil that specializes in writing {p_type} intelligence reports. Todays date is {get_time()}')
    return

def get_cwd():
    return getcwd()

def get_time():
    return datetime.today().strftime('%Y-%m-%d')

def exit_app(reason):
    print(f'{reason}')
    quit()

if __name__ == '__main__':
    script_start()
