import json
import os
import time

import openai
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def create_chat_completion(
    model, system_message, user_prompt, temperature, max_tokens
):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response
    except openai.error.APIError as e:
        print(f"OpenAI API returned an API Error: {e}")

        time.sleep(10)

        return create_chat_completion(
            model, system_message, user_prompt, temperature, max_tokens
        )
    except openai.error.APIConnectionError as e:
        print(f"Failed to connect to OpenAI API: {e}")

        time.sleep(10)

        return create_chat_completion(
            model, system_message, user_prompt, temperature, max_tokens
        )
    except openai.error.RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit: {e}")

        time.sleep(60)

        return create_chat_completion(
            model, system_message, user_prompt, temperature, max_tokens
        )
    except openai.error.AuthenticationError as e:
        print(f"Authentication error with OpenAI API: {e}")

        return None
    except openai.error.InvalidRequestError as e:
        print(f"Invalid request error with OpenAI API: {e}")

        return None
    except openai.error.ServiceUnavailableError as e:
        print(f"Service unavailable error with OpenAI API: {e}")

        time.sleep(30)

        return create_chat_completion(
            model, system_message, user_prompt, temperature, max_tokens
        )
    except requests.exceptions.ReadTimeout as e:
        print(f"Network request took too long: {e}")

        time.sleep(60)

        return create_chat_completion(
            model, system_message, user_prompt, temperature, max_tokens
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

        time.sleep(600)

        return create_chat_completion(
            model, system_message, user_prompt, temperature, max_tokens
        )


def get_context(csv_file):
    df = pd.read_csv(csv_file)
    column_header = df.columns.values.tolist()

    context = {}
    for header in column_header:
        context[header] = df[header].tolist()[:5]

    return context


def get_prompt(context):
    file = open('utils/context_4_single.txt', 'r')
    prompt = file.read()

    prompt = prompt.strip() + '\n\n\n'
    for key in context.keys():
        prompt += f'{key}: {context[key]}\n\n'

    prompt += 'Return a JSON object with key as tags and dictionary as value\n'
    prompt += 'In dictionary, have two keys: "numerical" and "category"\n'
    prompt += '"Numerical key can have values "Yes" or "No"\n'
    prompt += '''If the category for non-numerical data does not coincide with
    any of the above, return None'''
    prompt += 'No need to provide explanation. Simply return the JSON object\n'

    return prompt


def chat_api(prompt_context, system_message="", temperature=0.7):
    system_message = "You are a helpful assistant."

    prompt = prompt_context
    ANNOTATING_MODEL = "gpt-4"

    response = create_chat_completion(
        ANNOTATING_MODEL, system_message, prompt, temperature, 900
    )
    response_content = json.loads(response['choices'][0]['message']['content'])

    return response_content


def parse_response_json(response):
    data = []

    for key in response.keys():
        if response[key]["numerical"].lower() == "yes":
            data.append([key, True, response[key]["category"]])
        else:
            if response[key]["category"].lower() != "none":
                data.append([key, False, response[key]["category"]])

    return data
