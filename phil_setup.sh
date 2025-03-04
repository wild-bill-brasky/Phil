#!/bin/bash 
#Installs Ollama and the Llama3.2 LLM for use by Phil
read -p "
This script will install the Ollama environment and pull the Llama3.2 LLM from an online repository.
 
Press any key to continue or ctrl+C to exit..."

if [ $(id -u) -eq 0 ]
  then echo "Do not run script as sudo!"
  exit
else
    echo -e "Non-root user confirmed, checking for Ollama installation...\n"
    read -t 2 
fi

if command -v ollama > /dev/null 2>&1; then
    echo "Ollama is already Installed!"
else
    echo -e "Ollama is not installed, installing Ollama from Ollama.com...\n"
    read -t 2 
    curl -fsSL https://ollama.com/install.sh | sh
fi

echo -e "Pulling Llama3.2 LLM...\n"
read -t 3 
ollama pull llama3.2
echo "Llama3.2 successfully installed."

if [ -f /phil_env/bin/activate ]; then
    echo -e "Python Environment already installed, nub.\n"
else
    echo -e "Creating python virtual environment in current working directory..."
    read -t 3 
    python3 -m venv phil_env
    echo -e "Installing python requirements..."
    read -t 3
    source phil_env/bin/activate
    pip install -r requirements.txt
    deactivate
fi

echo -e "\nSetup completed! Phil is ready to roll :D"
exit
