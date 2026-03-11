from prompts import system_prompt
from call_function import available_functions, call_function
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import argparse
import sys
from config import MAX_ITERATIONS

def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    if api_key is None:
        raise RuntimeError("Api key not found, please add it to the .env file, \
                           under the name GEMINI_API_KEY=\"YOUR KEY\"")
    
    parser = argparse.ArgumentParser(description = "Chatbot")
    parser.add_argument("user_prompt", type = str, help = "User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    client = genai.Client(api_key = api_key)

    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    for _ in range(MAX_ITERATIONS):
        # passing messages as a reference :)
        if generate_content(client, messages, args) == 0:
            return
        
    print("Maximum allowed number of iterations on model reached. Terminating.")
    sys.exit(-1)

def generate_content(client: genai.Client, messages: list, args):
    response = client.models.generate_content(
        model = 'gemini-2.5-flash', 
        contents = messages,
        config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt),
    )
    if response.candidates:
        for candidate in response.candidates:
            messages.append(candidate.content)
    if response.usage_metadata is None:
        raise RuntimeError("Google API is currently down. Try again later.")
    
    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    if not response.function_calls:
        print("Response:")
        print(response.text)
        return 0
    function_results = []
    for function_call in response.function_calls:
        print(f"Calling function: {function_call.name}({function_call.args})")
        function_call_result = call_function(function_call)
        if (
            not function_call_result.parts
            or not function_call_result.parts[0].function_response
            or not function_call_result.parts[0].function_response.response
        ):
            raise RuntimeError(f"Empty function response for {function_call.name}")
    
        function_results.append(function_call_result.parts[0])

        if args.verbose:
            print(f"-> {function_call_result.parts[0].function_response.response}")
    messages.append(types.Content(role="user", parts=function_results))

if __name__ == "__main__":
    main()

# Project doesn't contain any comments, I acknowledge that, will improve next time!