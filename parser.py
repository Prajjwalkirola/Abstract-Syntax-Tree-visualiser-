class Parser:
    def __init__(self, token_file_path):
        self.tokens = self.read_tokens(token_file_path)
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None

    def read_tokens(self, file_path):
        tokens = []
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or not line.startswith('(') or not line.endswith(')'):
                    continue #skip malformed line
                line = line.strip('()')
                parts = line.strip(',',1)
                if len(parts)!=2:
                    continue
                token_type = parts[0].strip().strip("'\"")
                token_value = parts[1].strip().strip("'\"")
                tokens.append((token_type, token_value))
        return tokens

    def error(self, message):
        raise Exception(f"Parse error: {message}")

    def advance(self):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_type):
        if self.current_token and self.current_token[0] == expected_type:
            self.advance()
        else:
            self.error(f"Expected {expected_type}, got {self.current_token}")

    def parse(self):
        return self.parse_program()

    def parse_program(self):
        statements = []
        while self.current_token:
            statements.append(self.parse_statement())
        return {"type": "Program", "body": statements}

    def parse_statement(self):
        if self.current_token[0] == "IDENTIFIER":
            return self.parse_assignment()
        else:
            self.error("Invalid statement")

    def parse_assignment(self):
        var_name = self.current_token[1]
        self.consume("IDENTIFIER")
        self.consume("OPERATOR")  # Expecting '='
        value = self.parse_expression()
        self.consume("SEPARATOR")  # Expecting ';'
        return {"type": "Assignment", "name": var_name, "value": value}

    def parse_expression(self):
        if self.current_token[0] == "NUMBER":
            return self.parse_number()
        elif self.current_token[0] == "IDENTIFIER":
            return self.parse_identifier()
        else:
            self.error("Invalid expression")

    def parse_number(self):
        value = self.current_token[1]
        self.consume("NUMBER")
        return {"type": "Number", "value": value}

    def parse_identifier(self):
        name = self.current_token[1]
        self.consume("IDENTIFIER")
        return {"type": "Identifier", "name": name}


# ----------------------------
# Run the parser from symbol table
# ----------------------------
if __name__ == "__main__":
    parser = Parser("symbol_table.txt")  # Update with your filename
    ast = parser.parse()
    print("Abstract Syntax Tree (AST):")
    print(ast)
