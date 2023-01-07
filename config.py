import os
if os.environ.get("OPENAPI_KEY"):
  open_api_key = os.environ.get('OPENAPI_KEY')
else:
  import streamlit as st
  open_api_key = st.secrets['OPENAPI_KEY']
