
import json 
import requests 
from streamlit_extras.app_logo import add_logo
import streamlit as st 
from streamlit_lottie import st_lottie 
from streamlit_extras.switch_page_button import switch_page


add_logo("images/htpd_text.png", height=100)


path = "images/research_animation.json"
with open(path,"r") as file: 
    url = json.load(file) 

st.markdown("""
<style>
.research {
    font-size: 100px;
    font-weight: bold;
    text-align: center;
    color: purple;
    display:inline;
}
            
.xpress {
    font-size: 100px;
    font-weight: bold;
    text-align: center;
    color: green;   
    display:inline;
}

.icon {
}
            
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; padding-top: 0rem;'><p class='research'>research<p class='xpress'>Xpress</p></h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: Black;'>Synthesize Research Evidence through AI Capabilities</h4>", unsafe_allow_html=True)

st_lottie(url, 
    loop=True, 
    quality='high',
    key='second'
    )
      
   
col1, col2, col3 , col4, col5 = st.columns(5)

with col1:
    pass
with col2:
    pass
with col4:
    pass
with col5:
    pass
with col3:
    get_started = st.button('Get Started', key = 'get_started')
    if get_started:
        switch_page("get started")
