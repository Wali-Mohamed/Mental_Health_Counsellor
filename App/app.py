import streamlit as st
import base64
import uuid
import db
from rag import rag  # Assuming 'rag' is your custom function for generating answers

# Function to encode the local image file as base64
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

def load_css(base64_image):
    """Load CSS for styling the app."""
    st.markdown(
        f"""
        <style>
        .stApp {{
             position: relative;
            background-image: url("data:image/jpg;base64,{base64_image}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            height: 100vh;  /* Full height */
            overflow:auto;

        }}
        # /* Adding a darker overlay on top of the background */
        # .stApp::before {{
        #     content: "";
        #     position: absolute;
        #     top: 0;
        #     left: 0;
        #     right: 0;
        #     bottom: 0;
        #     background-color: rgba(0, 0, 0, 0.5);  /* Black overlay with 50% opacity */
        #     z-index: 1;  /* Place overlay above background image */
        # }}
        /* Container styling to position content above the overlay */
        .centered {{
            display: flex;
            position:relative;
            z-index: 2; /* Position content above overlay */
            flex-direction: column;
            align-items: center;
            padding: 10px;
            justify-content: center;
            color:white;
           
        }}
        .input-container {{
            background-color: rgba(255, 255, 255, 0.8);
            padding: 20px;
            border-radius: 10px;
            width: 80%;
            max-width: 800px;
            box-shadow: 0px 4px 8px rgba(0,0,0,0.1);
            margin:auto;
        }}
        
        input, button {{
            width: 80%;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ccc;
            display: block;
            margin: 10px auto;
        }}
        button {{
            cursor: pointer;
            background-color: #4CAF50;
            color: white;
            font-size: 16px;
            display: block;
            margin: 10px auto;
        }}
        
       
        .stButton > button:hover {{
        background-color: #4CAF50;
        color: white;
        }}
       
        /* Target the input field within the Streamlit text input widget */
        .stTextInput > div > div > input {{
            width: 100% !important;  /* Set width to 70% */
            color: #FF5733 !important;  /* Set text color */
            font-size: 16px !important;  /* Set font size */
            border: 1px solid #cccccc !important;  /* Optional: border color */
            padding: 10px !important;  /* Optional: add padding */
            border-radius: 20px;  /* Optional: rounded corners */
        }}
        .stButton > button {{
            display: block;
            margin: 5px auto;  /* Center-align the button */
            border: 1px solid #4CAF50;
            outline: none;
            width: 25%;  /* Set button width */
            height: 60px;
            font-size: 16px;
            color: #4CAF50;
            background-color: white;
            text_align:center;
    }}
    .answer {{
                background-color: #f0f2f6;  /* Light grey background */
                padding: 10px;
                border-radius: 5px;
                margin: 10px auto;
                width:75%;
            }}
    /* Centering the radio buttons */
    .stRadio > div {{
        display: flex;
        justify-content: center;
    }}
    .centered-radio {{
                text-align: center;
                font-size: 16px;
                margin-top: 20px;
                margin-bottom: 5px;
            }}
    .stTextInput label {{
                font-size: 40px; /* Increase the font size of the input label */
            }}
        
        </style>
        """,
        unsafe_allow_html=True
    )
def print_log(message):
    print(message, flush=True)

def main():
    st.set_page_config(page_title="Mental Health Assistant", layout="wide")

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

    question=col.text_input('**Enter your question here:**')
    
    
    # Initialize or maintain the state of last_answer and last_conversation_id
    if 'last_answer' not in st.session_state:
        st.session_state['last_answer'] = None
        st.session_state['last_conversation_id'] = None

    if col.button("Ask"):
        print_log("ask button pressed.")
        
        if question:
            conversation_id = str(uuid.uuid4())
            try:
                answer = rag(question)  # Process the question through your rag function
                # Display the answer with custom CSS
                answer = rag(question)  # Process the question through your rag function
                st.session_state['last_answer'] = answer  # Store the answer in session state
                st.session_state['last_conversation_id'] = conversation_id            
               
                
                db.save_conversation(
                    conversation_id=conversation_id,
                    question=question,
                    answer_data=answer,
                )
                st.session_state['last_answer'] = answer  # Store the answer in session state
                st.session_state['last_conversation_id'] = conversation_id
                
                
            except Exception as e:
                st.error("There was an issue processing your question. Please try again later.")
                print_log(f"Error generating answer or saving conversation: {e}")
        else:
           st.error("Please enter a question.")
    if st.session_state.get('last_answer'):
        st.markdown(f"<div class='answer'>{st.session_state['last_answer']}</div>", unsafe_allow_html=True)    
   
    if 'last_conversation_id' in st.session_state:
        st.markdown("<div class='centered-radio'>Was this answer helpful?</div>", unsafe_allow_html=True)
        feedback = st.radio("", ["Yes", "No"], key="feedback_radio",horizontal=True, label_visibility="collapsed")  
        
        if st.button("Submit Feedback", key=f"submit_feedback_button"):
             
            conversation_id = st.session_state['last_conversation_id']
            print_log("Ask feedbaack button pressed.")  # Confirm this is printed
            feedback_value = 1 if feedback == "Yes" else -1
            
            try:
                # Check the type of feedback_value and ensure it's an integer
                if not isinstance(feedback_value, int):
                    st.error("Invalid feedback value type.")
                    print_log(f"Invalid type for feedback_value: {type(feedback_value)}")
                else:
                    # Confirm feedback value and conversation ID before saving
                    print_log(f"Conversation ID: {conversation_id} and Feedback Value: {feedback_value}")
                    st.success(f"Feedback received: {'Positive' if feedback_value == 1 else 'Negative'}")
                    db.save_feedback(conversation_id=conversation_id, feedback=feedback_value)
            except Exception as e:
                st.error("There was an issue processing your question. Please try again later.")
                print_log(f"Error generating answer or saving conversation: {e}")
        

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
