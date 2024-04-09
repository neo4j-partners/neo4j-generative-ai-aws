from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain.prompts.prompt import PromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain_community.chat_models import BedrockChat
from retry import retry
from timeit import default_timer as timer
import streamlit as st
import ingestion.bedrock_util as bedrock_util
from langchain_community.embeddings import BedrockEmbeddings
from neo4j_driver import run_query
from json import loads
import json

bedrock = bedrock_util.get_client()

model_name = st.secrets["SUMMARY_MODEL"]
if model_name == '':
    model_name = 'anthropic.claude-v2'


SYSTEM_PROMPT = """You are a Financial expert with SEC filings who can answer questions only based on the context below.
* Answer the question STRICTLY based on the context provided in JSON below.
* Do not assume or retrieve any information outside of the context 
* Use three sentences maximum and keep the answer concise
* List the results in rich text format if there are more than one results
* If the context is empty, just respond None
* Do NOT assume. So no extraneous information in the response

"""

PROMPT_TEMPLATE = """
<question>
{input}
</question>

Here is the context in JSON format. Note that company's are not considered asset managers in this dataset, 
and form10ks don't include asset manager information. Where asset manager info is mode explicitly available, 
you can assume the mentioned asset managers are impacted by the same things as the companies. 
<context>
{context}
</context>
"""
PROMPT = PromptTemplate(
    input_variables=["input","context"], template=PROMPT_TEMPLATE
)

EMBEDDING_MODEL = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=bedrock)
def vector_graph_qa(query):
    query_vector = EMBEDDING_MODEL.embed_query(query)
    return run_query("""
    CALL db.index.vector.queryNodes('document-embeddings', 50, $queryVector)
    YIELD node AS doc, score
    OPTIONAL MATCH (doc)<-[:HAS]-(c:Company)<-[o:OWNS]-(manager:Manager)
    RETURN c.companyName AS company, 
        collect('The asset manager ' + manager.managerName + ' owns ' + toString(o.shares) + 
        ' shares of ' + c.companyName + ' as of ' + toString(o.reportCalendarOrQuarter)) AS assetManagerInfo, 
        doc.text AS company10kInfo, 
        score
    ORDER BY score DESC LIMIT 10
    """, params =  {'queryVector': query_vector})

def df_to_context(df):
    result = df.to_json(orient="records")
    parsed = loads(result)
    # text = yaml.dump(
    #     parsed,
    #     sort_keys=False, indent=1,
    #     default_flow_style=None)
    text = json.dumps(parsed, indent=1)
    return text

@retry(tries=5, delay=5)
def get_results(question):
    start = timer()
    try:
        bedrock_llm = BedrockChat(
            model_id=model_name,
            client=bedrock,
            model_kwargs = {
                "temperature":0,
                "top_k":1, "top_p":0.1,
                "anthropic_version":"bedrock-2023-05-31",
                "max_tokens": 20000
            }
        )
        df = vector_graph_qa(question)
        ctx = df_to_context(df)
        ans = PROMPT.format(input=question, context=ctx)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=ans
            )
        ]
        result = bedrock_llm(messages).content
        r = {'context': ctx, 'result': result}
        return r
    finally:
        print('Cypher Generation Time : {}'.format(timer() - start))


