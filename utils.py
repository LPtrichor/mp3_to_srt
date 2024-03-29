import time
from gradio import Request
import openai


def gradio_history_to_openai_messages(history, system_role):
    openai_messages = [{
        "role": "system",
        "content": system_role
    }]

    for one in history:
        openai_messages.append({
            "role": "user",
            "content": one[0],
        })

        openai_messages.append({
            "role": "assistant",
            "content": one[1],
        })

    return openai_messages


def get_gpt_chunk_tool_calls(chunk):
    return chunk.choices[0].delta.tool_calls


def save_file_by_content(chatbot_name, file_name, content):
    file_path = f"/static/{chatbot_name}_{file_name}"
    with open("." + file_path, 'wb') as file:
        file.write(content)

    return file_path


def create_file_url_path(req: Request, file_path: str):
    return req.request.base_url._url[:-1] + file_path


def get_openai_client():
    return openai.OpenAI(
        api_key="sk-COu3MKYRVWhzdiBjA1384891D999406b852e5a1a5442F075",
        base_url="https://one-api.bltcy.top/v1"
    )


def get_embeddings(embedding_input):
    # embedding_input = {
    #     "documents": embedding_input
    # }
    # print(type(embedding_input))
    # print(embedding_input)
    embeddings = get_openai_client().embeddings.create(
        model="text-embedding-ada-002",
        input=embedding_input,
        # input="The food was delicious and the waiter...",
        encoding_format="float"
    )

    embeddings_result = []
    for i in embeddings.data:
        embeddings_result.append(i.embedding)

    return embeddings_result
