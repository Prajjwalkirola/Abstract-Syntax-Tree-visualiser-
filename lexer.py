class Lexer:
    def __init__(self, filename):
        self.filename = filename
        self.source_code = self.load_source_code()
        self.tokens = []
        self.symbol_table ={}
        self.keywords = {"if", "else", "while", "for", "return", "def", "class", "import", "from", "print"}
        self.operators = {"+", "-", "*", "/", "%", "=", "==", "!=", "<", ">", "<=", ">="}
        self.delimiters = {"(", ")", "{", "}", "[", "]", ",", ":", ".", ";"}
        self.indent_stack = [0] #stack to track indentation levels
        self.line_num = 1
        
    def add_to_symbol_table(self, token_type, value):
        if value not in self.symbol_table:
            self.symbol_table[value] = token_type

    def load_source_code(self):
        with open(self.filename, "r") as file:
            return file.readlines()

    def is_identifier(self, token):
        if not token[0].isalpha() and token[0] != '_':
            return False
        for char in token:
            if not (char.isalnum() or char == '_'):
                return False
        return True

    def is_number(self, token):
        if token.isdigit():
            return True
        if '.' in token:
            parts = token.split('.')
            return len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit()
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
        token = ""
        is_comment = False  # To track multi-line comments
        for line in self.source_code:
            stripped_line = line.rstrip() #remove tailing spaces
            if not stripped_line:
                continue #ignore empty lines
            tokens = self.process_line(line)
            self.tokens.extend(tokens)
        
        i = 0
        while i < len(self.source_code):
            char = self.source_code[i]
            if char.isspace():
                if token:
                    self.classify_and_store(token)
                    token = ""
            elif char in self.operators:
                if token:
                    self.classify_and_store(token)
                    token = ""
                if i+1 < len(self.code) and self.code[i:i+2] in self.operators:
                    self.tokens.append(("OPERATOR", self.code[i:i+2]))
                    i += 1
                else:
                    self.tokens.append(("OPERATOR", char))
            elif char in self.delimiters:
                if token:
                    self.classify_and_store(token)
                    token = ""
                self.tokens.append(("SEPARATOR", char))
            else:
                token += char
            i += 1
        if token:
            self.classify_and_store(token)
        return self.tokens

    def process_line(self, line):
        tokens = []
        stripped_line = line.lstrip() #remove leading spaces
        leading_spaces = len(line) - len(stripped_line) # count the spaces before content
        
        if leading_spaces > self.indent_stack[-1]:
            self.indent_stack.append(leading_spaces)
            self.tokens.append(("INDENT", leading_spaces))
        elif leading_spaces < self.indent_stack[-1]:
            while self.indent_stack and leading_spaces < self.indent_stack[-1]:
                self.indent_stack.pop()
                self.tokens.append(("DEDENT", leading_spaces))
                        
            
        i = 0
        while i < len(line):
            char = line[i]

            if char.isspace():  # Handling whitespaces
                i += 1
                continue
            
            if char == "#":  # Handling comments
                break  

            if char in self.operators:  # Handling operators
                if i + 1 < len(line) and line[i:i+2] in self.operators:
                    tokens.append(("OPERATOR", line[i:i+2]))
                    i += 2
                else:
                    tokens.append(("OPERATOR", char))
                    self.add_to_symbol_table("OPERATOR",char)
                    i += 1

            elif char in self.delimiters:  # Handling delimiters
                tokens.append(("DELIMITER", char))
                self.add_to_symbol_table("DELIMITER", char)
                i += 1

            elif char.isdigit() or (char == "." and i + 1 < len(line) and line[i + 1].isdigit()):  
                num = ""
                is_float = False
                while i < len(line) and (line[i].isdigit() or line[i] == "."):
                    if line[i] == ".":
                        is_float = True
                    num += line[i]
                    i += 1
                tokens.append(("FLOAT_LITERAL" if is_float else "INTEGER_LITERAL", num))
                self.add_to_symbol_table("LITERAL", num)

            elif char == '"' or char == "'":  # Handling string literals
                quote = char
                string = char
                i += 1
                while i < len(line) and line[i] != quote:
                    string += line[i]
                    i += 1
                string += quote
                tokens.append(("STRING_LITERAL", string))
                self.add_to_symbol_table("STRING_LITERAL", string)
                i += 1

            elif char.isalpha() or char == "_":  # Handling identifiers & keywords
                identifier = ""
                while i < len(line) and (line[i].isalnum() or line[i] == "_"):
                    identifier += line[i]
                    i += 1
                if identifier in self.keywords:
                    tokens.append(("KEYWORD", identifier))
                    self.add_to_symbol_table("KEYWORD", identifier)
                else:
                    tokens.append(("IDENTIFIER", identifier))
                    self.add_to_symbol_table("IDENTIFIER",identifier)

            else:
                i += 1  
                
        self.line_num +=1
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(("DEDENT", 0))

        return tokens



def main():
    filename = "source.py"
    lexer = Lexer(filename)
    tokens = lexer.tokenize()
    for token in tokens:
        print(token)
    print("\nSymbol Table:")
    for key, value in lexer.symbol_table.items():
        print(f"{key}: {value}")
    
if __name__ == "__main__":
    main()