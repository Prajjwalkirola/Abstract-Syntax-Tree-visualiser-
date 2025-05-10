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
        print("Tokens loaded:", self.tokens)  # Debug print

    def error(self, message):
        raise Exception(f"Parse error: {message}")

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def consume(self, token_type):
        if self.current_token is None:
            self.error(f"Unexpected end of input. Expected token type {token_type}.")
        elif self.current_token[0] == token_type:
            print(f"Consumed token: {self.current_token}")
            self.advance()
        else:
            self.error(f"Expected token type {token_type}, but got {self.current_token}")

    def parse(self):
        return self.parse_program()

    def parse_program(self):
        statements = []
        while self.current_token:
            print(f"Parsing statement: {self.current_token}")
            statements.append(self.parse_statement())
        return {"type": "Program", "body": statements}

    def parse_statement(self):
        if self.current_token[1] == "print" and self.current_token[0] in ("IDENTIFIER","KEYWORD"):
            return self.parse_print()
        elif self.current_token[1] == "if" and self.current_token[0] == "KEYWORD":
            return self.parse_if()
        elif self.current_token[0] == "IDENTIFIER":
            return self.parse_assignment()
        else:
            self.error("Invalid statement")


    def parse_assignment(self):
        var_name = self.current_token[1]
        self.consume("IDENTIFIER")
        self.consume("OPERATOR")  # '='
        expression = self.parse_expression()
        self.consume("SEPARATOR")  # ';'
        return {"type": "Assignment", "name": var_name, "value": expression}

    def parse_print(self):
        if self.current_token[0] in ("IDENTIFIER","KEYWORD") and self.current_token[1]=="print":
            self.advance()
        else:
            self.error(f"exception print keyword but got {self.current_token}")
        self.consume("SEPARATOR")   # '('
        expr = self.parse_expression()
        self.consume("SEPARATOR")   # ')'
        self.consume("SEPARATOR")   # ';'
        return {"type": "PrintStatement", "value": expr}
    
    def parse_string(self):
        value = self.current_token[1]
        self.consume("STRING")
        return{"type":"String","value": value}


    def parse_if(self):
        self.consume("KEYWORD","if")
        self.consume("SEPARATOR","(")
        condition = self.parse_expression()
        self.consume("SEPARATOR",")")
        self.consume("SEPARATOR",":") #:
        self.consume("INDENT")[1]
        body = self.parse_block(indent)
        
        if_node = {
            "type": "IfStatement",
            "condition": condition,
            "body": body,
            " elif_blocks": [],
            "else_block": None
        }
        
        while self.current_token and self.current_token[0] == "KEYWORD" and self.current_token[1] == "elif":
            self.consume("KEYWORD", "elif")
            self.consume("SEPARATOR", "(")
            elif_condition = self.parse_expression()
            self.consume("SEPARATOR", ")")
            self.consume("SEPARATOR", ":")
            indent = self.consume("INDENT")[1]
            elif_body = self.parse_block(indent)
            if_node["elif_blocks"].append({
                "condition": elif_condition,
                "body": elif_body
        })
        
        if self.current_token and self.current_token[0] == "KEYWORD" and self.current_token[1]=="else":
            self.consume("KEYWORDS","else")
            self.consume("SEPARATOR", ":")
            self.consume("INDENT")[1]
            else_body = self.parse_block(indent)
            if_node["else_block"]=else_body
        return if_node

    def parse_block(self):
        statements = []
        while self.current_token and self.current_token[0] != "DEDENT":
            statements.append(self.parse_statement())
        if self.current_token and self.current_token[0] == "DEDENT":
            self.consume("DEDENT")
        return statements
        
    def parse_expression(self):
        node= self.parse_term()
        while self.current_token and self.current_token[0]== "OPERATOR":
            op= self.current_token[1]
            self.advance()
            right= self.parse_term()
            node = {"type":"BinaryExpression","operator":op, "left":node, "right":right}
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current_token and self.current_token[0] == "OPERATOR" and self.current_token[1] in ('+', '-'):
            op = self.current_token[1]
            self.consume("OPERATOR")
            right = self.parse_factor()
            node = {"type": "BinaryExpression", "operator": op, "left": node, "right": right}
        return node

    def parse_factor(self):
        token_type, token_value=self.current_token
        if token_type == 'NUMBER':
            return self.parse_number()
        elif token_type == 'STRING':
            return self.parse_string()
        elif token_type == 'IDENTIFIER':
            return self.parse_identifier()
        elif token_type == 'SEPARATOR' and token_type=="(":
            self.consume( 'SEPARATOR',"(")
            expr = self.parse_expression()
            self.consume( 'SEPARATOR',")")
            return expr
        else:
            self.error("Invalid factor")

    def parse_number(self):
        num = self.current_token[1]
        self.consume("NUMBER")
        return {"type": "Number", "value": num}

    def parse_identifier(self):
        var_name = self.current_token[1]
        self.consume("IDENTIFIER")
        return {"type": "Identifier", "name": var_name}

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
    
