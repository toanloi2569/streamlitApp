import json

import openai
import streamlit as st

from services.intent_detection import IntentDetector
from services.intent_func_mapper import IntentFuncMapper

st.title("FPT SmartCloud Assistant")

openai.api_key = st.secrets["OPENAI_API_KEY"]


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
    
    {question}
    """

    intent_detector = IntentDetector()
    intents, entities = intent_detector.detect(user_prompt)
    print('intents: ', intents)
    print('entities: ', entities)

    query_results = []
    intent_func_mapper = IntentFuncMapper()
    for intent in intents:
        func = intent_func_mapper.get_func(intent)
        print(func)
        query_result = func(entities)
        query_results.append(query_result)

    print('query_results: ', query_results)

    query_results_enriched = json.dumps({
        "text": user_prompt,
        "intents": intents,
        "entities": entities,
        "query_results": str(query_results)
    })

    processed_prompt = nlg_prompt_template.format(question=query_results_enriched)
    print('processed_prompt: ', processed_prompt)
    return processed_prompt


if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Tôi có thể giúp gì cho bạn?"):
    original_prompt = prompt
    prompt = preprocess(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(original_prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
