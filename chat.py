from agents import user_proxy, sql_expert, data_analyst

# Chat Function
conversation_history = []
def chat_with_sakila(user_question: str) -> str:
    history_text = ""
    for h in conversation_history:
        history_text += f"User: {h['user']}\n"
        history_text += f"Analyst: {h['analyst']}\n\n"

    chat_result = user_proxy.initiate_chat(
        sql_expert,
        message=f"""You are continuing an ongoing conversation.
Conversation so far:
{history_text if history_text != '' else '<no prior conversation>'}

New user question:
{user_question}
""",
        max_turns=5,
        silent=False,
    )
    sql_results = chat_result.summary

    analyst_result = user_proxy.initiate_chat(
        data_analyst,
        message=f"""You are continuing an ongoing conversation.
Conversation so far:
{history_text if history_text != '' else '<no prior conversation>'}

Based on the following SQL query results, answer:
User asked: '{user_question}'
Query Results: {sql_results}
""",
        max_turns=1,
        silent=False
    )
    final_answer = analyst_result.summary

    conversation_history.append({
        "user": user_question,
        "analyst": final_answer
    })

    MAX_HISTORY = 10
    if len(conversation_history) > MAX_HISTORY:
        conversation_history.pop(0)

    print(f"Answer: {final_answer}")
    return final_answer

# Chat Interface
def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║         Sakila Database AI Chat Assistant                  ║
╚════════════════════════════════════════════════════════════╝
Ask questions about the film Sakila PostgreSQL database.          
Type 'exit' or 'quit' or 'q' to end the chat.
""")
    
    while True:
        try:
            user_input = input("\nYour question (type 'q' to exit): ").strip()
            if not user_input: continue
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            chat_with_sakila(user_input)
        except KeyboardInterrupt:
            print("Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()