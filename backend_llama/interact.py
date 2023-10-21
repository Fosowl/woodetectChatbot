import time
from subprocess import Popen, PIPE, STDOUT

from llamacpp_channel import *

control = pyllamacpp()
for word in control.next_word():
    if control.exited():
        break
    if control.is_loading() and control.waiting():
        control.send("###Human: Hello\n###Assistant: ")
    if control.is_loading():
        print("Waiting for llm...")
    if control.waiting() and word == "":
        question = input("\nEnter query: ")
        formatted_question = f"###Human: {question}\n###Assistant:\n"
        control.send(formatted_question)
    print(word, end=' ')
    if '\n' in word:
        print()
        