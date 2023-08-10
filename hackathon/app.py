import json

import openai
import streamlit as st
import tiktoken
from openai import InvalidRequestError

from config import config
from services.intent_detection import IntentDetector
from services.intent_func_mapper import IntentFuncMapper

st.title("FPT SmartCloud Assistant")

openai.api_key = config.OPENAI_API_KEY
max_message_stack_size = 8


def preprocess(user_prompt):
    nlg_prompt_template = """
    Bạn là một trợ lý ảo và hỗ trợ người dùng trả lời câu hỏi. 
    Dữ liệu được hỏi đã được truy vấn từ cơ sở dữ liệu của FPT SmartCloud và được lưu trữ dưới dạng json có cấu trúc như sau:
    {{
        "text": "Câu hỏi của người dùng",
        "intents": ["danh sách các intent được phát hiện"],
        "entities": ["danh sách các entity được phát hiện"],
        "query_results": ["danh sách các kết quả truy vấn"]
    }}
    Bạn hãy trả lời câu hỏi của người dùng dựa trên các kết quả truy vấn được lưu trữ trong biến query_results.
    Nếu dữ liệu có cấu trúc, hãy hiển thị dạng numbering list.
    Chỉ cần trả lời đúng câu hỏi, không cần giải thích.
    
    {question}
    """

    intent_detector = IntentDetector()
    intents, entities = intent_detector.detect(user_prompt)
    print('intents: ', intents)
    print('entities: ', entities)

    query_results = []
    intent_func_mapper = IntentFuncMapper()

    if len(intents) == 1 and intents[0] == 'other':
        return user_prompt

    for intent in intents:
        func = intent_func_mapper.get_func(intent)
        query_result = func(entities)
        query_results.append(query_result)

    print('query_results: ', query_results)
    query_results_enriched = json.dumps({
        "text": user_prompt,
        "intents": intents,
        "entities": entities,
        "query_results": str(query_results)
    }, ensure_ascii=False)

    processed_prompt = nlg_prompt_template.format(question=query_results_enriched)
    return processed_prompt


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Tôi có thể giúp gì cho bạn?"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            original_prompt = prompt
            prompt = preprocess(prompt)
            messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
            messages.append({"role": "user", "content": prompt})
            while num_tokens_from_string(json.dumps(messages), 'cl100k_base') > 500 and len(messages) > 1:
                messages.pop(0)

            for response in openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=messages,
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        except InvalidRequestError as e:
            st.error(f"OpenAI API error: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

    st.session_state.messages.append({"role": "user", "content": original_prompt})
    st.session_state.messages.append({"role": "assistant", "content": full_response})
