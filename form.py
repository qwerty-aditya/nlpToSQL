import streamlit as st
import requests
import time
import json
from PIL import Image
import pandas as pd

URL = "http://127.0.0.1:5000"
image_dir = "images/valiance.png"

def stick_it_good():
    # make header sticky.
    st.markdown(
        """
            <div class='fixed-header'/>
            <style>
                div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
                    position: sticky;
                    top: 2.875rem;
                    background-color: white;
                    z-index: 999;
                }
                .fixed-header {
                    border-bottom: 1px solid black;
                }
            </style>
        """,
        unsafe_allow_html=True,
    )

def generate_response(user_input):
    # initialize pinecone
    r = st.session_state["session"].get(
        url=URL + "/input/", params={"user_input": user_input}
    )
    return r

def main():
    # Initialise session
    if "session" not in st.session_state:
        st.session_state["session"] = requests.Session()
        r = st.session_state["session"].get(url=URL + "/")
        print(r)

    main_container = st.container()
    with main_container:
        logo = Image.open(f"{image_dir}")
        main_container.image(logo, width=250)
        st.title("Generative BI")
        stick_it_good()

    title = st.text_input('Query upon the data',
                          'SELECT * FROM insights LIMIT1;')
    response_list = generate_response(title)
    if response_list.json() == {}:
        st.write('write correct query')
    else:
        df = pd.DataFrame.from_dict(response_list.json(), orient="index")
        st.dataframe(df)


if __name__ == "__main__":
    main()