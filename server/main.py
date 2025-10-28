#!/usr/bin/env python
"""Backend server for VisPile frontend interface.

Runs queries to LLMs using documents and instructions provided by the interface.

Sends results of LLM queries back to the frontend using Flask server.
"""

import fnmatch
import json
import os
from ast import literal_eval
from pathlib import Path

from dotenv import load_dotenv
import pandas as pd

import openai_tasks


__author__ = "Adam Coscia"
__license__ = "MIT"
__version__ = "0.1.0"
__email__ = "acoscia125@gmail.com"


# load env variables from .env file, including api keys
load_dotenv()

API_TOKEN = os.environ.get("OPENAI_API_KEY")  # gives access to OpenAI API
OPENAI_EMBEDDING_MODEL = "text-embedding-3-large"  # OpenAI embedding model

#
# load chunked text and pre-computed embeddings
# the files are ~100 MB combined, so may take a minute
# embeddings are of length 1024
# must convert embeddings from CSV str type back to list type
# the doc dataframe has three columns: "source", "text" and "embedding"
# the node dataframe has two columns: "node" and "embedding"
#
print(" * loading document embeddings...")
VAST_DOCUMENT_EMBEDDINGS = pd.read_csv("data/embeddings/vast/documents.csv")
VAST_DOCUMENT_EMBEDDINGS["embedding"] = VAST_DOCUMENT_EMBEDDINGS["embedding"].apply(literal_eval)

print(" * loading node embeddings...")
VAST_NODE_EMBEDDINGS = pd.read_csv("data/embeddings/vast/nodes.csv")
VAST_NODE_EMBEDDINGS["embedding"] = VAST_NODE_EMBEDDINGS["embedding"].apply(literal_eval)

print(" * embeddings loaded!")


def os_path_to_list(path, d, root):
    """Traverse files and their content nested in local directory.

    Returns flat list of file dicts with paths and contents.
    """
    name = os.path.basename(path)
    if os.path.isdir(path):
        # path is a directory
        for x in os.listdir(path):
            os_path_to_list(os.path.join(path, x), d, root)
    else:
        # path is a file
        if name.strip().lower().endswith(".txt"):
            with open(path, "r", encoding="cp1252", errors="backslashreplace") as f:
                new_id = path.replace(os.sep, "/")  # normalize path
                new_path = path.replace(root + os.sep, "").replace(os.sep, "/")  # normalize path
                d.append(
                    {
                        "id": new_id,
                        "path": new_path,
                        "pathList": new_path.split("/"),
                        "name": name,
                        "text": f.read(),
                    }
                )
    return d


def query(model_checkpoint, model_type, user_model_params, dataset, task, user_task_settings, documents):
    """Queries `model_checkpoint` using protocol for `model_type` and `task`.

    Uses `documents` and additional `user_model_params` and `user_task_settings` provided by the frontend interface.
    """
    # tasks that use the OpenAI chat endpoint API
    openai_chat_tasks = [
        "analyze",
        "summarize",
        "extract_entities",
        "classify_topics",
        "generate_questions",
        "generate_tasks",
        "explain_concepts",
        "answer_questions",
        "custom",
    ]
    # tasks that use the OpenAI embedding endpoint API
    openai_embedding_tasks = ["search_nodes", "search_documents", "compare_sentences"]

    if model_type == "openai":
        # set endpoint parameters
        if task in openai_chat_tasks:
            # chat endpoint parameters
            endpoint_parameters = {
                "API_TOKEN": API_TOKEN,  # gives access to OpenAI API
                "frequency_penalty": 1,  # [-2, 2] positive means less repetition in words
                "presence_penalty": 1,  # [-2, 2] positive penalize model for talking about new things
                "temperature": 0.2,  # [0, 2] set this or top_p but not both, lower to reduce randomness
                "top_p": None,  # [0, 1] set this or top_p but not both, lower to reduce randomness
            }
        if task in openai_embedding_tasks:
            # embedding endpoint parameters
            endpoint_parameters = {
                "API_TOKEN": API_TOKEN,  # gives access to OpenAI API
                "dimensions": 1024,  # Number of dimensions the resulting output embeddings should have. None for default.
                "format": "float",  # Format for embeddings, either `float` or `base64`
            }
        # override endpoint parameters with user model parameters from frontend
        if user_model_params is not None:
            for key, value in user_model_params.items():
                endpoint_parameters[key] = value

    # pick sub-routine based on model type and task
    results = {}

    if task in openai_chat_tasks:
        openai_chat_args = [model_checkpoint, endpoint_parameters, user_task_settings, documents, results]
    if task in openai_embedding_tasks:
        # data to compare with query
        if dataset == "live":
            # VAST dataset embeddings
            if task == "search_nodes":
                data = VAST_NODE_EMBEDDINGS
            if task == "search_documents":
                data = VAST_DOCUMENT_EMBEDDINGS
            if task == "compare_sentences":
                data = documents
        openai_embedding_args = [OPENAI_EMBEDDING_MODEL, endpoint_parameters, user_task_settings, data, results]

    if model_type == "openai":
        if task == "analyze":
            openai_tasks.run_openai_chat_analyze(*openai_chat_args)
        if task == "summarize":
            openai_tasks.run_openai_chat_summarize(*openai_chat_args)
        if task == "extract_entities":
            openai_tasks.run_openai_chat_extract(*openai_chat_args)
        if task == "classify_topics":
            openai_tasks.run_openai_chat_classify(*openai_chat_args)
        if task == "generate_questions":
            openai_tasks.run_openai_chat_questions(*openai_chat_args)
        if task == "generate_tasks":
            openai_tasks.run_openai_chat_tasks(*openai_chat_args)
        if task == "explain_concepts":
            openai_tasks.run_openai_chat_explain(*openai_chat_args)
        if task == "answer_questions":
            openai_tasks.run_openai_chat_answer(*openai_chat_args)
        if task == "custom":
            openai_tasks.run_openai_chat_custom(*openai_chat_args)
        if task == "search_nodes":
            openai_tasks.run_openai_embedding_search(*openai_embedding_args)
        if task == "search_documents":
            openai_tasks.run_openai_embedding_search(*openai_embedding_args)
        if task == "compare_sentences":
            openai_tasks.run_openai_embedding_compare(*openai_embedding_args)

    return results


