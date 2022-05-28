#!/bin/python3

import basic

while True:
    # Get user input
    text = input("basic >  ")
    # removing whitespace
    text = text.strip()
    # exit keyword
    if text == "exit":
        break
    # Tokenizing
    tokens, error = basic.runner(text)
    if error:
        print(error)
    else:
        print(tokens)
