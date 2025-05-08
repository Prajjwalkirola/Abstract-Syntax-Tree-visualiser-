import json
from graphviz import Digraph

# Function to load AST from a JSON file
def load_ast(filename="ast.json"):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from AST file.")
        exit(1)

# Recursive function to add nodes and edges to the Graphviz Digraph
def add_nodes_edges(ast, dot, parent_id=None, node_id=[0]):
    current_id = str(node_id[0])
    label = ast.get("type", "Unknown")

    # Add more context to nodes
    if label == "Number":
        label += f"\n{ast['value']}"
    elif label == "Identifier":
        label += f"\n{ast['name']}"
    elif label == "BinaryExpression":
        label += f"\n{ast['operator']}"
    elif label == "Assignment":
        label += f"\n{ast['name']}"
    elif label == "PrintStatement":
        label += "\n(print)"

    dot.node(current_id, label)
    if parent_id is not None:
        dot.edge(parent_id, current_id)

    node_id[0] += 1

    for key, value in ast.items():
        if isinstance(value, dict):
            add_nodes_edges(value, dot, current_id, node_id)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    add_nodes_edges(item, dot, current_id, node_id)

# Function to visualize AST and save it as a PNG
def visualize_ast(ast):
    dot = Digraph(comment="Abstract Syntax Tree", format='png')
    add_nodes_edges(ast, dot)
    output_path = dot.render("ast_output", cleanup=True)
    print(f"AST visualized and saved as: {output_path}")

# Main entry point
if __name__ == "__main__":
    ast = load_ast("ast.json")
    visualize_ast(ast)