#
# Web app packages
#
from flask import Flask, request, jsonify
from flask_cors import CORS


# Create Flask app
app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def get_connected():
    """Displays connected message. Useful to confirm if server is reachable."""
    return jsonify("Connected!")


@app.route("/token-usage", methods=["GET"])
def get_token_usage():
    """Displays token usage info."""
    tokens_used = {}
    for file in os.listdir(os.path.join(".", "data", "usage")):
        if fnmatch.fnmatch(file, "tokens_used*.json"):
            fp = os.path.join(".", "data", "usage", file)
            with open(fp, "r") as f:
                counts = json.load(f)
                tokens_used[file] = counts
    return jsonify(tokens_used)


@app.route("/documents", methods=["GET"])
def get_documents():
    """Get files from local directory to use as documents."""
    root = os.path.join(".", "data", "News Articles")

    files = os_path_to_list(root, [], root)

    return jsonify(files)


@app.route("/save", methods=["POST"])
def save_interactions():
    """Save interactions (for study)."""
    data_in = request.json  # request is sent as JSON, which is converted to a dict
    dataset = data_in["dataset"]  # get dataset as string
    interactions = data_in["interactions"]  # get interactions as dict
    root = os.path.join(".", "data", "study")  # get root of file path
    Path(root).mkdir(parents=True, exist_ok=True)  # create path if needed
    with open(os.path.join(root, f"{dataset}.json"), "w") as f:
        json.dump(interactions, f, indent=2)  # save to disk
    return {}  # no response needed


@app.route("/query", methods=["POST"])
def post_query():
    """Query model using task, documents and user settings sent from frontend interface."""
    data_in = request.json  # request is sent as JSON, which is converted to a dict

    model_checkpoint = data_in["model_checkpoint"]  #  (String) model checkpoint; e.g.,'gpt-3.5-turbo'
    model_type = data_in["model_type"]  #              (String) model type; e.g., 'openai'
    user_model_params = data_in["model_settings"]  #   (Dict) user-defined settings for model
    dataset = data_in["dataset"]  #                    (String) dataset to pull embeddings from
    task = data_in["task"]  #                          (String) task for LLM to perform; e.g., 'summarize'
    user_task_settings = data_in["task_settings"]  #   (Dict) user-defined settings for task
    documents = data_in["documents"]  #                (List) documents as text strings; e.g., ['abc', 'edf', ...]

    # query model type and checkpoint on task with documents and model/task settings
    data_out = query(model_checkpoint, model_type, user_model_params, dataset, task, user_task_settings, documents)

    return jsonify(data_out)  # send data to client (must be in JSON string format)


if __name__ == "__main__":
    app.run(host="localhost", port=int(os.environ.get("PORT", 3008)))
