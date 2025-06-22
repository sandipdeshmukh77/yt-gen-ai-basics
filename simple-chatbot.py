from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os
# client = OpenAI()

gemini_api_key = os.getenv("GEMINI_API_KEY")

client = OpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

history= []

while True:
    user_input = input(" 👤You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the chatbot. Goodbye!")
        break
    user_input_with_role = {
            "role": "user",
            "content": user_input
        }
    history.append(user_input_with_role)
    

    # for openAI 
    # response = client.responses.create(
    # model="gpt-4.1",
    # input=history
    # )

    response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=history
)



    history.append({
            "role": "assistant",
            "content": response.choices[0].message.content
        })

    print("🧑‍💻AI :", response.choices[0].message.content)
