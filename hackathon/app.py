import json

import openai
import streamlit as st
import tiktoken
from openai import InvalidRequestError
# from ui.post_process import message_func, format_message

from config import config
from services.intent_detection import IntentDetector
from services.intent_func_mapper import IntentFuncMapper
from bs4 import BeautifulSoup
import datetime
import pandas as pd

openai.api_key = config.OPENAI_API_KEY
max_message_stack_size = 8

INITIAL_MESSAGE = [
    {
        "role": "assistant",
        "content": "Xin chào, mình là trợ lý ảo của FPT SmartCloud. Bạn có thể hỏi mình về các dự án đang triển khai của FPT SmartCloud.",
    }
]


def clean_text(html_text):
    # Sử dụng BeautifulSoup để phân tích văn bản HTML
    soup = BeautifulSoup(html_text, 'html.parser')

    # Loại bỏ tất cả các HTML tag và giữ lại nội dung văn bản
    clean_text = soup.get_text()

    return clean_text


def set_page_title_and_icon():
    st.markdown("""
        <style>
            .big-font {
                font-size:50px !important;
                font-weight: bold; /* In đậm */
                color: black;
            }
            .caption {
                font-size:15px !important;
            }
        </style>
        """,
        unsafe_allow_html=True)

    st.markdown('<p class="big-font">Carbon Assistant 💎</p>', unsafe_allow_html=True)


def create_dataframe(table_data):
    n_data = []
    for row in table_data['result']:
        n_row = []
        for cell in row:
            if isinstance(cell, str):
                cell = clean_text(cell)
            n_row.append(cell)
        n_data.append(tuple(n_row))
    df = pd.DataFrame(n_data, columns=table_data['columns'])
    return df


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

    query_results = []
    intent_func_mapper = IntentFuncMapper()

    if len(intents) == 1 and intents[0] == 'other':
        return user_prompt, intents[0], None

    for intent in intents:
        func = intent_func_mapper.get_func(intent)
        query_result = func(entities)
        query_results.append(query_result)

    query_results_enriched = json.dumps({
        "text": user_prompt,
        "intents": intents,
        "entities": entities,
        "query_results": str(query_results)
    }, ensure_ascii=False)

    print(query_results_enriched)
    processed_prompt = nlg_prompt_template.format(question=query_results_enriched)
    intent = intents[0]
    table_result = query_results[0]
    print(table_result)
    return processed_prompt, intent, table_result


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def format_message(text):
    return text.replace('```', '')


with open("ui/sidebar.md", "r") as sidebar_file:
    sidebar_content = sidebar_file.read()
with open("ui/styles.md", "r") as styles_file:
    styles_content = styles_file.read()

# Call the function to set the title and icon
set_page_title_and_icon()

st.sidebar.markdown(sidebar_content)
st.write(styles_content, unsafe_allow_html=True)

if st.button("Reset Chat"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.session_state["messages"] = []


if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = INITIAL_MESSAGE

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
            prompt, intent, table_result = preprocess(prompt)
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
            message_placeholder.markdown(format_message(full_response))
            if intent == "get_project_activities":
                df = create_dataframe(table_result)
                st.data_editor(df)
            st.session_state.messages.append({"role": "user", "content": original_prompt})
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except InvalidRequestError as e:
            st.error(f"OpenAI API error: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")


