"""OpenAI tasks helper module."""

import evaluate
import pandas as pd
import spacy
from scipy import spatial  # for calculating vector similarities for embedding search
from sklearn.metrics.pairwise import cosine_similarity  # for calculating vector similarities for sentence comparison

import openai_api
import openai_prompts


__author__ = "Adam Coscia"
__license__ = "MIT"
__version__ = "0.1.0"
__email__ = "acoscia125@gmail.com"


DOC_SEP = "|||||"  # a special separator string to put between documents, same as used in `multi-news` dataset
NLP = spacy.load("data/models/en_core_web_sm-3.8.0")


def run_openai_chat_analyze(model_checkpoint, endpoint_params, task_settings, documents, results, seed=None):
    """Make OpenAI API request to analyze documents."""
    # get analyze prompt formatter function
    if len(documents) == 1:
        prompt_formatter = openai_prompts.openai_analyze_singledoc
    elif len(documents) > 1:
        prompt_formatter = openai_prompts.openai_analyze_multidoc

    # get instructions to put in prompt
    additional_instructions = task_settings["instructions"]
    user_instructions = [additional_instructions]

    print("prompt:")
    print(prompt_formatter(DOC_SEP, "", user_instructions))

    # formats documents into custom prompt and returns chat messages for OpenAI API
    messages, max_tokens = openai_api.format_chat_messages(
        model_checkpoint,
        documents,
        DOC_SEP,
        user_instructions,
        prompt_formatter,
    )

    # make a request to OpenAI using formatted messages and recieve response
    status, response, _, _ = openai_api.request_chat_endpoint(
        model_checkpoint, messages, max_tokens, endpoint_params, seed
    )

    if status == 200:
        text = response["choices"][0]["message"]["content"]  # get text from response
        results["success"] = True
        results["text"] = text  # save results
    else:
        results["success"] = True
        results["response"] = response  # return entire response
        results["status"] = status  # return status code


def run_openai_chat_summarize(model_checkpoint, endpoint_params, task_settings, documents, results, seed=None):
    """Make OpenAI API request to summarize documents.

    Evaluates summary using ROUGE.

    See: <https://huggingface.co/docs/transformers/tasks/summarization#evaluate>
    """
    # get summarization prompt formatter function
    if len(documents) == 1 and task_settings["summary_length"] == "concise":
        prompt_formatter = openai_prompts.openai_summarize_concise_singledoc
    elif len(documents) == 1 and task_settings["summary_length"] == "verbose":
        prompt_formatter = openai_prompts.openai_summarize_verbose_singledoc
    elif len(documents) > 1 and task_settings["summary_length"] == "concise":
        prompt_formatter = openai_prompts.openai_summarize_concise_multidoc
    elif len(documents) > 1 and task_settings["summary_length"] == "verbose":
        prompt_formatter = openai_prompts.openai_summarize_verbose_multidoc

    # get instructions to put in prompt
    additional_instructions = task_settings["instructions"]
    user_instructions = [additional_instructions]

    print("prompt:")
    print(prompt_formatter(DOC_SEP, "", user_instructions))

    # formats documents into summarization prompt and returns chat messages for OpenAI API
    messages, max_tokens = openai_api.format_chat_messages(
        model_checkpoint,
        documents,
        DOC_SEP,
        user_instructions,
        prompt_formatter,
    )

    # make a request to OpenAI using formatted messages and recieve response
    status, response, input_tokens_used, output_tokens_used = openai_api.request_chat_endpoint(
        model_checkpoint, messages, max_tokens, endpoint_params, seed
    )

    if status == 200:
        # get summary text from response
        summary_text = response["choices"][0]["message"]["content"]

        # evaluate summary with ROGUE
        rouge = evaluate.load("rouge")
        text = "".join([" ".join(doc.replace("\n", " ").split()) for doc in documents])
        rogue_result = rouge.compute(predictions=[summary_text], references=[text], use_stemmer=True)

        # save results
        results["success"] = True
        results["text"] = summary_text
        results["stats"] = {
            "rouge1": rogue_result["rouge1"],
            "rouge2": rogue_result["rouge2"],
            "rougeL": rogue_result["rougeL"],
            "percent_reduction": {
                "input": input_tokens_used,
                "output": output_tokens_used,
                "value": (1 - output_tokens_used / input_tokens_used) * 100,
            },
        }
    else:
        results["success"] = False
        results["response"] = response  # return entire response
        results["status"] = status  # return status code


