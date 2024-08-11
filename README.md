# BICO: Business Intelligence Companion

<div align="center">

[English](./README.md) | [简体中文](./README_zh.md)

</div>

## Exploring the Frontier of Text2Artifact in Business Intelligence

BICO (Business Intelligence Companion) is a PoC project that explores the integration of Large Language Models (LLMs) with existing platform services, resolutioning how we interact with complex Business Intelligence (BI) tools. By leveraging the power of AWS services like Bedrock, OpenSearch, and QuickSight, BICO transforms abstract human queries into structured API calls, making sophisticated BI operations accessible to a wider audience.


## Text2Artifact Capability
BICO translate natural language into complex QuickSight dashboards:



## Text2SQL Capability
BICO in action as it generates optimized SQL queries from natural language:

https://github.com/user-attachments/assets/65ec01f3-aabc-4c91-85ed-95970094c68f



## ✨ Key Innovations

### 1. Text2Artifact: Beyond Simple Conversions

BICO can achieve the capability of "Text2Artifact", expanding on ideas like Text2SQL and Text2Platform. This approach allows LLMs to understand and manipulate complex, structured data and platform objects through natural language interactions.

- 🧠 Intelligent parsing of user intents into platform-specific operations
- 🔧 Dynamic generation of API call sequences to fulfill complex requests
- 🎨 Creation and modification of platform artifacts (e.g., SQL queries, QuickSight dashboards) through conversation

### 2. LLM-Friendly API Design

BICO explores the balance between API granularity and LLM comprehension:

- 🧩 Modular function design optimized for LLM understanding and chaining
- 🔗 Handle-based memory management for complex object manipulation
- 📚 Rich, context-aware function documentation and pseudo-code prompts to guide LLM decision-making

## ✨ Features

- 📊 Natural language to SQL query conversion (Text2SQL)
- 🎨 AI-driven QuickSight dashboard creation (Text2Artifact)
- 🧠 Navigating complex relationships between tables with varying granularities
- ⚡ Optimization-aware query construction and dashboard design
- 🖼️ Handle-based object management for artifact elements
- 📝 Pseudo-code prompts for guided AI operations

## 🚀 Project Vision: 

- 🤝 Contribute to the development of more intuitive Text2Artifact systems
- 🔍 Explore optimal API designs for LLM integration
- 🌟 Help shape the future of AI-assisted technology interaction

## 🛠️ Getting Started

1. Set permissions for AWS IAM. 

   This project uses the isengard account, including bedrock models, knowledge base, and quicksight, all managed implicitly through IAM. The RDS database parameters need to be manually configured in the database.py file. The OpenSearch index parameters need to be manually configured in search_tool.py.

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```


3. Run the main script:
   ```
   chainlit run app.py
   ```

## Resources & Thanks
# This project references and uses the following projects:

- [QuickSight Assets-as-Code](https://github.com/aws-samples/amazon-quicksight-assets-as-code-sample?tab=readme-ov-file#quicksight-assets-as-code)
- [langchain-aws](https://github.com/langchain-ai/langchain-aws) 
- [data-analysis-llm-agent](https://github.com/crazycloud/data-analysis-llm-agent/tree/main)
- [Bedrock-AIChatbot-Sample](https://github.com/hayao-k/Bedrock-AIChatbot-Sample)

# This project was inspired by the following blog.
- [Prompt 高级技巧：借助伪代码精准的控制 LLM 的输出结果和定义其执行逻辑](https://baoyu.io/blog/prompt-engineering/advanced-prompting-using-pseudocode-to-control-llm-output)
- [Building language agents as graphs](https://langchain-ai.github.io/langgraph/)


## 📜 License

BICO is released under the [MIT License](LICENSE).
