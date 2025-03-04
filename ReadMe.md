              (      )
              ~(^^^^)~
               ) @@ \~_          |\
              /     | \        \~ /  --- (Welcome to Phil's read me file.)
             ( 0  0  ) \        | |
              ---___/~  \       | |
               /'__/ |   ~-_____/ |
o          _   ~----~      ___---~
  O       //     |         |
         ((~\  _|         -|
   o  O //-_ \/ |        ~  |
        ^   \_ /         ~  |
               |          ~ |
               |     /     ~ |
               |     (       |
                \     \      /\
               / -_____-\   \ ~~-*
               |  /       \  \
               / /         / /
             /~  |       /~  |
             ~~~~        ~~~~

# Requirements:
    - Ubuntu based Linux distro (22.04 or later)
    - curl binary
    - Python 3.10 or later and pip
    - Unrestricted access to the interwebs
    - Functioning SMTP bridge or server with credentials

# Installion:
    - Running the **setup.sh** shell script will install the Ollama API, the Llama3.2 LLM (this can be changed in the config file), and
      a python virtual environment. This will be created in the working directory in the folder /phil_env. DO NOT RUN AS ROOT.

# Scope:
    - Phil, or whatever name you end up giving it, is an AI bot that writes high level intelligence reports for various subjects. 
      A Proton Mail bridge is used to forward reports, however any SMTP server using TLS can be configured for use.

# Usage: 
    - Phil is initated from terminal with the run_phil.sh shell script. This will load the python virtual environment and scrape the
      web for information. Sources can be added or removed in the web_urls.config file. 
    - Phil takes the following arguments and produces reports based on those arguments. The arguments are -defense, -cyber, -finance, and -msm
    - Email forwarding is default off, however when on, it will forward the reports to the specified SMTP mail server via TLS. This is configured 
      in the phil.config file. An example terminal command would be **"./run_phil.sh -defense".**
    - Reports are automatically saved locally in the reports directory.
    - Raw scraped and cleaned data is stored in the raw_data directory.
    - The email forwarding server is designed to be on the same subnet. Make sure to configure host and network firewalls as needed.

# Hyperparamter Warning:
    - This version of Phil does not use RAG but instead uses a large context window (num_ctx) to ingest data and create a report. No scraped data
      is saved into a RAG DB. With this said, a large num_ctx value can overwhelm GPUs and require RAM to process and store tokens. In this case, data must flow
      through the CPU for compute. This can overwork the CPU and lead to above safe operating temperatures and possibly burning out your CPU. Make 
      sure to experiment with hyperparameter settings in the phil.config file prior to scheduled use. For reference, a 12GB graphics card (4070 RTX)
      can sustain a num_ctx value of 50,000 with the 3.2B llama3.2 LLM without calling for external resources.




