from typing import Tuple, Dict
import dotenv
import os
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

import requests
import json
import streamlit as st

endpoint = "https://models.inference.ai.azure.com"
model_name = "Phi-4"
token = os.environ["GITHUB_TOKEN"]

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

load_dotenv()
EXCHANGERATE_API_KEY = os.getenv('EXCHANGERATE_API_KEY')


def get_exchange_rate(base: str, target: str, amount: str) -> Tuple:
    """Return a tuple of (base, target, amount, conversion_result (2 decimal places))"""
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/pair/{base}/{target}/{amount}"
    response = json.loads(requests.get(url).text)
    return(base, target, amount, f'{response["conversion_result"]:.2f}')

# print(get_exchange_rate("USD", "GBP", "350"))

def call_llm(textbox_input) -> Dict:
    """Make a call to the LLM with the textbox_input as the prompt.
       The output from the LLM should be a JSON (dict) with the base, amount and target"""
              
    try:
        response = client.complete(
            messages=[
                UserMessage(textbox_input),
            ],
            temperature=1.0,
            top_p=1.0,
            max_tokens=1000,
            model=model_name
        )

    except Exception as e:
        print(f"Exception {e} for {text}")
    else:
        return response.choices[0].message.content

def run_pipeline():
    """Based on textbox_input, determine if you need to use the tools (function calling) for the LLM.
    Call get_exchange_rate(...) if necessary"""

    if True: #tool_calls
        get_exchange_rate()
        st.write(f'{base} {amount} is {target} {exchange_response["conversion_result"]:.2f}')

    elif True: #tools not used
        # Update this
        st.write(f"(Function calling not used) and response from the model")
    else:
        st.write("NotImplemented")


# Set the title of the app
st.title("Multilingual Money Changer")

# Create a text input box
user_input = st.text_input("Enter the amount and the currency:")

# Create a submit button
if st.button("Submit"):
    # Display the contents of the text box below
    st.write(call_llm(user_input))