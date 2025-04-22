class Lexer:
    def __init__(self, filename):
        self.filename = filename
        self.source_code = self.load_source_code()
        self.tokens = []
        self.symbol_table = {}
        self.keywords = {"if", "else", "while", "for", "return", "def", "class", "import", "from", "print"}
        self.operators = {"+", "-", "*", "/", "%", "=", "==", "!=", "<", ">", "<=", ">="}
        self.delimiters = {"(", ")", "{", "}", "[", "]", ",", ":", ".", ";"}
        self.indent_stack = [0]  # Stack to track indentation levels
        self.line_num = 1

    def add_to_symbol_table(self, token_type, value):
        if value not in self.symbol_table:
            self.symbol_table[value] = token_type

    def load_source_code(self):
        try:
            with open(self.filename, "r") as file:
                return file.readlines()
        except FileNotFoundError:
            raise Exception(f"Error: File '{self.filename}' not found.")
        except Exception as e:
            raise Exception(f"Error reading file '{self.filename}': {e}")

    def is_identifier(self, token):
        return token[0].isalpha() or token[0] == '_' and all(c.isalnum() or c == '_' for c in token)

    def is_number(self, token):
        if token.isdigit():
            return True
        if '.' in token:
            parts = token.split('.')
            return len(parts) == 2 and all(part.isdigit() for part in parts)
        return False

    def classify_and_store(self, token):
        if token in self.keywords:
            self.tokens.append(("KEYWORD", token))
        elif token in self.operators:
            self.tokens.append(("OPERATOR", token))
        elif token in self.delimiters:
            self.tokens.append(("SEPARATOR", token))
        elif self.is_identifier(token):
            self.tokens.append(("IDENTIFIER", token))
        elif self.is_number(token):
            self.tokens.append(("NUMBER", token))
        else:
            self.tokens.append(("UNKNOWN", token))

    def tokenize(self):
        for line in self.source_code:
            stripped_line = line.rstrip()  # Remove trailing spaces
            if not stripped_line:
                continue  # Ignore empty lines
            tokens = self.process_line(line)
            self.tokens.extend(tokens)

        return self.tokens

    def process_line(self, line):
        tokens = []
        stripped_line = line.lstrip()  # Remove leading spaces
        leading_spaces = len(line) - len(stripped_line)  # Count the spaces before content

        # Handle indentation
        if leading_spaces > self.indent_stack[-1]:
            self.indent_stack.append(leading_spaces)
            tokens.append(("INDENT", leading_spaces))
        elif leading_spaces < self.indent_stack[-1]:
            while self.indent_stack and leading_spaces < self.indent_stack[-1]:
                self.indent_stack.pop()
                tokens.append(("DEDENT", leading_spaces))

        i = 0
        while i < len(line):
            char = line[i]

            if char.isspace():  # Handling whitespaces
                i += 1
                continue

            if char == "#":  # Handling single-line comments
                break  # Ignore the rest of the line

            if char in self.operators:  # Handling operators
                if i + 1 < len(line) and line[i:i + 2] in self.operators:
                    tokens.append(("OPERATOR", line[i:i + 2]))
                    self.add_to_symbol_table("OPERATOR", line[i:i + 2])
                    i += 2
                else:
                    tokens.append(("OPERATOR", char))
                    self.add_to_symbol_table("OPERATOR", char)
                    i += 1

            elif char in self.delimiters:  # Handling delimiters
                tokens.append(("SEPARATOR", char))
                self.add_to_symbol_table("SEPARATOR", char)
                i += 1

            elif char.isdigit() or (char == "." and i + 1 < len(line) and line[i + 1].isdigit()):  
                num = ""
                is_float = False
                while i < len(line) and (line[i].isdigit() or line[i] == "."):
                    if line[i] == ".":
                        is_float = True
                    num += line[i]
                    i += 1
                tokens.append(("NUMBER", num))
                self.add_to_symbol_table("NUMBER", num)

            elif char == '"':  # Handling string literals
                string_literal = ""
                i += 1  # Skip the opening quote
                while i < len(line) and line[i] != '"':
                    string_literal += line[i]
                    i += 1
                if i < len(line):  # Skip the closing quote
                    i += 1
                tokens.append(("STRING", string_literal))
                self.add_to_symbol_table("STRING", string_literal)

            elif char.isalpha() or char == "_":  # Identifiers or keywords
                ident = ""
                while i < len(line) and (line[i].isalnum() or line[i] == "_"):
                    ident += line[i]
                    i += 1
                if ident in self.keywords:
                    tokens.append(("KEYWORD", ident))
                else:
                    tokens.append(("IDENTIFIER", ident))
                self.add_to_symbol_table("IDENTIFIER", ident)


        return tokens
