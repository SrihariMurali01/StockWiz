import streamlit as st
import requests

# Initialize session state for storing chat history and chart path
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'chart' not in st.session_state:
    st.session_state['chart'] = None

st.title("Stock Market Chatbot")

# Display chat history and scroll to the bottom
if st.session_state['history']:
    chat_output = ""
    for i, chat in enumerate(st.session_state['history']):
        chat_output += f"**You**: {chat['user']}\n\n**Bot**: {chat['bot']}\n\n---\n"
    
    st.markdown(chat_output)

    # Display the chart if available
    if st.session_state['chart']:
        st.image(st.session_state['chart'])

    # Add a script to scroll to the bottom of the chat
    st.markdown("""
        <script>
        var chatBox = window.parent.document.querySelector('section.main');
        chatBox.scrollTop = chatBox.scrollHeight;
        </script>
        """, unsafe_allow_html=True)

# Place the text input at the bottom
user_message = st.text_input("Type your message here:")

if st.button("Send"):
    if user_message:
        # Send the user message to the Flask backend
        response = requests.post(
            "http://localhost:5000/chat",  # Make sure the Flask app is running on this address
            json={"message": user_message}
        )
        
        if response.status_code == 200:
            data = response.json()
            bot_response = data.get("response", "")
            chart_path = data.get("chart", None)
            # Append user message and bot response to chat history
            st.session_state['history'].append({"user": user_message, "bot": bot_response})
            # Store the chart path
            st.session_state['chart'] = chart_path
        else:
            st.session_state['history'].append({"user": user_message, "bot": "Error: Could not retrieve response."})

    # Refresh the page to show the new message at the bottom
    st.rerun()
