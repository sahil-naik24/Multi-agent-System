import gradio as gr
import requests
import uuid

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
API_URL = "http://127.0.0.1:8000/api/v1/query"
UPLOAD_URL = "http://127.0.0.1:8000/api/v1/upload"

# Generate persistent session id per browser session
def get_session_id():
    return str(uuid.uuid4())


# ─────────────────────────────────────────────
# API Call (FIXED)
# ─────────────────────────────────────────────
def call_backend(message, session_id):
    try:
        payload = {
            "query": str(message), 
            "session_id": str(session_id) if session_id else None
        }

        response = requests.post(
            API_URL, 
            json=payload, 
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 422:
            print(f"❌ Validation Error: {response.json()}")
            return "❌ Backend received invalid data format (422)."

        response.raise_for_status()
        data = response.json()

        return data.get("final_response", "No response generated.")

    except requests.exceptions.RequestException as e:
        return f"⚠️ API Error: {str(e)}"


# ─────────────────────────────────────────────
# File Upload Logic
# ─────────────────────────────────────────────
def upload_files(files):
    if not files:
        return "⚠️ No files selected."

    try:
        file_tuples = []
        for file in files:
            file_tuples.append(
                ("files", (file.name.split("/")[-1], open(file.name, "rb")))
            )

        response = requests.post(UPLOAD_URL, files=file_tuples)

        if response.status_code == 422:
            print(f"❌ Upload Validation Error: {response.json()}")
            return "❌ Upload failed: invalid data format (422)."

        response.raise_for_status()
        return f"✅ {len(files)} file(s) uploaded successfully."

    except requests.exceptions.RequestException as e:
        return f"⚠️ Upload Error: {str(e)}"


# ─────────────────────────────────────────────
# Gradio UI
# ─────────────────────────────────────────────
with gr.Blocks(title="Multi-Agent Chatbot") as demo:

    session_state = gr.State(get_session_id())

    with gr.Row():

        # ── Sidebar ──────────────────────────────
        with gr.Column(scale=1, min_width=220):
            gr.Markdown("### 📁 Upload Files")
            file_input = gr.File(
                label="Select files",
                file_count="multiple",
                type="filepath"
            )
            upload_btn = gr.Button("Upload", variant="primary")
            upload_status = gr.Textbox(
                label="Status",
                interactive=False,
                lines=2
            )

            upload_btn.click(
                upload_files,
                inputs=[file_input],
                outputs=[upload_status]
            )

        # ── Main Chat Area ────────────────────────
        with gr.Column(scale=4):
            gr.Markdown("## 🤖 Multi-Agent AI Assistant")

            chatbot = gr.Chatbot(height=500)

            msg = gr.Textbox(
                placeholder="Ask something...",
                container=False,
                scale=7
            )

            clear = gr.Button("Clear Chat")

            def user_message(message, history):
                history.append({"role": "user", "content": message})
                return "", history

            def bot_response(history, session_id):
                if not history or "content" not in history[-1]:
                    return history
                    
                user_msg = history[-1]["content"]
                response = call_backend(user_msg, session_id)
                history.append({"role": "assistant", "content": response})
                return history

            msg.submit(
                user_message,
                [msg, chatbot],
                [msg, chatbot],
                queue=False
            ).then(
                bot_response,
                [chatbot, session_state],
                chatbot
            )

            clear.click(lambda: [], None, chatbot, queue=False)


# ─────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────
if __name__ == "__main__":
    demo.launch(server_port=7860)