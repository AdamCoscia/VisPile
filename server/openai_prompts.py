"""OpenAI prompt formatter functions module.

Each prompt formatter function should take as arguments three variables:
- `doc_sep`: token used for separating documents
- `doc_prompt`: the documents combined in a single prompt, separated by doc_sep
- `user_instructions`: a list of any additional text instructions from the user
"""

from textwrap import dedent

__author__ = "Adam Coscia"
__license__ = "MIT"
__version__ = "0.1.0"
__email__ = "acoscia125@gmail.com"


def openai_analyze_singledoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for analyzing a single document."""
    system_prompt = f"""
    You are a helpful assistant for analyzing a single document.

    You will be provided a single document.

    Your task is to analyze the document as if you are a professional intelligence analyst. You MUST cite how you used the document for analysis in your response. {user_instructions[0]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]


def openai_analyze_multidoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for analyzing multiple documents."""
    system_prompt = f"""
    You are a helpful assistant for analyzing multiple documents.
    
    You will be provided multiple documents, where each document is separated by {doc_sep}.

    Your task is to analyze the documents as if you are a professional intelligence analyst. You MUST cite (1) which documents you used for analysis and (2) how you used the documents in your response. {user_instructions[0]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]


def openai_summarize_concise_singledoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for synthesizing a shorter summary of a single document."""
    system_prompt = f"""
    You are a helpful assistant for summarizing a single document.

    You will be provided a single document.

    In clear and concise language, summarize the main events that are described in the document. Start your response by saying 'This document'. Return your response in a single sentence. {user_instructions[0]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]


def openai_summarize_concise_multidoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for synthesizing a shorter summary of multiple documents."""
    system_prompt = f"""
    You are a helpful assistant for summarizing multiple documents.

    You will be provided multiple documents, where each document is separated by {doc_sep}.

    In clear and concise language, summarize the main events that are described across all of the documents. Start your response by saying 'The documents'. Return your response in a single sentence. {user_instructions[0]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]


def openai_summarize_verbose_singledoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for synthesizing a longer summary of a single document."""
    system_prompt = f"""
    You are a helpful assistant for summarizing a single document.

    You will be provided a single document.

    In clear and concise language, summarize the key points, themes, and events described in the document. {user_instructions[0]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]


def openai_summarize_verbose_multidoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for synthesizing a longer summary of multiple documents."""
    system_prompt = f"""
    You are a helpful assistant for summarizing multiple documents.

    You will be provided multiple documents, where each document is separated by {doc_sep}.

    In clear and concise language, summarize the key points, themes, and events described in each document. {user_instructions[0]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]


def openai_extract_singledoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for extracting entities in a single document."""
    system_prompt = f"""
    You are a helpful assistant for extracting all entities from a single document.

    You will be provided a single document.

    Your task is to extract all entities of the following type: "{user_instructions[0]}". You MUST use ONLY the provided document. You will NOT use any other source of information. {user_instructions[1]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]


def openai_extract_multidoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for extracting entities in multiple documents."""
    system_prompt = f"""
    You are a helpful assistant for extracting all entities from multiple documents.

    You will be provided multiple documents, where each document is separated by {doc_sep}.

    Your task is to extract all entities of the following type: "{user_instructions[0]}". If multiple documents contain multiple entities, list all documents that entity is described in. You MUST use ONLY the provided documents. You will NOT use any other source of information. You MUST cite which documents each entity was extracted from in your response. {user_instructions[1]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]


def openai_classify_singledoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for classifying topics described in a single document."""
    system_prompt = f"""
    You are a helpful assistant for classifying the topics of a single document.

    You will be provided a single document.

    Your task is to classify the topics of the document. For each topic, please list two items: (1) the name of the topic; and (2) a short description of the topic. {user_instructions[0]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]


def openai_classify_multidoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for classifying topics found in multiple documents."""
    system_prompt = f"""
    You are a helpful assistant for classifying the topics of multiple documents.

    You will be provided multiple documents, where each document is separated by {doc_sep}.

    Your task is to classify the topics in each document. For each topic, please list three items: (1) the name of the topic; (2) a short description of the topic; and (3) which documents the topic belongs to. {user_instructions[0]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]


