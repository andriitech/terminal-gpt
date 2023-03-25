import openai
import sys
import keyring
import getpass
import re
import readline
import time
from colorama import Fore, Style, init
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter
from halo import Halo

spinner = Halo(spinner='dots', color='magenta')

KEYRING_SERVICE = "openai_chat_gpt"

def get_api_key():
    api_key = keyring.get_password(KEYRING_SERVICE, "api_key")

    if not api_key:
        api_key = getpass.getpass("Enter your OpenAI API key: ").strip()
        keyring.set_password(KEYRING_SERVICE, "api_key", api_key)

    return api_key

def chat_gpt(prompt, conversation_history, use_chat_api):
    spinner.start()
    if use_chat_api:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            max_tokens=150,
            top_p=1.0,
            frequency_penalty=0,
            presence_penalty=0,
        )
        spinner.stop()
        print(response)
        return response.choices[0].message.content

    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=prompt,
        temperature=0.8,
        max_tokens=150,
        top_p=1.0,
        frequency_penalty=0,
        presence_penalty=0,
    )
    spinner.stop()
    print(response)
    return response.choices[0].text.strip()

def detect_language(text):
    # Add more languages and their corresponding keywords as needed
    languages = {
        'python': 'python',
        'javascript': 'javascript',
        'java': 'java',
        'csharp': 'csharp',
        'cpp': 'cpp',
        'ruby': 'ruby',
        'php': 'php',
        'go': 'go',
        'swift': 'swift',
        'kotlin': 'kotlin',
        'rust': 'rust',
        'scala': 'scala',
        'perl': 'perl',
        'lua': 'lua',
        'typescript': 'typescript',
        'dart': 'dart',
        'r': 'r',
        'elixir': 'elixir',
        'haskell': 'haskell'
    }

    words = re.findall(r'\w+', text.lower())
    for lang, keyword in languages.items():
        if keyword in words:
            return lang

    return 'PHP'


def format_code(text, default_language='PHP'):
    try:
        code_start = text.find('```')
        code_end = text.rfind('```')

        if code_start == -1 or code_end == -1 or code_start == code_end:
            return text

        before_code = text[:code_start].strip()
        code = text[code_start + 3:code_end].strip()
        after_code = text[code_end + 3:].strip()

        language = detect_language(before_code)
        if language is None:
            language = default_language

        lexer = get_lexer_by_name(language)
        formatter = TerminalFormatter()
        formatted_code = highlight(code, lexer, formatter)

        return before_code + "\n\n" + formatted_code + "\n\n" + after_code
    except Exception as e:
        print(f"Error formatting code: {e}")
        return text



def task_mode(prompt):
    gpt_response = chat_gpt(prompt, "", False)
    print(f"gpt: {gpt_response}")

def chat_mode():
    init(autoreset=True)

    username = getpass.getuser()
    conversation_history = ""

    while True:
        user_input = input(f"{Fore.GREEN}{username}{Style.RESET_ALL}: ")
        if user_input.lower() == "exit":
            break

        conversation_history += f"User: {user_input}\n"
        gpt_response = chat_gpt(user_input, conversation_history, True)
        conversation_history += f"GPT-4: {gpt_response}\n"
        print(f"{Fore.MAGENTA}gpt{Style.RESET_ALL}: {format_code(gpt_response, 'JavaScript')}")

if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) < 2:
        print("Usage: cligpt [task|chat] ")
        sys.exit(1)

    mode = sys.argv[1].lower()
    if mode not in ["task", "chat"]:
        print("Invalid argument. Use 'task' or 'chat'.")
        sys.exit(1)

    api_key = get_api_key()
    openai.api_key = api_key

    if mode == "task":
        if len(sys.argv) < 3:
            print("Usage: cligpt [task] [promt]")
            sys.exit(1)

        task_mode(sys.argv[2])
    elif mode == "chat":
        chat_mode()

