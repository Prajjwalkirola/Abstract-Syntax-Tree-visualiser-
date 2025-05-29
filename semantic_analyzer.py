class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table_stack = [set()]  # Stack for scopes
        self.errors = []

    def analyze(self):
        self.visit(self.ast)
        return self.errors

    def current_scope(self):
        return self.symbol_table_stack[-1]

    def declare(self, var):
        scope = self.current_scope()
        if var in scope:
            self.errors.append(f"Duplicate declaration: {var}")
        scope.add(var)

    def is_declared(self, var):
        return any(var in scope for scope in reversed(self.symbol_table_stack))

    def visit(self, node):
        if isinstance(node, dict):
            node_type = node.get("type")
            if node_type == "Assignment":
                var = node["name"]
                self.declare(var)
                self.visit(node["value"])
            elif node_type == "Identifier":
                if not self.is_declared(node["name"]):
                    self.errors.append(f"Undeclared variable: {node['name']}")
            elif node_type == "BinaryExpression":
                self.visit(node["left"])
                self.visit(node["right"])
            elif node_type == "Block":
                self.symbol_table_stack.append(set())
                for stmt in node.get("body", []):
                    self.visit(stmt)
                self.symbol_table_stack.pop()
            elif node_type == "Program":
                for stmt in node.get("body", []):
                    self.visit(stmt)
            # Extend here for more node types (e.g., FunctionDeclaration)
        elif isinstance(node, list):
            for item in node:
                self.visit(item)