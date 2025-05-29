import json

tokens = [ "KEYWORDS", "OPERATORS", "SEPARATORS", "IDENTIFIER", "NUMBER", "STRING", "INDENT", "DEDENT"]
class Lexer:
    def __init__(self, filename):
        self.filename = filename
        self.source_code = self.load_source_code()
        self.tokens = []
        self.symbol_table = {}
        self.keywords = {
            "if", "else", "elif", "while", "for", "return", "def", "class", 
            "import", "from", "print", "in", "not", "and", "or", "True", "False",
            "None", "break", "continue", "try", "except", "finally", "raise",
            "async", "await", "with", "as", "pass", "global", "nonlocal"
        }
        self.operators = {
            "+", "-", "*", "/", "%", "=", "==", "!=", "<", ">", "<=", ">=",
            "+=", "-=", "*=", "/=", "%=", "**", "//", "//=", "**=", "&=", "|=",
            "^=", "<<=", ">>=", "&", "|", "^", "~", "<<", ">>", "is", "is not"
        }
        self.delimiters = {
            "(", ")", "{", "}", "[", "]", ",", ":", ".", ";", "@", "->",
            "...", "\\", "`"
        }
        self.indent_stack = [0]
        self.line_num = 1
        self.column = 0

    def add_to_symbol_table(self, token_type, value):
        if value not in self.symbol_table:
            self.symbol_table[value] = token_type
    
    def save_token(self, filename="tokens.json"):
        try:
            with open(filename, "w")as f:
                json.dump(self.tokens, f)
            print(f"token stream saved to'{filename}'.")
        except Exception as e:
            print(f"failed to save tokens: {e}")

    def load_source_code(self):
        try:
            with open(self.filename, "r") as file:
                return file.readlines()
        except FileNotFoundError:
            raise Exception(f"Error: File '{self.filename}' not found.")
        except Exception as e:
            raise Exception(f"Error reading file '{self.filename}': {e}")

    def is_identifier(self, token):
        return (token[0].isalpha() or token[0] == '_') and all(c.isalnum() or c == '_' for c in token)

    def is_number(self, token):
        if token.isdigit():
            return True
        if '.' in token:
            parts = token.split('.')
            return len(parts) == 2 and all(part.isdigit() for part in parts)
        return False

    def tokenize(self):
        for line in self.source_code:
            stripped_line = line.rstrip()
            if not stripped_line:
                self.line_num += 1
                continue

            tokens_in_line = self.process_line(line)
            self.tokens.extend(tokens_in_line)
            self.line_num += 1

        return self.tokens

    def process_line(self, line):
        tokens = []
        stripped_line = line.lstrip()
        leading_spaces = len(line) - len(stripped_line)
        self.column = 0

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
            self.column = i

            if char.isspace():
                i += 1
                continue

            if char == "#":
                comment = line[i:].strip()
                tokens.append(("COMMENT", comment))
                break

            # Handle string literals with different quotes
            if char in ('"', "'"):
                quote = char
                string_literal = ""
                i += 1
                while i < len(line) and line[i] != quote:
                    if line[i] == '\\':
                        i += 1
                        if i < len(line):
                            string_literal += '\\' + line[i]
                    else:
                        string_literal += line[i]
                    i += 1
                if i >= len(line):
                    self.error(f"Unterminated string literal at line {self.line_num}")
                i += 1
                tokens.append(("STRING", string_literal))
                continue

            # Handle multi-character operators
            matched_op = False
            for op_len in range(3, 0, -1):
                if i + op_len <= len(line) and line[i:i+op_len] in self.operators:
                    tokens.append(("OPERATOR", line[i:i+op_len]))
                    self.add_to_symbol_table("OPERATOR", line[i:i+op_len])
                    i += op_len
                    matched_op = True
                    break
            if matched_op:
                continue

            # Handle delimiters
            if char in self.delimiters:
                tokens.append(("SEPARATOR", char))
                self.add_to_symbol_table("SEPARATOR", char)
                i += 1
                continue

            # Handle numbers (including hex, binary, and float)
            if char.isdigit() or (char == "." and i + 1 < len(line) and line[i + 1].isdigit()):
                num = ""
                is_hex = False
                is_binary = False
                if char == "0" and i + 1 < len(line):
                    if line[i + 1].lower() == "x":
                        is_hex = True
                        num = "0x"
                        i += 2
                    elif line[i + 1].lower() == "b":
                        is_binary = True
                        num = "0b"
                        i += 2
                while i < len(line):
                    if is_hex and line[i].lower() in "0123456789abcdef":
                        num += line[i]
                    elif is_binary and line[i] in "01":
                        num += line[i]
                    elif not is_hex and not is_binary and (line[i].isdigit() or line[i] == "."):
                        num += line[i]
                    else:
                        break
                    i += 1
                tokens.append(("NUMBER", num))
                self.add_to_symbol_table("NUMBER", num)
                continue

            # Handle identifiers and keywords
            if char.isalpha() or char == "_":
                ident = ""
                while i < len(line) and (line[i].isalnum() or line[i] == "_"):
                    ident += line[i]
                    i += 1
                if ident in self.keywords:
                    tokens.append(("KEYWORD", ident))
                else:
                    tokens.append(("IDENTIFIER", ident))
                self.add_to_symbol_table("IDENTIFIER", ident)
                continue

            # Unknown token
            tokens.append(("UNKNOWN", char))
            i += 1

        return tokens

    def error(self, message):
        raise Exception(f"Lexer error at line {self.line_num}, column {self.column}: {message}")

    def save_symbol_table(self, filename="symbol_table.txt"):
        try:
            with open(filename, "w") as file:
                for symbol, token_type in self.symbol_table.items():
                    file.write(f"{token_type}, {symbol}\n")
            print(f"Symbol table saved to '{filename}'.")
        except Exception as e:
            print(f"Failed to save symbol table: {e}")


if __name__ == "__main__":
    lexer = Lexer("source.py")  # Replace with your file
    tokens = lexer.tokenize()

    print("Tokens:\n")
    for token in tokens:
        print(token)

    lexer.save_token("tokens.json")
    lexer.save_symbol_table("symbols.txt")
