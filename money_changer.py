from typing import Tuple, Dict
import dotenv
import os
from dotenv import load_dotenv
from openai import OpenAI

import requests
import json
import streamlit as st

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o-mini"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

load_dotenv()
EXCHANGERATE_API_KEY = os.getenv('EXCHANGERATE_API_KEY')


def get_exchange_rate(base: str, target: str, amount: str) -> Tuple:
    """Return a tuple of (base, target, amount, conversion_result (2 decimal places))"""
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/pair/{base}/{target}/{amount}"
    response = json.loads(requests.get(url).text)
    return(base, target, amount, f'{response["conversion_result"]:.2f}')

def call_llm(textbox_input) -> Dict:
    """Make a call to the LLM with the textbox_input as the prompt.
       The output from the LLM should be a JSON (dict) with the base, amount and target"""

    tools = [{
    "type": "function",
    "function": {
            "name": "exchange_rate_function",
            "description": "Convert a given amount of money from one currency to another. Each currency will be represented as a 3-letter code",
            "parameters": {
                "type": "object",
                "properties": {
                    "base": {
                        "type": "string",
                        "description": "Base currency"
                    },
                    "target": {
                        "type": "string",
                        "description": "Target currency"
                    },
                    "amount": {
                        "type": "string",
                        "description": "Amount to convert"
                    }
                },
                "required": [
                    "base",
                    "target",
                    "amount"
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    }]
              
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": textbox_input,
                }
            ],
            temperature=1.0,
            top_p=1.0,
            max_tokens=1000,
            model=model_name,
            tools=tools
        )

    except Exception as e:
        print(f"Exception {e} for {text}")
    else:
        return response#.choices[0].message.tool_calls[0].function.arguments

def run_pipeline(user_input):
    """Based on textbox_input, determine if you need to use the tools (function calling) for the LLM.
    Call get_exchange_rate(...) if necessary"""

    response = call_llm(user_input)

    if response.choices[0].finish_reason == 'tool_calls':
        response_arguments = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
        base = response_arguments["base"]
        target = response_arguments["target"]
        amount = response_arguments["amount"]
        _, _, _, conversion_result = get_exchange_rate(base, target, amount)

        st.write(f'{base} {amount} is {target} {conversion_result}')

    elif response.choices[0].finish_reason == 'stop':
        st.write(response.choices[0].message.content)
    else:
        st.write("NotImplemented")


# Set the title of the app
st.title("Multilingual Money Changer")

# Create a text input box
user_input = st.text_input("Enter the amount and the currency:")

# Create a submit button
if st.button("Submit"):
    # Display the contents of the text box below
    run_pipeline(user_input)