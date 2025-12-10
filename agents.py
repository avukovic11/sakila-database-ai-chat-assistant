from autogen import UserProxyAgent, AssistantAgent
from sql import execute_sql, FULL_DATABASE_PROFILE
import os

# LLM Configuration
llm_config = {
    "config_list": [{
        "model": "gpt-5-mini",  
        "base_url": "https://api.openai.com/v1",
        "api_key": os.getenv("OPENAI_API_KEY"),
    }],
    "timeout": 120
}

# Agents
user_proxy = UserProxyAgent(
    name="user_proxy",
    system_message="You execute SQL queries and return results only. If there are multiple queries, return results for all queries.",
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    human_input_mode="NEVER",
    code_execution_config=False,
)


sql_expert = AssistantAgent(
    name="sql_expert",
    system_message=f"""
You are an expert PostgreSQL SQL developer for the Sakila database. 
Your task is to translate user questions into efficient and correct SQL queries.

For context, here is the complete profile of the database:
{FULL_DATABASE_PROFILE}


RULES:
1. If the user requests data modification, reject it by exactly saying 'User is not allowed to modify the database' and add the keyword 'TERMINATE' to end the chat.
2. If the user question is not related to the Sakila database, respond with 'I can only answer questions about the Sakila database' and add the keyword 'TERMINATE' to end the chat.
3. Use only execute_sql to run your SQL queries (the default value for limit is 30). User proxy will only provide results from the queries, it will never talk in natural language. If there are multiple queries, execute them one by one.
4. If you get a satisfactory answer to the user's question, respond with the query result (not natural language) and keyword 'TERMINATE' to end the chat.
""",
    llm_config=llm_config
)


data_analyst = AssistantAgent(
    name="data_analyst",
    system_message="""
You are a data analyst. You receive SQL query results from user_proxy and provide a short, clear answer to the user's question.

Do not request tools or generate SQL queries.
Only interpret the results in plain English.
If the question is not about the data, respond with 'I can only answer questions about the database.'
There is a cap on how many rows can be returned from SQL queries (100), so if the row count is really big, show the 100 rows.
""",
    llm_config=llm_config
)

# Register function execute_sql
sql_expert.register_for_llm(name="execute_sql", description="Execute a SQL query on the database")(execute_sql)
user_proxy.register_for_execution(name="execute_sql", description="Execute a SQL query on the database")(execute_sql)