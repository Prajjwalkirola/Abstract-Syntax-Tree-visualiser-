# Abstract Syntax Tree Visualizer

## Project Description

**Abstract Syntax Tree Visualizer** is a web-based tool that takes source code from the user, performs **Lexical Analysis**, builds a **Symbol Table**, performs **Parsing**, and generates an **Abstract Syntax Tree (AST)**. If parsing is successful, the AST is visualized on the frontend; otherwise, appropriate error messages are shown.

This project avoids the use of built-in parsing libraries, making it educational and transparent for understanding how compilers work internally.

---

##  Features

- Accepts source code from the web interface (`source.txt`)
- Performs **Lexical Analysis** using `lexer.py`
- Builds a **Symbol Table** saved in `symbol_table.txt`
- Parses the tokens using `parser.py` to generate AST
- Visualizes the AST on the same HTML page
- Displays helpful syntax errors if AST is not generated

---

##  Tech Stack

| Layer         | Technology Used                |
|---------------|--------------------------------|
| Backend       | Python (no built-in parsers)   |
| Frontend      | HTML, CSS, JavaScript          |
| Visualization | Python library for tree rendering (e.g., `graphviz`, `anytree`, or `networkx`) |

---

##  Folder Structure

abstract-syntax-tree-visualizer/
├── lexer.py # Lexical analyzer (generates tokens)
├── parser.py # Parser that generates AST from tokens
├── symbol_table.txt # Stores tokens (used by parser)
├── source.txt # Contains user code input from frontend
├── templates/
│ └── index.html # HTML page for input/output
├── static/
│ ├── style.css # Styling for frontend
│ └── script.js # JS to handle UI logic
└── app.py # Backend server (e.g., Flask)



---

## 🚀 How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/abstract-syntax-tree-visualizer.git
cd abstract-syntax-tree-visualizer
````
---
## Run the Lexer
```bash
Copy
Edit
python lexer.py
This reads source.txt and saves tokens to symbol_table.txt.
````
---

## Run the Parser
```bash
Copy
Edit
python parser.py
This parses the tokens and generates an AST or shows an error.
````
---

## Start the Web Interface (Optional)
If you're using Flask:

```bash
Copy
Edit
python app.py
Then go to http://localhost:5000/ to enter source code and see the AST.
````
Web Interface
The user enters code in the frontend (index.html)

The backend saves the code into source.txt

Lexer and Parser process the code

The resulting AST is visualized in the same browser page

Notes
No third-party parsing libraries (like PLY, ANTLR, etc.) are used.

All components are custom-coded in Python.

Visualization is handled using a Python tree library and rendered on the frontend.

Contributions
Pull requests, feature ideas, and improvements are always welcome!





---



  
