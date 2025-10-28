# VisPile server

To run prompts for the VisPile interface, we use the OpenAI API to query GPT. We host a Python Flask server that recieves instructions from the interface, runs the prompts, and sends the processed data back to the interface.

You will need an OpenAI API key, which you can generate in your [OpenAI dashboard](https://platform.openai.com/settings/organization/api-keys).

## Setup

Before you begin:

- Install Python `>= v3.9.x` ([latest release](https://www.python.org/downloads/release/python-31112/))

Download the data:

- Download [data.zip](https://drive.google.com/file/d/1SWyPWpJ06rd1_oDcwITPO8ddpwRQYUo6/view?usp=sharing)
- Move into the [data](data/) directory
- Unzip the file
- You should see 3 new folders in [data](data/): `News Articles/`, `embeddings/`, and `models/`

First, install dependencies:

- If you are running Windows (replace `-3.9` with your Python version):

```bash
# Start a virtual environment
py -3.9 -m venv venv

# Activate the virtual environment
.\venv\Scripts\activate

# Install dependencies
python -m pip install -r requirements.txt
```

- If you are running MacOS / Linux (replace `python3.9` with your Python version):

```bash
# Start a virtual environment
python3.9 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
python -m pip install -r requirements.txt
```

Next, create a [.env](.env) file in this directory and put the following in it:

```bash
OPENAI_API_KEY=<<YOUR API KEY HERE>>
```

Finally, run the server:

```bash
python main.py
```

## Packages

- dotenv `v3.4.2` [link](https://github.com/theskumar/python-dotenv)
- Flask `v3.1.x` [link](https://flask.palletsprojects.com/en/stable/)
- flask-cors `v5.x` [link](https://pypi.org/project/flask-cors/)
- OpenAI Python API `v3.4.2` [link](https://github.com/openai/openai-python)
