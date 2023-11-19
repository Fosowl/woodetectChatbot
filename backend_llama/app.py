"""
Backend API for chatbot.
author: Martin Legrand
"""

#!/usr/bin/python3
import time
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import threading
import re
import warnings
from typing import List

warnings.filterwarnings("ignore", category=UserWarning)

from llamacpp_channel import *

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
control = pyllamacpp()
llama_generator = control.next_word()

@app.route('/')
@cross_origin()
def status():
    return "chatbot API online." 

@app.route('/is_loading', methods=['GET', 'POST'])
def is_loading():
    """
    Check if LLM is still being loaded by llama.cpp
    """
    tmp = str(control.is_loading())
    return jsonify({"reply": tmp})

@app.route('/get_sentence_history', methods=['GET'])
def get_sentence_history():
    """
    Get history of sentences generated by LLM
    """
    return jsonify({"reply": str(control.get_sentences_history())})


@app.route('/check_waiting', methods=['GET'])
def check_waiting():
    """
    check if LLM is waiting for input
    """
    if control.waiting():
        return jsonify({"reply": "True"})
    return jsonify({"reply": "False"})

@app.route('/check_exited', methods=['GET'])
def check_exited():
    """
    route to check if LLM process has exited (shouln't happen unless there's a fatal error)
    """
    return jsonify({"reply": str(control.exited())})

@app.route('/debug', methods=['GET'])
def debug():
    """
    route for debug status
    """
    return jsonify({"waiting": control.waiting(),
                    "exited": control.exited(),
                    "loading": control.is_loading()})

@app.route('/send_message', methods=['GET', 'POST'])
def send_message():
    """
    Sends a message to the LLM and returns a JSON response.
    check_waiting route should be called first to check if LLM is busy.
    """
    if not control.waiting():
        return jsonify({"reply": "LLM is busy."})
    message = request.json['message']
    formatted_question = f"###Human: {message} ###Assistant:\n"
    control.send(formatted_question)
    return jsonify({"reply": "Message sent"})

@app.route('/get_last_sentence', methods=['GET'])
def get_last_sentence():
    """
    Get last sentence from LLM while it's being generated, used for real-time display on frontend
    """
    return jsonify({"reply": control.get_last_sentence()})

# TODO FINISH THIS
@app.route('/send_message_and_wait_response', methods=['GET', 'POST'])
def send_message_and_wait():
    """
    This is the route to interact with LLM in a standard way.
    Avantage: No need for complex logic on the frontend to allow real-time display of message.
    Inconvenient: The frontend may have to wait for some time before getting a response.
    """
    if not control.waiting():
        return jsonify({"reply": "LLM is busy. This shouldn't happen with this API route, check frontend."})
    message = request.json['message']
    formatted_question = f"###Human: {message} ###Assistant:\n"
    control.send(formatted_question)
    # FIX THIS
    while True:
        if not control.waiting():
            time.sleep(0.1)
        else:
            break
    return jsonify({"reply": control.get_last_sentence()})

def llama_cpp_thread():
    global llama_generator
    while True:
        next(llama_generator)

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(port=5000, debug=False, use_reloader=False)).start()
    llama_cpp_thread()
