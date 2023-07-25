# neo4j-generative-ai-aws
This is a sample notebook and web application which shows how Amazon Bedrock and Titan can be used with Neo4j. We will explore how to leverage generative AI to build and consume a knowledge graph in Neo4j.

The dataset we're using is from the SEC's EDGAR system.  It was downloaded using [these scripts](https://github.com/neo4j-partners/neo4j-sec-edgar-form13).

The dataflow in this demo consists of two parts:
1. Ingestion - we read the EDGAR files with Bedrock, extracting entities and relationships from them.  Bedrock then generates Neo4j Cypher that is run against a Neo4j database deployed from AWS Marketplace.
2. Consumption - A user inputs natural language into a web UI.  Bedrock converts that to Neo4j Cypher which is run against the database.  This flow allows non technical users to query the database.

To get started setting up the demo, clone this repo into a [SageMaker Studio](https://aws.amazon.com/sagemaker/studio/) environment and then follow the instructions in [notebook.ipynb](notebook.ipynb).