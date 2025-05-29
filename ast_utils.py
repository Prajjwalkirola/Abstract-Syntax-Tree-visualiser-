import subprocess
import json
import os

def run_full_pipeline(source_file):
    # Run lexer
    subprocess.run(["python", "lexer.py"], check=True)
    # Run parser
    subprocess.run(["python", "parser.py"], check=True)
    # Run visualizer
    subprocess.run(["python", "ast_visualizer.py"], check=True)


def get_entities_from_tokens(tokens):
    operators = set()
    functions = set()
    for token in tokens:
        if token[0] == "OPERATOR":
            operators.add(token[1])
        if token[0] == "IDENTIFIER":
            # Heuristic: function names are followed by '('
            idx = tokens.index(token)
            if idx + 1 < len(tokens) and tokens[idx + 1][0] == "SEPARATOR" and tokens[idx + 1][1] == "(":
                functions.add(token[1])
    return {
        "operators": sorted(list(operators)),
        "functions": sorted(list(functions))
    } 