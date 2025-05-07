def read_tokens_from_symbol_table(filename):
    tokens = []
    with open(filename, 'r') as file:
        for line in file:
            if ':' in line:
                value, token_type = line.strip().split(':')
                tokens.append((token_type.strip(), value.strip()))
    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
        print("Tokens loaded:", self.tokens)  # Debug print

    def error(self, message):
        raise Exception(f"Parse error: {message}")

    def advance(self):
        """Move to the next token."""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    
    def consume(self, token_type):
        """Consume the current token if it matches the given token type."""
        if self.current_token is None:
            self.error(f"Unexpected end of input. Expected token type {token_type}.")
        elif self.current_token[0] == token_type:
            print(f"Consumed token: {self.current_token}")  # Debug print
            self.advance()
        else:  
            self.error(f"Expected token type {token_type}, but got {self.current_token}")

    def parse_program(self):
        """Parse the entire program."""
        statements = []
        while self.current_token:
            print(f"Parsing statement: {self.current_token}")  # Debug print}")
            statements.append(self.parse_statement())
        return {"type": "Program", "body": statements}

    def parse_statement(self):
        """Parse a single statement."""
        if self.current_token[0] == "IDENTIFIER":
            return self.parse_assignment()
        else:
            self.error("Invalid statement")

    def parse_assignment(self):
        """Parse an assignment statement."""
        var_name = self.current_token[1]
        self.consume("IDENTIFIER")
        self.consume("OPERATOR")  # Equals sign '='
        expression = self.parse_expression()
        self.consume("SEPARATOR")  # Semicolon ';'
        return {"type": "Assignment", "name": var_name, "value": expression}

    def parse_expression(self):
        return self.parse_term()
    
    def parse_term(self):
        node= self.parse_factor()
        while self.current_token and self.current_token[0]=="OPERATOR" and self.current_token[1]in('+','-'):
            op = self.current_token[1]
            self.consume("OPERATOR")
            right= self.parse_factor()
            node ={"type":"BinaryExpression","operator": op, "left": node, "right":right}
        return node
    
    def parse_factor(self):
        if self.current_token[0]=='NUMBER':
            return self.parse_number()
        elif self.current_token[0]=='IDENTIFIER':
            return self.parse_identifier()
        else:
            self.error("invalid factor")

    def parse_primary(self):
        if self.current_token[0] == "NUMBER":
            return self.parse_number()
        elif self.current_token[0] == "IDENTIFIER":
            return self.parse_identifier()
        elif self.current_token[0] == "SEPARATOR" and self.current_token[1] == '(':
            self.consume("SEPARATOR")  # consume '('
            expr = self.parse_expression()
            self.consume("SEPARATOR")  # consume ')'
            return expr
        else:
            self.error("Invalid primary expression")

    def parse_number(self):
        """Parse a number."""
        num = self.current_token[1]
        self.consume("NUMBER")
        return {"type": "Number", "value": num}

    def parse_identifier(self):
        """Parse an identifier."""
        var_name = self.current_token[1]
        self.consume("IDENTIFIER")
        return {"type": "Identifier", "name": var_name}

    def parse(self):
        return self.parse_program()

    def parse_statement(self):
        if self.current_token[0] == "IDENTIFIER":
            if self.current_token[1] == "print":
                return self.parse_print()
            else:
                return self.parse_assignment()
        else:
            self.error("Invalid statement")

    def parse_print(self):
        self.consume("IDENTIFIER")  # 'print'
        self.consume("SEPARATOR")   # '('
        expr = self.parse_expression()
        self.consume("SEPARATOR")   # ')'
        self.consume("SEPARATOR")   # ';'
        return {"type": "PrintStatement", "value": expr}


if __name__ == "__main__":
    # Read tokens from the symbol table text file
    tokens = read_tokens_from_symbol_table("symbol_table.txt")
    print(f"Tokens read from symbol_table.txt: {tokens}")  # Debug print

    # Create parser object
    parser = Parser(tokens)

    # Parse the tokens into an AST
    ast = parser.parse()

    # Display the Abstract Syntax Tree (AST)
    print("Abstract Syntax Tree (AST):")
    print(ast)
