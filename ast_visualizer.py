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

def get_node_color(node_type):
    colors = {
        "Program": "#4A90E2",  # Blue
        "Assignment": "#50E3C2",  # Teal
        "BinaryExpression": "#F5A623",  # Orange
        "UnaryExpression": "#F5A623",  # Orange
        "Number": "#7ED321",  # Green
        "String": "#7ED321",  # Green
        "Identifier": "#BD10E0",  # Purple
        "IfStatement": "#D0021B",  # Red
        "WhileStatement": "#D0021B",  # Red
        "ForStatement": "#D0021B",  # Red
        "FunctionDefinition": "#9013FE",  # Deep Purple
        "PrintStatement": "#4A90E2",  # Blue
        "ReturnStatement": "#4A90E2",  # Blue
        "BreakStatement": "#4A90E2",  # Blue
        "ContinueStatement": "#4A90E2",  # Blue
        "Boolean": "#7ED321",  # Green
        "None": "#7ED321",  # Green
        "AugmentedAssignment": "#50E3C2",  # Teal
    }
    return colors.get(node_type, "#9B9B9B")  # Default gray

def get_node_label(node):
    node_type = node.get("type", "Unknown")
    label = node_type

    if node_type == "Number":
        label += f"\n{node['value']}"
    elif node_type == "String":
        label += f"\n'{node['value']}'"
    elif node_type == "Identifier":
        label += f"\n{node['name']}"
    elif node_type == "BinaryExpression":
        label += f"\n{node['operator']}"
    elif node_type == "UnaryExpression":
        label += f"\n{node['operator']}"
    elif node_type == "Assignment":
        label += f"\n{node['name']} ="
    elif node_type == "AugmentedAssignment":
        label += f"\n{node['left']['name']} {node['operator']}"
    elif node_type == "PrintStatement":
        label += "\nprint"
    elif node_type == "IfStatement":
        label += "\nif"
    elif node_type == "WhileStatement":
        label += "\nwhile"
    elif node_type == "ForStatement":
        label += "\nfor"
    elif node_type == "FunctionDefinition":
        label += f"\ndef {node['name']}"
    elif node_type == "ReturnStatement":
        label += "\nreturn"
    elif node_type == "Boolean":
        label += f"\n{node['value']}"
    elif node_type == "None":
        label += "\nNone"

    return label

# Recursive function to add nodes and edges to the Graphviz Digraph
def add_nodes_edges(ast, dot, parent_id=None, node_id=[0]):
    current_id = str(node_id[0])
    node_type = ast.get("type", "Unknown")
    label = get_node_label(ast)
    color = get_node_color(node_type)

    # Create node with styling
    dot.node(current_id, label, 
             style="filled",
             fillcolor=color,
             fontcolor="white",
             shape="box",
             margin="0.2",
             fontname="Arial")

    if parent_id is not None:
        dot.edge(parent_id, current_id, color="#666666")

    node_id[0] += 1

    # Handle different node types
    if node_type == "Program":
        for stmt in ast.get("body", []):
            add_nodes_edges(stmt, dot, current_id, node_id)
    elif node_type == "BinaryExpression":
        add_nodes_edges(ast["left"], dot, current_id, node_id)
        add_nodes_edges(ast["right"], dot, current_id, node_id)
    elif node_type == "UnaryExpression":
        add_nodes_edges(ast["right"], dot, current_id, node_id)
    elif node_type == "Assignment":
        add_nodes_edges(ast["value"], dot, current_id, node_id)
    elif node_type == "AugmentedAssignment":
        add_nodes_edges(ast["right"], dot, current_id, node_id)
    elif node_type == "PrintStatement":
        for arg in ast.get("arguments", []):
            add_nodes_edges(arg, dot, current_id, node_id)
    elif node_type == "IfStatement":
        add_nodes_edges(ast["condition"], dot, current_id, node_id)
        for stmt in ast.get("body", []):
            add_nodes_edges(stmt, dot, current_id, node_id)
        for elif_block in ast.get("elif_blocks", []):
            add_nodes_edges(elif_block["condition"], dot, current_id, node_id)
            for stmt in elif_block.get("body", []):
                add_nodes_edges(stmt, dot, current_id, node_id)
        if ast.get("else_block"):
            for stmt in ast["else_block"]:
                add_nodes_edges(stmt, dot, current_id, node_id)
    elif node_type == "WhileStatement":
        add_nodes_edges(ast["condition"], dot, current_id, node_id)
        for stmt in ast.get("body", []):
            add_nodes_edges(stmt, dot, current_id, node_id)
    elif node_type == "ForStatement":
        # Fix: Wrap variable in Identifier node if it's a string
        variable = ast["variable"]
        if isinstance(variable, str):
            variable = {"type": "Identifier", "name": variable}
        add_nodes_edges(variable, dot, current_id, node_id)
        add_nodes_edges(ast["iterable"], dot, current_id, node_id)
        for stmt in ast.get("body", []):
            add_nodes_edges(stmt, dot, current_id, node_id)
    elif node_type == "FunctionDefinition":
        for stmt in ast.get("body", []):
            add_nodes_edges(stmt, dot, current_id, node_id)
    elif node_type == "ReturnStatement" and ast.get("value"):
        add_nodes_edges(ast["value"], dot, current_id, node_id)

# Function to visualize AST and save it as a PNG
def visualize_ast(ast):
    dot = Digraph(comment="Abstract Syntax Tree", format='png')
    dot.attr(rankdir='TB', size='8,5', dpi='300')
    dot.attr('node', shape='box', style='rounded,filled', fontname='Arial')
    dot.attr('edge', fontname='Arial')
    
    add_nodes_edges(ast, dot)
    
    output_path = dot.render("ast_output", cleanup=True)
    print(f"AST visualized and saved as: {output_path}")

# Main entry point
if __name__ == "__main__":
    ast = load_ast("ast.json")
    visualize_ast(ast)
