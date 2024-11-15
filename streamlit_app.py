import streamlit as st
from openai import OpenAI

# アプリのタイトルと説明
st.title("🖼️ Image Prompt Generator and Creator")
st.write(
    "This app allows you to generate detailed prompts for AI-based image creation and visualize the results using OpenAI's DALL·E model. "
    "To use this app, you need an OpenAI API key, which you can obtain [here](https://platform.openai.com/account/api-keys)."
)

# OpenAI APIキーの入力
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # OpenAIクライアントの作成
    client = OpenAI(api_key=openai_api_key)

    # セッションの初期化
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "image_history" not in st.session_state:
        st.session_state.image_history = []

    # サイドバーにオプションを追加
    st.sidebar.header("🎨 Image Generation Options")
    style = st.sidebar.selectbox(
        "Select Style",
        ["Realistic", "Cartoon", "Abstract", "Cyberpunk", "Vintage"]
    )
    theme = st.sidebar.text_input("Theme (e.g., sunset, futuristic city)")
    additional_details = st.sidebar.text_area("Additional Details")

    # プロンプト生成用の関数
    def generate_image_prompt(theme, style, additional_details):
        prompt = f"{theme}, in {style} style"
        if additional_details:
            prompt += f", {additional_details}"
        return prompt

    # プロンプトの生成
    image_prompt = generate_image_prompt(theme, style, additional_details)
    st.sidebar.write(f"Generated Prompt: `{image_prompt}`")

    # メイン画面に入力フォームを表示
    st.subheader("Chat Interface")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input("Describe the image you want to create or ask a question:"):
        # 入力をセッションに保存
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # プロンプト生成の処理
        if "generate" in user_input.lower():  # 例: "generate an image of..."
            with st.chat_message("assistant"):
                st.markdown(f"Generating an image for: `{image_prompt}`")

            # DALL·E APIを使って画像生成
            try:
                response = client.image.create(
                    prompt=image_prompt,
                    n=1,
                    size="1024x1024"
                )
                image_url = response['data'][0]['url']

                # 画像を表示
                st.image(image_url, caption="Generated Image", use_column_width=True)
                st.session_state.image_history.append({"prompt": image_prompt, "url": image_url})
                st.session_state.messages.append({"role": "assistant", "content": f"Image generated for: `{image_prompt}`"})
            except Exception as e:
                st.error(f"Error generating image: {e}")
        else:
            # テキストのみの応答
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            )
            assistant_response = response['choices'][0]['message']['content']
            with st.chat_message("assistant"):
                st.markdown(assistant_response)
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})

    # 履歴の表示
    st.subheader("🕒 Image Generation History")
    if st.session_state.image_history:
        for entry in st.session_state.image_history:
            st.write(f"Prompt: {entry['prompt']}")
            st.image(entry['url'], width=200)
    else:
        st.info("No images generated yet.", icon="📂")
