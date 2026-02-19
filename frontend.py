import gradio as gr
import requests
import uuid

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
API_URL = "http://127.0.0.1:8000/api/v1/query"  # Change if deployed

# Generate persistent session id per browser session
def get_session_id():
    return str(uuid.uuid4())


# ─────────────────────────────────────────────
# API Call (FIXED)
# ─────────────────────────────────────────────
def call_backend(message, session_id):
    try:
        # Match the QueryRequest Pydantic model exactly
        payload = {
            "query": str(message), 
            "session_id": str(session_id) if session_id else None
        }

        response = requests.post(
            API_URL, 
            json=payload, 
            headers={"Content-Type": "application/json"}
        )
        
        # This will help you see the exact error in your console if it fails
        if response.status_code == 422:
            print(f"❌ Validation Error: {response.json()}")
            return "❌ Backend received invalid data format (422)."

        response.raise_for_status()
        data = response.json()

        # Extract based on your QueryResponse model
        return data.get("final_response", "No response generated.")

    except requests.exceptions.RequestException as e:
        return f"⚠️ API Error: {str(e)}"

# ─────────────────────────────────────────────
# Bot Response Logic (FIXED)
# ─────────────────────────────────────────────



# ─────────────────────────────────────────────
# Gradio UI
# ─────────────────────────────────────────────
with gr.Blocks(title="Multi-Agent Chatbot") as demo:

    session_state = gr.State(get_session_id())

    gr.Markdown("## 🤖 Multi-Agent AI Assistant")

    chatbot = gr.Chatbot(height=500)

    msg = gr.Textbox(
        placeholder="Ask something...",
        container=False,
        scale=7
    )

    clear = gr.Button("Clear Chat")

    def user_message(message, history):
        # Add user message
        history.append({"role": "user", "content": message})
        return "", history

    def bot_response(history, session_id):
        # Ensure history isn't empty and get the last user message string
        if not history or "content" not in history[-1]:
            return history
            
        user_msg = history[-1]["content"]
        
        # We only pass message and session_id to match the API requirements
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
