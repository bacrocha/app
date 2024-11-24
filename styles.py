import streamlit as st


def apply_custom_styles():
    st.markdown("""
        <style>
            .main {
                padding: 2rem;
            }
            .stButton>button {
                width: 100%;
                background-color: #4CAF50;
                color: white;
                padding: 0.5rem;
                border-radius: 5px;
                border: none;
            }
            .stButton>button:hover {
                background-color: #45a049;
            }
            .error-msg {
                color: #ff0000;
                padding: 1rem;
                border-radius: 5px;
                background-color: #ffe6e6;
            }
            .success-msg {
                color: #4CAF50;
                padding: 1rem;
                border-radius: 5px;
                background-color: #f0fff0;
            }
            .st-emotion-cache-1y4p8pa {
                padding: 2rem;
                border-radius: 10px;
                background-color: #f8f9fa;
            }
            .stWarning {
                background-color: #fff3cd;
                padding: 1rem;
                border-radius: 5px;
                border-left: 5px solid #ffc107;
            }
            .development-warning {
                background-color: #f8f9fa;
                padding: 2rem;
                border-radius: 10px;
                margin: 1rem 0;
            }
        </style>
    """, unsafe_allow_html=True)
