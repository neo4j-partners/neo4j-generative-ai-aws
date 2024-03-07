import boto3
import streamlit as st
import json

SERVICE_NAME=st.secrets['SERVICE_NAME']
REGION_NAME=st.secrets['REGION_NAME']
bedrock = boto3.client(
 service_name=SERVICE_NAME,
 region_name=REGION_NAME,
 endpoint_url=f'https://{SERVICE_NAME}.{REGION_NAME}.amazonaws.com',
 aws_access_key_id=st.secrets["ACCESS_KEY"],
 aws_secret_access_key=st.secrets["SECRET_KEY"]
)

def get_client():
    return bedrock

model_name = st.secrets["MULTIMODAL_MODEL"]
if model_name == '':
    model_name = 'anthropic.claude-3-sonnet-20240229-v1:0'

def call_language_model(prompt_data):
    try:
        body = json.dumps({"messages": [{"role": "user", "content": f"{prompt_data}"}],
                           "temperature":0,
                           "top_k":1, "top_p":0.88,
                           "anthropic_version":"bedrock-2023-05-31",
                           "max_tokens": 50000})
        modelId = model_name # change this to use a different version from the model provider
        accept = 'application/json'
        contentType = 'application/json'

        response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
        response_body = json.loads(response.get('body').read())
        return response_body.get('content')[0].get('text')
    except Exception as e:
        print(e)
