from swarm import Swarm, Agent
from swarm.types import Result
from openai import OpenAI
from duckduckgo_search import DDGS
import os,time
from dotenv import load_dotenv,find_dotenv
from swarm.repl.repl import pretty_print_messages,process_and_print_streaming_response
from data_fetcher import guba_topics,uplimits
import time


load_dotenv(find_dotenv())

def getMarketData(context_variables: dict) -> Result:
    uplimits_data = uplimits.fetch_continuous_up_limit_data()
    guba_topics_data = guba_topics.getTopics()
    context_text = '\n## 连板统计：\n\n'+uplimits_data+'\n\n## 新闻:\n\n'+guba_topics_data
    return Result(
        value=context_text,
        context_variables=context_variables,
        agent=analyzer_agent,
    )

# 分析器 Agent
analyzer_agent = Agent(
    name="Analyzer",
    instructions="""你是一个A股交易达人, 能使用工具获取Market Data, 然后从短线交易的角度分析连板个股的题材是悲观避险导致还是整体市场推动的结果，得出复盘结论应该关注哪些方向和个股。
    \n注意股票必须带链接，比如[中芯国际](https://xueqiu.com/S/SH688981),注意如果股票代码6开头的链接是/S/SH6...,其他是/S/SZ...
    """,
    functions=[getMarketData]
)


# 运行示例
def run(
    starting_agent, context_variables=None, stream=False, debug=False, user_input='今日A股复盘'
) -> None:
    client = Swarm(OpenAI(api_key=os.getenv("OPENAI_API_KEY"),base_url=os.getenv("LLM_BASE"),))
    print("Starting Swarm CLI 🐝")

    messages = []
    agent = starting_agent

    # user_input = input("\033[90mUser\033[0m: ")
    messages.append({"role": "user", "content": user_input})

    response = client.run(
        model_override=os.getenv("MODEL"),
        agent=agent,
        messages=messages,
        context_variables=context_variables or {},
        stream=stream,
        debug=debug,
    )

    if stream:
        response = process_and_print_streaming_response(response)
    else:
        pretty_print_messages(response.messages)

Agents = Swarm(OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("LLM_BASE")))

if __name__ == "__main__":
    print(run(starting_agent=analyzer_agent,stream=False,debug=True,context_variables={}))