def run_openai_chat_extract(model_checkpoint, endpoint_params, task_settings, documents, results, seed=None):
    """Make OpenAI API request to extract entities in documents."""
    # get extract prompt formatter function
    if len(documents) == 1:
        prompt_formatter = openai_prompts.openai_extract_singledoc
    elif len(documents) > 1:
        prompt_formatter = openai_prompts.openai_extract_multidoc

    # get instructions to put in prompt
    entity_string = task_settings["entity"]
    additional_instructions = task_settings["instructions"]
    user_instructions = [entity_string, additional_instructions]

    print("prompt:")
    print(prompt_formatter(DOC_SEP, "", user_instructions))

    # formats documents into custom prompt and returns chat messages for OpenAI API
    messages, max_tokens = openai_api.format_chat_messages(
        model_checkpoint,
        documents,
        DOC_SEP,
        user_instructions,
        prompt_formatter,
    )

    # make a request to OpenAI using formatted messages and recieve response
    status, response, _, _ = openai_api.request_chat_endpoint(
        model_checkpoint, messages, max_tokens, endpoint_params, seed
    )

    if status == 200:
        text = response["choices"][0]["message"]["content"]  # get text from response
        results["success"] = True
        results["text"] = text  # save results
    else:
        results["success"] = True
        results["response"] = response  # return entire response
        results["status"] = status  # return status code


def run_openai_chat_classify(model_checkpoint, endpoint_params, task_settings, documents, results, seed=None):
    """Make OpenAI API request to classify topics in documents."""
    # get classify prompt formatter function
    if len(documents) == 1:
        prompt_formatter = openai_prompts.openai_classify_singledoc
    elif len(documents) > 1:
        prompt_formatter = openai_prompts.openai_classify_multidoc

    # get instructions to put in prompt
    additional_instructions = task_settings["instructions"]
    user_instructions = [additional_instructions]

    print("prompt:")
    print(prompt_formatter(DOC_SEP, "", user_instructions))

    # formats documents into custom prompt and returns chat messages for OpenAI API
    messages, max_tokens = openai_api.format_chat_messages(
        model_checkpoint,
        documents,
        DOC_SEP,
        user_instructions,
        prompt_formatter,
    )

    # make a request to OpenAI using formatted messages and recieve response
    status, response, _, _ = openai_api.request_chat_endpoint(
        model_checkpoint, messages, max_tokens, endpoint_params, seed
    )

    if status == 200:
        text = response["choices"][0]["message"]["content"]  # get text from response
        results["success"] = True
        results["text"] = text  # save results
    else:
        results["success"] = True
        results["response"] = response  # return entire response
        results["status"] = status  # return status code


def run_openai_chat_questions(model_checkpoint, endpoint_params, task_settings, documents, results, seed=None):
    """Make OpenAI API request to synthesize analytic questions based on documents."""
    # get questions prompt formatter function
    if len(documents) == 1:
        prompt_formatter = openai_prompts.openai_questions_singledoc
    elif len(documents) > 1:
        prompt_formatter = openai_prompts.openai_questions_multidoc

    # get instructions to put in prompt
    additional_instructions = task_settings["instructions"]
    user_instructions = [additional_instructions]

    print("prompt:")
    print(prompt_formatter(DOC_SEP, "", user_instructions))

    # formats documents into custom prompt and returns chat messages for OpenAI API
    messages, max_tokens = openai_api.format_chat_messages(
        model_checkpoint,
        documents,
        DOC_SEP,
        user_instructions,
        prompt_formatter,
    )

    # make a request to OpenAI using formatted messages and recieve response
    status, response, _, _ = openai_api.request_chat_endpoint(
        model_checkpoint, messages, max_tokens, endpoint_params, seed
    )

    if status == 200:
        text = response["choices"][0]["message"]["content"]  # get text from response
        results["success"] = True
        results["text"] = text  # save results
    else:
        results["success"] = True
        results["response"] = response  # return entire response
        results["status"] = status  # return status code


def run_openai_chat_tasks(model_checkpoint, endpoint_params, task_settings, documents, results, seed=None):
    """Make OpenAI API request to synthesize analytic tasks based on documents."""
    # get tasks prompt formatter function
    if len(documents) == 1:
        prompt_formatter = openai_prompts.openai_tasks_singledoc
    elif len(documents) > 1:
        prompt_formatter = openai_prompts.openai_tasks_multidoc

    # get instructions to put in prompt
    additional_instructions = task_settings["instructions"]
    user_instructions = [additional_instructions]

    print("prompt:")
    print(prompt_formatter(DOC_SEP, "", user_instructions))

    # formats documents into custom prompt and returns chat messages for OpenAI API
    messages, max_tokens = openai_api.format_chat_messages(
        model_checkpoint,
        documents,
        DOC_SEP,
        user_instructions,
        prompt_formatter,
    )

    # make a request to OpenAI using formatted messages and recieve response
    status, response, _, _ = openai_api.request_chat_endpoint(
        model_checkpoint, messages, max_tokens, endpoint_params, seed
    )

    if status == 200:
        text = response["choices"][0]["message"]["content"]  # get text from response
        results["success"] = True
        results["text"] = text  # save results
    else:
        results["success"] = True
        results["response"] = response  # return entire response
        results["status"] = status  # return status code


