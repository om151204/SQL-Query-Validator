# SQL Query Validator

## **Overview**
This project is an **SQL Query Validator** that performs **Lexical Analysis, Syntax Analysis, and Semantic Analysis** on SQL queries. It supports both **DML (Data Manipulation Language) and DDL (Data Definition Language)** queries.

## **Features**
- Identifies **DML** commands: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `MERGE`
- Identifies **DDL** commands: `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, `RENAME`
- Constructs **Syntax Trees** for valid queries
- Provides **Lexical, Syntax, and Semantic Analysis**
- Detects invalid query structures and incorrect SQL syntax

## **Technologies Used**
- **Python 3+**
- **Regular Expressions (`re` module)**

## **Installation**
1. **Clone the Repository:**
   ```sh
   git clone https://github.com/YOUR-USERNAME/SQL-Query-Validator.git
