import json

import openai
import streamlit as st
import tiktoken

from config import config
from services.intent_detection import IntentDetector
from services.intent_func_mapper import IntentFuncMapper


INITIAL_MESSAGE = [
    {"role": "user", "content": "Xin chào !"},
    {
        "role": "assistant",
        "content": "Chào bạn, mình là trợ lý ảo của FPT SmartCloud. Bạn có thể hỏi mình về các dự án đang triển khai của FPT SmartCloud.",
    },
]


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

# Call the function to set the title and icon
set_page_title_and_icon()

openai.api_key = config.OPENAI_API_KEY
max_message_stack_size = 8

table_data = [1]

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
    Nếu dữ liệu có cấu trúc, hãy thể hiện dưới dạng bảng.
    Nếu dữ liệu có project_name, hãy thêm thông tin project_name vào câu trả lời.
    
    {question}
    """

    intent_detector = IntentDetector()
    intents, entities = intent_detector.detect(user_prompt)

    query_results = []
    intent_func_mapper = IntentFuncMapper()
    for intent in intents:
        func = intent_func_mapper.get_func(intent)
        query_result = func(entities)
        query_results.append(query_result)
        print(query_result)

    query_results_enriched = json.dumps({
        "text": user_prompt,
        "intents": intents,
        "entities": entities,
        "query_results": str(query_results)
    })
    table_data = query_results[0]
    processed_prompt = nlg_prompt_template.format(question=query_results_enriched)
    return processed_prompt

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


with open("ui/sidebar.md", "r") as sidebar_file:
    sidebar_content = sidebar_file.read()
with open("ui/styles.md", "r") as styles_file:
    styles_content = styles_file.read()


st.sidebar.markdown(sidebar_content)

if st.button("Reset Chat"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.session_state["messages"] = INITIAL_MESSAGE

st.write(styles_content, unsafe_allow_html=True)


if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = INITIAL_MESSAGE

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
import pandas as pd
from datetime import datetime

data = {
    'subject': ['Bot FE-CS không có file thiết kế kịch bản'],
    'startDate': [datetime(2023, 7, 26)],
    'description': ['<p>Dự án đã hoàn thành từ lâu. PM Fsoft/BA là Hội đã nghỉ. Trải qua nhiều lượt BA/Bot builder maintain. Không có file thiết kế kịch bản</p>'],
    'rootCause': [''],
    'dueDate': [datetime(2023, 8, 3)],
    'correctiveAction': ['<ul><li><p>Làm tài liệu kịch bản bot</p></li></ul>'],
    'preventiveAction': [''],
    'criticalLevel': ['High'],
    'status': ['Solving'],
    'closedDate': [None],
}

columns = [
    'subject', 'startDate', 'description', 'rootCause', 'dueDate',
    'correctiveAction', 'preventiveAction', 'criticalLevel', 'status', 'closedDate'
]

df = pd.DataFrame(data, columns=columns)

if prompt := st.chat_input("Tôi có thể giúp gì cho bạn?"):
    original_prompt = prompt
    prompt = preprocess(prompt)
    with st.chat_message("user"):
        st.markdown(original_prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages]
        while num_tokens_from_string(json.dumps(messages), 'cl100k_base') > 500:
            messages.pop(0)
        messages.append({"role": "user", "content": prompt})
        for response in openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=messages,
            stream=True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "user", "content": original_prompt})
    st.session_state.messages.append({"role": "assistant", "content": full_response})

if len(table_data) > 0:
    edited_df = st.data_editor(df) # 👈 this is a widget
