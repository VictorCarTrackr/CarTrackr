import streamlit as st

Favicon = "Images/favicon.png"
Logo = "Images/Logo.png"

st.set_page_config(
    page_title="Home",
    page_icon=Favicon
)

with st.sidebar:
    st.logo(Logo, size="large")
            

st.title("Hello, Streamlit!")

st.text_input("Enter some text:", key="input_text")

