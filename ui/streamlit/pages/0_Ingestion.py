import streamlit as st
import ingestion.pipeline as ingestion
from io import StringIO
from pathlib import Path

st.set_page_config(
    page_title="SEC EDGAR Filings - Data Ingestion",
    page_icon="🧠",
    layout="wide",
)

st.title("SEC EDGAR Filings - Data Ingestion")

with st.form("ingestion_form"):
   uploaded_file = st.file_uploader('Upload SEC EDGAR Filing', type=['txt'])
   # Every form must have a submit button.
   submitted = st.form_submit_button("Submit")
   if submitted:
       with st.spinner('Processing the Transcript...'):
         if uploaded_file is not None:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            string_data = stringio.read()
            res = ingestion.run_pipeline(Path(uploaded_file.name).stem, string_data)
            if res is not None:
               st.success('Done!')
               with st.expander("See Generated Cypher"):
                  st.markdown(f"""
                              ```
                              {res}
                              ```
                  """)
            else:
               st.error("The Filing could not be ingested now. Try again later.")
         else:
            st.error("Please upload an SEC File")