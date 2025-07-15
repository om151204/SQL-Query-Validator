import re


DML_COMMANDS = ["SELECT", "INSERT", "UPDATE", "DELETE", "MERGE"]
DDL_COMMANDS = ["CREATE", "ALTER", "DROP", "TRUNCATE", "RENAME"]

# Patterns 
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
    tokens = re.findall(r'\b\w+\b|[^\s\w]', query)
    return tokens

def syntax_analysis(tokens):
    query_type = get_query_type(tokens)
    query = " ".join(tokens)

    if query_type == "DML":
        command = tokens[0].upper()
        if command in DML_COMMANDS and DML_PATTERNS[command].match(query):
            return query_type, command
    elif query_type == "DDL":
        command = tokens[0].upper()
        if command in DDL_COMMANDS and DDL_PATTERNS[command].match(query):
            return query_type, command
    return "INVALID", None

def semantic_analysis(query_type, command):
    if query_type == "DML":
        if command in DML_COMMANDS:
            return f"Valid {query_type} command: {command}."
        else:
            return "Invalid DML command."
    elif query_type == "DDL":
        if command in DDL_COMMANDS:
            return f"Valid {query_type} command: {command}."
        else:
            return "Invalid DDL command."
    else:
        return "Syntax Error: Invalid query structure."

def get_query_type(tokens):
    command = tokens[0].upper()
    if command in DML_COMMANDS:
        return "DML"
    elif command in DDL_COMMANDS:
        return "DDL"
    return "INVALID"

def compile_sql(query):
    print("Compiler Phases Output:")

    # Lexical Analysis Phase
    print("1. Lexical Analysis:")
    tokens = lexical_analysis(query)
    print(f"Tokens: {tokens}")

    # Syntax Analysis Phase
    print("\n2. Syntax Analysis:")
    query_type, command = syntax_analysis(tokens)
    if query_type == "INVALID":
        print("Query Type: INVALID")
        return "Invalid query structure."
    else:
        print(f"Query Type: {query_type} ({command})")

        # Build the syntax tree
        print("\n3. Syntax Tree:")
        syntax_tree = construct_syntax_tree(tokens, command)
        print(syntax_tree)

    # Semantic Analysis Phase
    print("\n4. Semantic Analysis:")
    result = semantic_analysis(query_type, command)
    print(f"Result: {result}")
    return result


if __name__ == "__main__":
    while True:
        sql_query = input('Enter the SQL query to check (or "exit" to quit): ')
        if sql_query.lower() == 'exit':
            break
        compile_sql(sql_query)

# Sample Test Cases For The Code
# SELECT * FROM employees WHERE department = 'IT';
# SELECT e.name, d.department_name FROM employees e JOIN departments d ON e.dept_id = d.id WHERE e.salary > 50000;
# INSERT INTO customers (first_name, last_name, email) VALUES ('John', 'Doe', 'john.doe@example.com');
# UPDATE products SET price = price * 1.1 WHERE category = 'Electronics';
# DELETE FROM orders WHERE order_date < '2023-01-01';
# CREATE TABLE students (id INT PRIMARY KEY, name VARCHAR(50), age INT, grade FLOAT);
# ALTER TABLE employees ADD COLUMN hire_date DATE;
# DROP TABLE temp_logs;
# TRUNCATE TABLE session_data;
# CREATE INDEX idx_last_name ON customers (last_name);
# MERGE INTO target_table USING source_table ON (target_table.id = source_table.id) 
    # WHEN MATCHED THEN UPDATE SET target_table.value = source_table.value
    # WHEN NOT MATCHED THEN INSERT (id, value) VALUES (source_table.id, source_table.value);
# SELECT department, AVG(salary) as avg_salary 
    # FROM employees 
    # WHERE id IN (SELECT employee_id FROM performance_reviews WHERE rating > 4) 
    # GROUP BY department
    # HAVING AVG(salary) > 60000;
