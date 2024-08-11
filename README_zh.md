# BICO: Business Intelligence Companion

<div align="center">

[English](./README.md) | [简体中文](./README_zh.md)

</div>

## Exploring the Frontier of Text2Artifact in Business Intelligence

BICO（商业智能助手）是一个概念验证项目，旨在探索大型语言模型（LLMs）与现有平台服务的集成，解决我们与复杂商业智能（BI）工具的交互方式。通过利用AWS服务如Bedrock、OpenSearch和QuickSight的强大功能，BICO将抽象的人类查询转化为结构化的API调用，使复杂的BI操作变得更加易于使用。


## Text2Artifact Capability
BICO translates natural language into QuickSight dashboards:

https://github.com/user-attachments/assets/28269ad0-0c5f-4c7b-9f51-408b6de160ff

*<span style="color: #B0B0B0;">评论: 大语言模型介入平台服务成为现实</span>*

## Text2SQL Capability
BICO in action as it generates optimized SQL queries from natural language:

https://github.com/user-attachments/assets/d929013d-2821-4285-88bc-3616b10b6421

*<span style="color: #B0B0B0;">评论：榨干大语言模型在响应查询时的推理能力</span>*


## ✨ Key Innovations

### 1. Text2Artifact: Beyond Simple Conversions

BICO实现了"Text2Artifact"的能力, 拓展了Text2SQL和Text2Platform等理念. 这种方法允许大语言模型通过自然语言交互来理解和操作复杂的结构化数据和平台对象。

- 🧠 智能解析用户意图并转化为特定平台操作
- 🔧 动态生成API调用序列以满足复杂请求
- 🎨 通过对话创建和修改平台制品（如SQL查询、QuickSight仪表板）

### 2. LLM-Friendly API Design

BICO探索了API粒度与大语言模型理解能力之间的平衡：

- 🧩 为大语言模型的理解和链接优化的模块化函数设计
- 🔗 基于句柄的复杂对象内存管理
- 📚 丰富的、上下文感知的函数文档和伪代码提示，指导大语言模型决策

## ✨ Features

- 📊 自然语言到SQL查询的转换（TEXT2SQL）
- 🎨 AI驱动的QuickSight仪表板创建（TEXT2Artifact）
- 🧠 导航与对齐具有不同粒度的表之间的复杂关系
- ⚡ 优化感知的查询构建和仪表板设计
- 🖼️ 基于句柄的制品元素对象管理
- 📝 用于引导AI操作的伪代码提示

## 🚀 Project Vision: 

- 🤝 为开发更直观的Text2Artifact系统做出贡献
- 🔍 探索适合大语言模型集成的最佳API设计
- 🌟 帮助塑造AI辅助技术交互的未来

## 🛠️ Getting Started

1. Set permissions for AWS IAM. 

    本项目使用isengard账户，包括bedrock模型、知识库和quicksight，这些都通过IAM隐式管理。RDS数据库参数需要在database.py文件中手动配置。OpenSearch索引参数需要在search_tool.py中手动配置。


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

## Appendix

该项目获得AWS GCR Hackathon 二等奖
![4521723383801_ pic](https://github.com/user-attachments/assets/85747fe3-ecd8-4d9f-8d28-4bd21ea9e60c)