def openai_questions_singledoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for synthesizing analytic questions to ask about a single document."""
    system_prompt = f"""
    You are a helpful assistant for synthesizing analytic questions to ask about a single document.

    You will be provided a single document.

    Your task is to synthesize analytic questions to ask about the document as if you are a professional intelligence analyst. You MUST cite how you used the document to synthesize the questions in your response. {user_instructions[0]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]


def openai_questions_multidoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for synthesizing analytic questions to ask about multiple documents."""
    system_prompt = f"""
    You are a helpful assistant for synthesizing analytic questions to ask about multiple documents.

    You will be provided multiple documents, where each document is separated by {doc_sep}.

    Your task is to synthesize analytic questions to ask about the documents as if you are a professional intelligence analyst. You MUST cite (1) which documents you used to synthesize the questions and (2) how you used the documents in your response. {user_instructions[0]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]


def openai_tasks_singledoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for synthesizing analytic tasks to perform with a single document."""
    system_prompt = f"""
    You are a helpful assistant for synthesizing analytic tasks to perform with a single document.

    You will be provided a single document.

    Your task is to synthesize analytic tasks to perform with the document as if you are a professional intelligence analyst. You MUST cite how you used the document to synthesize the tasks in your response. {user_instructions[0]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]


def openai_tasks_multidoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for synthesizing analytic tasks to perform with multiple documents."""
    system_prompt = f"""
    You are a helpful assistant for synthesizing analytic tasks to ask about multiple documents.

    You will be provided multiple documents, where each document is separated by {doc_sep}.

    Your task is to synthesize analytic tasks to ask about the documents as if you are a professional intelligence analyst. You MUST cite (1) which documents you used to synthesize the tasks and (2) how you used the documents in your response. {user_instructions[0]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]


def openai_explain_singledoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for explaining concepts in a single document."""
    system_prompt = f"""
    You are a helpful assistant for explaining concepts using a single document.

    You will be provided a single document.

    Your task is to use the document to explain the following concepts: {user_instructions[0]}. You MUST use ONLY the provided document. You will NOT use any other source of information. {user_instructions[1]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]


def openai_explain_multidoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for explaining concepts in multiple documents."""
    system_prompt = f"""
    You are a helpful assistant for explaining concepts using multiple documents.

    You will be provided multiple documents, where each document is separated by {doc_sep}.

    Your task is to use the documents to explain the following concepts: {user_instructions[0]}. You MUST use ONLY the provided documents. You will NOT use any other source of information. You MUST cite which documents you used to explain each concept in your response. {user_instructions[1]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]


def openai_answer_singledoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for answering questions using a single document."""
    system_prompt = f"""
    You are a helpful assistant for answering questions using a single document.

    You will be provided a single document.

    Your task is to use the document to answer the following questions: {user_instructions[0]}. You MUST use ONLY the provided document. You will NOT use any other source of information. Please explain how you used the provided document in your response. {user_instructions[1]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]


def openai_answer_multidoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for answering questions using multiple documents."""
    system_prompt = f"""
    You are a helpful assistant for answering questions using multiple documents.

    You will be provided multiple documents, where each document is separated by {doc_sep}.

    Your task is to use the documents to answer the following questions: {user_instructions[0]}. You MUST use ONLY the provided documents. You will NOT use any other source of information. Please explain how you used the provided documents in your response. {user_instructions[1]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]


def openai_custom_singledoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for running custom instructions with a single document."""
    system_prompt = f"""
    You are a helpful assistant that expertly uses a single document to perform tasks.

    You will be provided a single document.

    You will use the document to perform the following task: {user_instructions[0]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]


def openai_custom_multidoc(doc_sep, doc_prompt, user_instructions):
    """Returns prompt instructions for running custom instructions with multiple documents."""
    system_prompt = f"""
    You are a helpful assistant that expertly uses multiple documents to perform tasks.

    You will be provided multiple documents, where each document is separated by {doc_sep}.
    
    You will use the documents to perform the following task: {user_instructions[0]}
    """
    return [
        {
            "role": "system",
            "content": dedent(system_prompt).strip(),
        },
        {
            "role": "user",
            "content": f"""{doc_prompt}""",
        },
    ]
