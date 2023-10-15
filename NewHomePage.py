
import json 
import requests 
  
import streamlit as st 
from streamlit_lottie import st_lottie 

# For the st lottie
path = "images/research_animation.json"
with open(path,"r") as file: 
    url = json.load(file) 



#First segment of title
with st.container():
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

st.markdown('#') 


#Another container
with st.container():
    left_column, right_column = st.columns(2)
    with left_column:
        st.header("Purpose")
        st.write("##")
        st.write('With our dashboard, you can quickly assess the key points, methods, and findings in those dense articles, making the research process smoother and faster!')
        st.button("Get Started", type="secondary")

    with right_column:
        st_lottie(url, 
            height=300, 
            width=400, 
            loop=True, 
            quality='high',
            key='research_lottie'
            )



        