def run_openai_chat_explain(model_checkpoint, endpoint_params, task_settings, documents, results, seed=None):
    """Make OpenAI API request to explain concepts in documents."""
    # get explain prompt formatter function
    if len(documents) == 1:
        prompt_formatter = openai_prompts.openai_explain_singledoc
    elif len(documents) > 1:
        prompt_formatter = openai_prompts.openai_explain_multidoc

    # get instructions to put in prompt
    concepts = [f'"{x}"' for x in task_settings["concepts"]]
    concepts_string = ", ".join(concepts)
    additional_instructions = task_settings["instructions"]
    user_instructions = [concepts_string, additional_instructions]

    print("prompt:")
    print(prompt_formatter(DOC_SEP, "", user_instructions))

    # formats documents into custom prompt and returns chat messages for OpenAI API
    messages, max_tokens = openai_api.format_chat_messages(
        model_checkpoint,
        documents,
        DOC_SEP,
        user_instructions,
        prompt_formatter,
    )

    # make a request to OpenAI using formatted messages and recieve response
    status, response, _, _ = openai_api.request_chat_endpoint(
        model_checkpoint, messages, max_tokens, endpoint_params, seed
    )

    if status == 200:
        text = response["choices"][0]["message"]["content"]  # get text from response
        results["success"] = True
        results["text"] = text  # save results
    else:
        results["success"] = True
        results["response"] = response  # return entire response
        results["status"] = status  # return status code


def run_openai_chat_answer(model_checkpoint, endpoint_params, task_settings, documents, results, seed=None):
    """Make OpenAI API request to answer questions using documents."""
    # get answer prompt formatter function
    if len(documents) == 1:
        prompt_formatter = openai_prompts.openai_answer_singledoc
    elif len(documents) > 1:
        prompt_formatter = openai_prompts.openai_answer_multidoc

    # get instructions to put in prompt
    questions = [f'"{x}"' for x in task_settings["questions"]]
    questions_string = ", ".join(questions)
    additional_instructions = task_settings["instructions"]
    user_instructions = [questions_string, additional_instructions]

    print("prompt:")
    print(prompt_formatter(DOC_SEP, "", user_instructions))

    # formats documents into custom prompt and returns chat messages for OpenAI API
    messages, max_tokens = openai_api.format_chat_messages(
        model_checkpoint,
        documents,
        DOC_SEP,
        user_instructions,
        prompt_formatter,
    )

    # make a request to OpenAI using formatted messages and recieve response
    status, response, _, _ = openai_api.request_chat_endpoint(
        model_checkpoint, messages, max_tokens, endpoint_params, seed
    )

    if status == 200:
        text = response["choices"][0]["message"]["content"]  # get text from response
        results["success"] = True
        results["text"] = text  # save results
    else:
        results["success"] = True
        results["response"] = response  # return entire response
        results["status"] = status  # return status code


def run_openai_chat_custom(model_checkpoint, endpoint_params, task_settings, documents, results, seed=None):
    """Make OpenAI API request to run custom prompt over documents."""
    # get custom prompt formatter function
    if len(documents) == 1:
        prompt_formatter = openai_prompts.openai_custom_singledoc
    elif len(documents) > 1:
        prompt_formatter = openai_prompts.openai_custom_multidoc

    # get instructions to put in prompt
    custom_prompt = task_settings["prompt"]
    user_instructions = [custom_prompt]

    print("prompt:")
    print(prompt_formatter(DOC_SEP, "", user_instructions))

    # formats documents into custom prompt and returns chat messages for OpenAI API
    messages, max_tokens = openai_api.format_chat_messages(
        model_checkpoint,
        documents,
        DOC_SEP,
        user_instructions,
        prompt_formatter,
    )

    # make a request to OpenAI using formatted messages and recieve response
    status, response, _, _ = openai_api.request_chat_endpoint(
        model_checkpoint, messages, max_tokens, endpoint_params, seed
    )

    if status == 200:
        text = response["choices"][0]["message"]["content"]  # get text from response
        results["success"] = True
        results["text"] = text  # save results
    else:
        results["success"] = True
        results["response"] = response  # return entire response
        results["status"] = status  # return status code


