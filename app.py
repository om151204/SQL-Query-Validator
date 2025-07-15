import re
from flask import Flask, request, render_template_string

app = Flask(__name__)

DML_COMMANDS = ["SELECT", "INSERT", "UPDATE", "DELETE", "MERGE"]
DDL_COMMANDS = ["CREATE", "ALTER", "DROP", "TRUNCATE", "RENAME"]

# Patterns for basic SQL validation
DML_PATTERNS = {
    "SELECT": re.compile(r"SELECT\s+.*\s+FROM\s+.*", re.IGNORECASE | re.DOTALL),
    "INSERT": re.compile(r"INSERT\s+INTO\s+.*", re.IGNORECASE | re.DOTALL),
    "UPDATE": re.compile(r"UPDATE\s+.*\s+SET\s+.*", re.IGNORECASE | re.DOTALL),
    "DELETE": re.compile(r"DELETE\s+FROM\s+.*", re.IGNORECASE | re.DOTALL),
    "MERGE": re.compile(r"MERGE\s+INTO\s+.*", re.IGNORECASE | re.DOTALL)
}

DDL_PATTERNS = {
    "CREATE": re.compile(r"CREATE\s+(TABLE|DATABASE|INDEX|VIEW)\s+.*", re.IGNORECASE | re.DOTALL),
    "ALTER": re.compile(r"ALTER\s+(TABLE|DATABASE|INDEX|VIEW)\s+.*", re.IGNORECASE | re.DOTALL),
    "DROP": re.compile(r"DROP\s+(TABLE|DATABASE|INDEX|VIEW)\s+.*", re.IGNORECASE | re.DOTALL),
    "TRUNCATE": re.compile(r"TRUNCATE\s+TABLE\s+.*", re.IGNORECASE | re.DOTALL),
    "RENAME": re.compile(r"RENAME\s+(TABLE|DATABASE|INDEX|VIEW)\s+.*", re.IGNORECASE | re.DOTALL)
}

class SyntaxTreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, node):
        self.children.append(node)

    def __repr__(self, level=0):
        ret = "\t" * level + repr(self.value) + "\n"
        for child in self.children:
            ret += child.__repr__(level + 1)
        return ret

def construct_syntax_tree(tokens, command):
    root = SyntaxTreeNode(command.upper())
    if command in DML_COMMANDS:
        root.add_child(SyntaxTreeNode(" ".join(tokens[1:])))
    elif command in DDL_COMMANDS:
        object_type = tokens[1].upper()
        root.add_child(SyntaxTreeNode(object_type))
        root.add_child(SyntaxTreeNode(" ".join(tokens[2:])))
    return root

def lexical_analysis(query):
    return re.findall(r'\b\w+\b|[^\s\w]', query)

def syntax_analysis(tokens):
    query_type = get_query_type(tokens)
    query = " ".join(tokens)
    command = tokens[0].upper()

    if query_type == "DML" and DML_PATTERNS.get(command, re.compile("^$")).match(query):
        return query_type, command
    elif query_type == "DDL" and DDL_PATTERNS.get(command, re.compile("^$")).match(query):
        return query_type, command
    return "INVALID", None

def semantic_analysis(query_type, command):
    if query_type == "DML" and command in DML_COMMANDS:
        return f"Valid {query_type} command: {command}."
    elif query_type == "DDL" and command in DDL_COMMANDS:
        return f"Valid {query_type} command: {command}."
    return "Syntax Error: Invalid query structure."

def get_query_type(tokens):
    if not tokens:
        return "INVALID"
    command = tokens[0].upper()
    if command in DML_COMMANDS:
        return "DML"
    elif command in DDL_COMMANDS:
        return "DDL"
    return "INVALID"

