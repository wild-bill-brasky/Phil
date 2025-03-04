import ollama

class listed_items():
    short_mem = []
    scraped_data = []

def build_call(role, content):
    listed_items.short_mem.append(
    {
      'role': role,
      'content': content,
    })
    return
    
def ollama_call(call_message):
    response = ollama.chat(model=f'llama3.2', options={'temperature': .0, 'num_ctx': 50000}, messages=call_message, stream=False)
    response = response['message']['content']
    return response

def pre_load(): #preload some settings
    build_call('system', 'You are an Intelligence Analyst named Phil that specializes in writing intelligence reports for a defense contractor.')
    return