def run_openai_embedding_search(model_checkpoint, endpoint_params, task_settings, embeddings, results):
    """Make OpenAI API request to get embedding of user query and search for related strings (e.g., nodes in a knowledge graph or documents).

    Returns a list of strings and relatedness scores, sorted from most related to least.

    See: <https://cookbook.openai.com/examples/question_answering_using_embeddings>
    """
    # make a request to OpenAI embedding endpoint and recieve response
    status, response, _ = openai_api.request_embedding_endpoint(
        model_checkpoint, task_settings["query"], endpoint_params
    )

    if status == 200:
        # set comparator function and number of documents to retrieve
        compute_relatedness = lambda x, y: 1 - spatial.distance.cosine(x, y)
        top_n = task_settings["top_n"] if "top_n" in task_settings else len(embeddings)

        # get query embedding
        query_embedding = response["data"][0]["embedding"]

        # score each row of the source texts (documents, nodes) using their pre-computed embeddings
        all_texts_scored = [
            (row[task_settings["id_col"]], compute_relatedness(query_embedding, row["embedding"]))
            for _, row in embeddings.iterrows()
        ]

        # sort by relatedness
        all_texts_scored.sort(key=lambda x: x[1], reverse=True)

        # take the top_n scores
        top_texts = [{"id": x[0], "score": x[1]} for x in all_texts_scored[:top_n]]

        # save results
        results["success"] = True
        results["texts"] = top_texts
    else:
        results["success"] = False
        results["response"] = response  # return entire response
        results["status"] = status  # return status code


def run_openai_embedding_compare(model_checkpoint, endpoint_params, task_settings, documents, results):
    """Make OpenAI API request to get embeddings of user query and compute pairwise similarity between query and documents.

    Uses spaCy to perform sentence segmentation of query and all documents, then computes similarity between all sentences.

    - See: <https://spacy.io/usage/linguistic-features#sbd>

    For each sentence in the query, finds the sentence in any document with the highest similarity.

    Returns a list of query and document sentence pairs and relatedness scores.
    """
    query = task_settings["query"]

    # split query and documents into sentences and store all sentences in single list by index
    source_id = []
    source_index = []
    all_sents_text = []
    all_sents_chars = []

    i = 0
    query_doc = NLP(query["text"])
    for query_sent in query_doc.sents:
        source_id.append(query["id"])
        source_index.append(i)
        all_sents_text.append(query_sent.text)
        all_sents_chars.append([query_sent.start_char, query_sent.end_char])

    for node in documents:
        i += 1
        node_doc = NLP(node["text"])
        for node_sent in node_doc.sents:
            source_id.append(node["id"])
            source_index.append(i)
            all_sents_text.append(node_sent.text)
            all_sents_chars.append([node_sent.start_char, node_sent.end_char])

    # make a request to OpenAI embedding endpoint and recieve response
    status, response, _ = openai_api.request_embedding_endpoint(model_checkpoint, all_sents_text, endpoint_params)

    if status == 200:
        # get embeddings
        for i, be in enumerate(response["data"]):
            assert i == be["index"]  # double check embeddings are in same order as input
        embeddings = [e["embedding"] for e in response["data"]]

        # reconstruct sentence sets with embeddings
        sentences = pd.DataFrame(
            {
                "source_id": source_id,  # id of source that sentence is from
                "source_index": source_index,  # index of source that sentence is from
                "sent_chars": all_sents_chars,  # char offsets for sent span in source
                "sent_text": all_sents_text,  # sentence text
                "embedding": embeddings,  # embeddings from OpenAI
            }
        )

        # get lists of query (X) and document (Y) embeddings to compare
        X = sentences[sentences["source_index"] == 0]["embedding"].to_list()
        Y = sentences[sentences["source_index"] > 0]["embedding"].to_list()

        # compute pairwise cosine similarity
        df = pd.DataFrame(cosine_similarity(X, Y))
        n_query_sents = len(X)
        df.columns = [col + n_query_sents for col in df.columns]

        # get top_n pairs of similarity between each query sentence and all document sentences
        top_n = task_settings["top_n"] if "top_n" in task_settings else 1
        df_top = df.apply(pd.Series.nlargest, axis=1, n=top_n)
        df_top = (
            df_top.stack()
            .reset_index()
            .rename(columns={"level_0": "query_sent_index", "level_1": "document_sent_index", 0: "score"})
        )

        # map query and documents to sentences using sent_index
        new_query_cols = ["query_id", "query_chars", "query_sent"]
        new_document_cols = ["document_id", "document_chars", "document_sent"]
        sentences_cols = ["source_id", "sent_chars", "sent_text"]
        df_top[new_query_cols] = df_top["query_sent_index"].apply(lambda x: sentences.iloc[x][sentences_cols])
        df_top[new_document_cols] = df_top["document_sent_index"].apply(lambda x: sentences.iloc[x][sentences_cols])

        # get results as list of records
        top_links = df_top.to_dict("records")

        # save results
        results["success"] = True
        results["links"] = top_links
    else:
        results["success"] = False
        results["response"] = response  # return entire response
        results["status"] = status  # return status code
