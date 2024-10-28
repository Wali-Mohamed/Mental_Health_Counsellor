import streamlit as st
import base64
import uuid
import test_db
from rag import rag
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string
def load_css(base64_image):
    # CSS to inject containing the styles.
    css = f"""
    <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{base64_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Adding an overlay */
        .overlay {{
            position: fixed;
            top: 0;
            left: 0;
            height: 100%;
            width: 100%;
            background-color: rgba(0, 0, 0, 0.5); /* Black background with opacity */
            z-index: -1; /* Ensures that the overlay is behind the content */
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    # Add an overlay div
    st.markdown('<div class="overlay"></div>', unsafe_allow_html=True)
def main():
    st.set_page_config(page_title="Mental Health Assistant", layout="wide")

    # Debug section in sidebar
    with st.sidebar:
        with st.expander("Debug Tools", expanded=True):
            if st.button("Check Database Tables"):
                test_db.check_tables()
                test_db.list_recent_conversations()
            
            st.write("Test Feedback Submission")
            # Get the most recent conversation ID for testing
            test_conversation_id = st.text_input(
                "Test Conversation ID", 
                value="test-conversation-id"
            )
            test_feedback = st.selectbox(
                "Test Feedback Value",
                options=[1, -1],
                format_func=lambda x: "Positive" if x == 1 else "Negative"
            )
            if st.button("Submit Test Feedback"):
                try:
                    feedback_id = test_db.save_feedback(test_conversation_id, test_feedback)
                    st.success(f"Feedback saved successfully with ID: {feedback_id}")
                except Exception as e:
                    st.error(f"Failed to save feedback: {str(e)}")
                    st.error(f"Error type: {type(e)}")

        # Main app content
        image_path = "./images/mental_health.jpg"
        base64_image = get_base64_image(image_path)
        load_css(base64_image)

        st.markdown('<div class="centered">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="input-container">
                <h1>Welcome to the Mental Health Assistant</h1>
                <p>How can I assist you today?</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        buff, col, buff2 = st.columns([1,3,1])
        question = col.text_input(':blue[**Enter your question here:**]')

        if col.button("Ask"):
            if question:
                conversation_id = str(uuid.uuid4())
                try:
                    answer = rag(question)
                    st.write("Answer:", answer)

                    # Save conversation first
                    test_db.save_conversation(
                        conversation_id=conversation_id,
                        question=question,
                        answer_data=answer,
                    )
                    st.success(f"Conversation saved with ID: {conversation_id}")

                    # Collect feedback
                    feedback = st.radio(
                        "Was this answer helpful?", 
                        ["Yes", "No"], 
                        key=f"feedback_{conversation_id}"
                    )
                    
                    if st.button("Submit Feedback", key=f"feedback_btn_{conversation_id}"):
                        feedback_value = 1 if feedback == "Yes" else -1
                        try:
                            feedback_id = test_db.save_feedback(conversation_id=conversation_id, feedback=feedback_value)
                            st.success(f"Feedback saved successfully with ID: {feedback_id}")
                        except Exception as e:
                            st.error(f"Error saving feedback: {str(e)}")

                except Exception as e:
                    st.error(f"Error: {str(e)}")

            else:
                st.error("Please enter a question.")

        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
