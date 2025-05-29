import json

# Read tokens from JSON file
def read_tokens_from_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
        self.line_num = 1
        self.column = 0
        print("Tokens loaded:", self.tokens)  # Debug print

    def error(self, message):
        raise Exception(f"Parse error at line {self.line_num}, column {self.column}: {message}")

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
            if self.current_token[0] == "NEWLINE":
                self.line_num += 1
                self.column = 0
            else:
                self.column += len(str(self.current_token[1]))
        else:
            self.current_token = None

    def consume(self, token_type, value=None):
        if self.current_token is None:
            self.error(f"Unexpected end of input. Expected token type {token_type}.")
        elif self.current_token[0] == token_type:
            if value is not None and self.current_token[1] != value:
                self.error(f"Expected token value '{value}', but got '{self.current_token[1]}'")
            token = self.current_token
            self.advance()
            return token
        else:
            self.error(f"Expected token type {token_type}, but got {self.current_token}")

    def parse(self):
        return self.parse_program()

    def parse_program(self):
        statements = []
        while self.current_token:
            # Skip comments and other non-statement tokens
            if self.current_token[0] in ("COMMENT", "NEWLINE", "INDENT", "DEDENT"):
                self.advance()
                continue
            statements.append(self.parse_statement())
        return {"type": "Program", "body": statements}

    def parse_statement(self):
        if self.current_token[0] == "KEYWORD":
            if self.current_token[1] == "print":
                return self.parse_print()
            elif self.current_token[1] == "if":
                return self.parse_if()
            elif self.current_token[1] == "while":
                return self.parse_while()
            elif self.current_token[1] == "for":
                return self.parse_for()
            elif self.current_token[1] == "def":
                return self.parse_function_def()
            elif self.current_token[1] == "return":
                return self.parse_return()
            elif self.current_token[1] == "break":
                return self.parse_break()
            elif self.current_token[1] == "continue":
                return self.parse_continue()
        elif self.current_token[0] == "IDENTIFIER":
            return self.parse_assignment()
        else:
            self.error(f"Invalid statement: {self.current_token}")

    def parse_assignment(self):
        var_name = self.current_token[1]
        self.consume("IDENTIFIER")
        
        # Handle augmented assignment operators
        if self.current_token[0] == "OPERATOR" and self.current_token[1] in ("+=", "-=", "*=", "/=", "%=", "**=", "//="):
            op = self.current_token[1]
            self.consume("OPERATOR")
            right = self.parse_expression()
            return {
                "type": "AugmentedAssignment",
                "operator": op,
                "left": {"type": "Identifier", "name": var_name},
                "right": right
            }
        
        # Regular assignment
        self.consume("OPERATOR", "=")
        expression = self.parse_expression()
        return {"type": "Assignment", "name": var_name, "value": expression}

    def parse_print(self):
        self.consume("KEYWORD", "print")
        self.consume("SEPARATOR", "(")
        args = []
        if self.current_token[0] != "SEPARATOR" or self.current_token[1] != ")":
            args.append(self.parse_expression())
            while self.current_token[0] == "SEPARATOR" and self.current_token[1] == ",":
                self.consume("SEPARATOR", ",")
                args.append(self.parse_expression())
        self.consume("SEPARATOR", ")")
        return {"type": "PrintStatement", "arguments": args}

    def parse_if(self):
        self.consume("KEYWORD", "if")
        self.consume("SEPARATOR", "(")
        condition = self.parse_expression()
        self.consume("SEPARATOR", ")")
        self.consume("SEPARATOR", ":")
        
        body = self.parse_block()
        elif_blocks = []
        else_block = None

        while self.current_token and self.current_token[0] == "KEYWORD" and self.current_token[1] == "elif":
            self.consume("KEYWORD", "elif")
            self.consume("SEPARATOR", "(")
            elif_condition = self.parse_expression()
            self.consume("SEPARATOR", ")")
            self.consume("SEPARATOR", ":")
            elif_body = self.parse_block()
            elif_blocks.append({
                "condition": elif_condition,
                "body": elif_body
            })

        if self.current_token and self.current_token[0] == "KEYWORD" and self.current_token[1] == "else":
            self.consume("KEYWORD", "else")
            self.consume("SEPARATOR", ":")
            else_block = self.parse_block()

        return {
            "type": "IfStatement",
            "condition": condition,
            "body": body,
            "elif_blocks": elif_blocks,
            "else_block": else_block
        }

    def parse_while(self):
        self.consume("KEYWORD", "while")
        self.consume("SEPARATOR", "(")
        condition = self.parse_expression()
        self.consume("SEPARATOR", ")")
        self.consume("SEPARATOR", ":")
        body = self.parse_block()
        return {"type": "WhileStatement", "condition": condition, "body": body}

    def parse_for(self):
        self.consume("KEYWORD", "for")
        var = self.consume("IDENTIFIER")[1]
        self.consume("KEYWORD", "in")
        iterable = self.parse_expression()
        self.consume("SEPARATOR", ":")
        body = self.parse_block()
        return {"type": "ForStatement", "variable": var, "iterable": iterable, "body": body}

    def parse_function_def(self):
        self.consume("KEYWORD", "def")
        name = self.consume("IDENTIFIER")[1]
        self.consume("SEPARATOR", "(")
        params = []
        if self.current_token[0] != "SEPARATOR" or self.current_token[1] != ")":
            params.append(self.consume("IDENTIFIER")[1])
            while self.current_token[0] == "SEPARATOR" and self.current_token[1] == ",":
                self.consume("SEPARATOR", ",")
                params.append(self.consume("IDENTIFIER")[1])
        self.consume("SEPARATOR", ")")
        self.consume("SEPARATOR", ":")
        body = self.parse_block()
        return {"type": "FunctionDefinition", "name": name, "parameters": params, "body": body}

    def parse_return(self):
        self.consume("KEYWORD", "return")
        value = None
        if self.current_token[0] != "NEWLINE":
            value = self.parse_expression()
        return {"type": "ReturnStatement", "value": value}

    def parse_break(self):
        self.consume("KEYWORD", "break")
        return {"type": "BreakStatement"}

    def parse_continue(self):
        self.consume("KEYWORD", "continue")
        return {"type": "ContinueStatement"}

    def parse_block(self):
        statements = []
        # Consume INDENT at the start of a block, if present
        if self.current_token and self.current_token[0] == "INDENT":
            self.consume("INDENT")
        while self.current_token and self.current_token[0] != "DEDENT":
            if self.current_token[0] == "NEWLINE":
                self.advance()
                continue
            statements.append(self.parse_statement())
        if self.current_token and self.current_token[0] == "DEDENT":
            self.consume("DEDENT")
        return statements

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        node = self.parse_and()
        while self.current_token and self.current_token[0] == "KEYWORD" and self.current_token[1] == "or":
            self.consume("KEYWORD", "or")
            right = self.parse_and()
            node = {"type": "BinaryExpression", "operator": "or", "left": node, "right": right}
        return node

    def parse_and(self):
        node = self.parse_comparison()
        while self.current_token and self.current_token[0] == "KEYWORD" and self.current_token[1] == "and":
            self.consume("KEYWORD", "and")
            right = self.parse_comparison()
            node = {"type": "BinaryExpression", "operator": "and", "left": node, "right": right}
        return node

    def parse_comparison(self):
        node = self.parse_term()
        while self.current_token and self.current_token[0] == "OPERATOR" and self.current_token[1] in ("==", "!=", "<", ">", "<=", ">=", "is", "is not", "in", "not in"):
            op = self.current_token[1]
            self.consume("OPERATOR")
            right = self.parse_term()
            node = {"type": "BinaryExpression", "operator": op, "left": node, "right": right}
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current_token and self.current_token[0] == "OPERATOR" and self.current_token[1] in ("+", "-"):
            op = self.current_token[1]
            self.consume("OPERATOR")
            right = self.parse_factor()
            node = {"type": "BinaryExpression", "operator": op, "left": node, "right": right}
        return node

    def parse_factor(self):
        node = self.parse_power()
        while self.current_token and self.current_token[0] == "OPERATOR" and self.current_token[1] in ("*", "/", "%", "//"):
            op = self.current_token[1]
            self.consume("OPERATOR")
            right = self.parse_power()
            node = {"type": "BinaryExpression", "operator": op, "left": node, "right": right}
        return node

    def parse_power(self):
        node = self.parse_unary()
        while self.current_token and self.current_token[0] == "OPERATOR" and self.current_token[1] == "**":
            self.consume("OPERATOR", "**")
            right = self.parse_unary()
            node = {"type": "BinaryExpression", "operator": "**", "left": node, "right": right}
        return node

    def parse_unary(self):
        if self.current_token and self.current_token[0] == "OPERATOR" and self.current_token[1] in ("+", "-", "not"):
            op = self.current_token[1]
            self.consume("OPERATOR")
            right = self.parse_unary()
            return {"type": "UnaryExpression", "operator": op, "right": right}
        return self.parse_primary()

    def parse_primary(self):
        token_type, token_value = self.current_token

        if token_type == "NUMBER":
            return self.parse_number()
        elif token_type == "STRING":
            return self.parse_string()
        elif token_type == "IDENTIFIER":
            node = self.parse_identifier()
            # Handle function call
            while self.current_token and self.current_token[0] == "SEPARATOR" and self.current_token[1] == "(":
                self.consume("SEPARATOR", "(")
                args = []
                if self.current_token[0] != "SEPARATOR" or self.current_token[1] != ")":
                    args.append(self.parse_expression())
                    while self.current_token[0] == "SEPARATOR" and self.current_token[1] == ",":
                        self.consume("SEPARATOR", ",")
                        args.append(self.parse_expression())
                self.consume("SEPARATOR", ")")
                node = {"type": "FunctionCall", "callee": node, "arguments": args}
            return node
        elif token_type == "KEYWORD" and token_value in ("True", "False", "None"):
            return self.parse_boolean_or_none()
        elif token_type == "SEPARATOR" and token_value == "(":
            self.consume("SEPARATOR", "(")
            expr = self.parse_expression()
            self.consume("SEPARATOR", ")")
            return expr
        else:
            self.error(f"Invalid primary expression: {self.current_token}")

    def parse_number(self):
        num = self.current_token[1]
        self.consume("NUMBER")
        return {"type": "Number", "value": num}

    def parse_string(self):
        value = self.current_token[1]
        self.consume("STRING")
        return {"type": "String", "value": value}

    def parse_identifier(self):
        name = self.current_token[1]
        self.consume("IDENTIFIER")
        return {"type": "Identifier", "name": name}

    def parse_boolean_or_none(self):
        value = self.current_token[1]
        self.consume("KEYWORD")
        return {"type": "Boolean" if value in ("True", "False") else "None", "value": value}

# Main execution
if __name__ == "__main__":
    tokens = read_tokens_from_json("tokens.json")
    print(f"Tokens read from tokens.json: {tokens}")

    parser = Parser(tokens)
    ast = parser.parse()

    print("Abstract Syntax Tree (AST):")
    print(json.dumps(ast, indent=2))  # Pretty print the AST
    with open("ast.json","w")as f:
        json.dump(ast,f,indent=2)
    print("ast written to ast.json")
    
