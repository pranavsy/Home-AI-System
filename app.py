import streamlit as st
import requests
import json
import time
import base64
from io import BytesIO
import os

MAC_MINI_IP = os.getenv("BACKEND_HOST", "192.168.1.15")
LM_STUDIO_PORT = os.getenv("BACKEND_PORT", 1234)
try:
    LM_STUDIO_PORT = int(LM_STUDIO_PORT)
except ValueError:
    LM_STUDIO_PORT = 1234

LM_STUDIO_ENDPOINT = f"http://{MAC_MINI_IP}:{LM_STUDIO_PORT}/v1/chat/completions"

def encode_image(image_bytes, mime_type):
    base64_encoded_data = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:{mime_type};base64,{base64_encoded_data}"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file_info" not in st.session_state:
    st.session_state.uploaded_file_info = None

st.set_page_config(page_title="Local AI Chat", layout="wide")

with st.sidebar:
    st.title("🔒 Private AI")
    st.markdown(f"Backend: `{MAC_MINI_IP}:{LM_STUDIO_PORT}`")
    st.divider()

    uploaded_file = st.file_uploader(
        "Upload Image (Optional)",
        type=["png", "jpg", "jpeg", "bmp", "gif"],
        help="Requires a multimodal model loaded in the backend."
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_name = uploaded_file.name
        file_type = uploaded_file.type

        if st.session_state.uploaded_file_info is None or st.session_state.uploaded_file_info["name"] != file_name:
            st.session_state.uploaded_file_info = {
                "name": file_name,
                "type": file_type,
                "bytes": file_bytes
            }
            if file_type.startswith("image/"):
                st.image(file_bytes, caption=f"Ready: {file_name}", width=200)
                st.session_state.uploaded_file_info["data_url"] = encode_image(file_bytes, file_type)
            else:
                st.info(f"Uploaded file: {file_name} ({file_type}). Cannot process non-image content.")
                if "data_url" in st.session_state.uploaded_file_info:
                    del st.session_state.uploaded_file_info["data_url"]

    if st.session_state.uploaded_file_info is not None:
        if st.button("Clear Uploaded File", key="clear_file_button"):
            st.session_state.uploaded_file_info = None
            st.rerun()

    st.divider()
    st.header("Actions")
    if st.button("Clear Chat History", key="clear_chat_button"):
        st.session_state.messages = []
        st.session_state.uploaded_file_info = None
        st.rerun()

st.title("Local AI Chat")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], list):
            image_name = message.get('image_name', 'Uploaded Image')
            for item in message["content"]:
                if item["type"] == "text":
                    st.markdown(item["text"])
                elif item["type"] == "image_url":
                    st.markdown(f"_(Image: {image_name})_")
        else:
            st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything..."):
    user_message_content = [{"type": "text", "text": prompt}]
    current_file_info = st.session_state.uploaded_file_info
    image_name_for_history = None

    if current_file_info and "data_url" in current_file_info:
        image_url = current_file_info["data_url"]
        image_name_for_history = current_file_info["name"]
        user_message_content.append({
            "type": "image_url",
            "image_url": {"url": image_url}
        })
        st.toast(f"Sending prompt with image: {image_name_for_history}", icon="🖼️")

    st.session_state.messages.append({
        "role": "user",
        "content": user_message_content,
        "image_name": image_name_for_history
    })

    with st.chat_message("user"):
        for item in user_message_content:
            if item["type"] == "text":
                st.markdown(item["text"])
            elif item["type"] == "image_url":
                 st.markdown(f"_(Image: {image_name_for_history})_")

    st.session_state.uploaded_file_info = None

    messages_for_api = []
    for msg in st.session_state.messages:
        content_to_send = msg["content"]
        if isinstance(content_to_send, list):
             serializable_content = []
             for item in content_to_send:
                 if item["type"] == "text":
                     serializable_content.append({"type": "text", "text": item["text"]})
                 elif item["type"] == "image_url" and "image_url" in item and "url" in item["image_url"]:
                     serializable_content.append({
                         "type": "image_url",
                         "image_url": {"url": item["image_url"]["url"]}
                     })
             content_to_send = serializable_content
        elif isinstance(content_to_send, str):
             content_to_send = content_to_send
        messages_for_api.append({"role": msg["role"], "content": content_to_send})

    api_payload = {
        "model": "loaded-model-name",
        "messages": messages_for_api,
        "temperature": 0.7,
        "max_tokens": 1500,
        "stream": False,
    }
    headers = {"Content-Type": "application/json"}

    try:
        with st.chat_message("assistant"):
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown("...")
            start_time = time.time()

            response = requests.post(LM_STUDIO_ENDPOINT, headers=headers, json=api_payload, timeout=300)
            response.raise_for_status()
            end_time = time.time()

            ai_response_data = response.json()

            if "choices" in ai_response_data and len(ai_response_data["choices"]) > 0:
                ai_content = ai_response_data["choices"][0]["message"]["content"].strip()
                thinking_placeholder.markdown(ai_content)
            else:
                ai_content = "Error: Received an unexpected response format."
                thinking_placeholder.error(f"Unexpected API response: {ai_response_data}")

        st.session_state.messages.append({"role": "assistant", "content": ai_content})

    except requests.exceptions.RequestException as e:
        st.error(f"API Request Error: Could not connect or communicate with backend at {LM_STUDIO_ENDPOINT}. Details: {e}")
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
             st.session_state.messages.pop()
        if 'thinking_placeholder' in locals(): thinking_placeholder.empty()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
             st.session_state.messages.pop()
        if 'thinking_placeholder' in locals(): thinking_placeholder.empty()

    st.rerun()