def compile_sql(query):
    tokens = lexical_analysis(query)
    query_type, command = syntax_analysis(tokens)
    if query_type == "INVALID":
        return tokens, "INVALID", None, None, "Invalid query structure."

    syntax_tree = construct_syntax_tree(tokens, command)
    semantic_result = semantic_analysis(query_type, command)
    return tokens, query_type, command, syntax_tree, semantic_result

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL Query Compiler</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        :root {
            --primary: #4361ee;
            --primary-dark: #3a0ca3;
            --secondary: #3f37c9;
            --light: #f8f9fa;
            --dark: #212529;
            --success: #4cc9f0;
            --warning: #f8961e;
            --danger: #f72585;
            --info: #4895ef;
            --gray: #6c757d;
            --light-gray: #e9ecef;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f5f7fb;
            color: var(--dark);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        header {
            text-align: center;
            margin-bottom: 2.5rem;
        }
        
        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary-dark);
            margin-bottom: 0.5rem;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .subtitle {
            color: var(--gray);
            font-size: 1.1rem;
            font-weight: 400;
        }
        
        .compiler-container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
            overflow: hidden;
            margin-bottom: 2rem;
        }
        
        .query-input {
            padding: 1.5rem;
            border-bottom: 1px solid var(--light-gray);
        }
        
        .query-input label {
            display: block;
            font-weight: 500;
            margin-bottom: 0.75rem;
            color: var(--primary-dark);
        }
        
        textarea {
            width: 100%;
            min-height: 150px;
            padding: 1rem;
            border: 2px solid var(--light-gray);
            border-radius: 8px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.95rem;
            resize: vertical;
            transition: all 0.3s ease;
        }
        
        textarea:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.2);
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.75rem 1.5rem;
            background-color: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 1rem;
        }
        
        .btn:hover {
            background-color: var(--primary-dark);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(67, 97, 238, 0.2);
        }
        
        .btn i {
            margin-right: 0.5rem;
        }
        
        .results {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            padding: 1.5rem;
        }
        
        .result-card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            padding: 1.25rem;
            transition: all 0.3s ease;
        }
        
        .result-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        
        .result-card h3 {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--primary-dark);
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
        }
        
        .result-card h3 i {
            margin-right: 0.5rem;
            color: var(--primary);
        }
        
        pre {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.85rem;
            line-height: 1.5;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .query-type {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .DML {
            background-color: rgba(76, 201, 240, 0.1);
            color: var(--success);
        }
        
        .DDL {
            background-color: rgba(72, 149, 239, 0.1);
            color: var(--info);
        }
        
        .INVALID {
            background-color: rgba(247, 37, 133, 0.1);
            color: var(--danger);
        }
        
        .syntax-tree {
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.85rem;
            line-height: 1.6;
        }
        
        .tree-node {
            margin-left: 1rem;
            position: relative;
        }
        
        .tree-node::before {
            content: "";
            position: absolute;
            left: -0.75rem;
            top: 0;
            bottom: 0;
            width: 1px;
            background-color: var(--light-gray);
        }
        
        .tree-node:first-child::before {
            top: 50%;
        }
        
        .tree-node:last-child::before {
            bottom: 50%;
        }
        
        .tree-node::after {
            content: "";
            position: absolute;
            left: -0.75rem;
            top: 50%;
            width: 0.5rem;
            height: 1px;
            background-color: var(--light-gray);
        }
        
        .tree-root {
            font-weight: bold;
            color: var(--primary);
        }
        
        .footer {
            text-align: center;
            margin-top: 3rem;
            color: var(--gray);
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            .results {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>SQL Query Compiler</h1>
            <p class="subtitle">Analyze and optimize your SQL queries with our powerful compiler</p>
        </header>
        
        <div class="compiler-container">
            <form method="post" class="query-input">
                <label for="sql_query">Enter your SQL query:</label>
                <textarea name="sql_query" id="sql_query" placeholder="SELECT * FROM users WHERE id = 1;">{{ sql_query }}</textarea>
                <button type="submit" class="btn">
                    <i class="fas fa-play"></i> Compile Query
                </button>
            </form>
            
            {% if compiled %}
            <div class="results">
                <div class="result-card">
                    <h3><i class="fas fa-code"></i> Lexical Analysis</h3>
                    <pre>{{ tokens }}</pre>
                </div>
                
                <div class="result-card">
                    <h3><i class="fas fa-tag"></i> Query Type</h3>
                    <div class="query-type {{ query_type }}">{{ query_type }}</div>
                    {% if command %}
                    <p style="margin-top: 0.5rem;">Command: <strong>{{ command }}</strong></p>
                    {% endif %}
                </div>
                
                <div class="result-card">
                    <h3><i class="fas fa-project-diagram"></i> Syntax Tree</h3>
                    <div class="syntax-tree">
                        {% if syntax_tree %}
                            {{ syntax_tree|replace("\n", "<br>")|replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")|safe }}
                        {% else %}
                            <p>No syntax tree generated</p>
                        {% endif %}
                    </div>
                </div>
                
                <div class="result-card">
                    <h3><i class="fas fa-check-circle"></i> Semantic Analysis</h3>
                    {% if query_type == "INVALID" %}
                        <p style="color: var(--danger);"><i class="fas fa-exclamation-triangle"></i> {{ semantic_result }}</p>
                    {% else %}
                        <p style="color: var(--success);"><i class="fas fa-check"></i> {{ semantic_result }}</p>
                    {% endif %}
                </div>
            </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>SQL Query Compiler &copy; 2023 | Built with Flask</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    sql_query = ""
    compiled = False
    tokens = []
    query_type = ""
    command = ""
    syntax_tree = ""
    semantic_result = ""

    if request.method == 'POST':
        sql_query = request.form['sql_query']
        tokens, query_type, command, tree, semantic_result = compile_sql(sql_query)
        syntax_tree = repr(tree) if tree else ""
        compiled = True

    return render_template_string(HTML_TEMPLATE, sql_query=sql_query, compiled=compiled,
                                tokens=tokens, query_type=query_type,
                                command=command, syntax_tree=syntax_tree,
                                semantic_result=semantic_result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
