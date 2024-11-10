import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Function
from sqlparse.tokens import Keyword, DML
import re

def remove_table_prefixes(token):
    """
    Recursively remove table prefixes from identifiers.
    """
    if isinstance(token, Identifier):
        # If it's an identifier with dot notation, keep only the column name
        if '.' in str(token):
            parts = str(token).split('.')
            return parts[-1]
        else:
            return str(token)
    elif isinstance(token, Function):
        # Handle functions like COUNT(*), AVG(column), etc.
        return str(token).lower()
    elif isinstance(token, IdentifierList):
        # If it's a list of identifiers, process each one
        return ', '.join(remove_table_prefixes(t) for t in token.get_identifiers())
    else:
        return str(token)

def extract_tokens_of_type(parsed, token_type):
    """
    Extract tokens of a specific type from the parsed SQL.
    """
    for token in parsed.tokens:
        if token.ttype is token_type:
            yield token
        elif hasattr(token, 'tokens'):
            yield from extract_tokens_of_type(token, token_type)

def normalize_query(query):
    """
    Normalize the SQL query to minimize differences.
    """
    # Remove leading/trailing whitespace
    query = query.strip()
    # Parse the query using sqlparse
    parsed = sqlparse.parse(query)[0]
    # Initialize lists to store different parts
    select_columns = []
    order_by_columns = []
    where_conditions = ''
    from_tables = []
    group_by_columns = []
    having_conditions = ''

    # Flags to indicate the current clause
    processing_select = False
    processing_order_by = False
    processing_group_by = False
    processing_from = False

    for token in parsed.tokens:
        if token.ttype is DML and token.value.upper() == 'SELECT':
            processing_select = True
            continue

        if processing_select:
            if token.ttype is Keyword and token.value.upper() == 'FROM':
                processing_select = False
                processing_from = True
                continue
            elif isinstance(token, (sqlparse.sql.IdentifierList, sqlparse.sql.Identifier, sqlparse.sql.Function)):
                # Process SELECT columns
                select_columns.extend(extract_identifiers(token))
            else:
                continue  # Skip other tokens in SELECT clause

        if processing_from:
            if token.ttype is Keyword:
                processing_from = False
                continue
            elif isinstance(token, (sqlparse.sql.IdentifierList, sqlparse.sql.Identifier)):
                from_tables.extend(extract_identifiers(token))
            else:
                continue  # Skip other tokens in FROM clause

        if isinstance(token, sqlparse.sql.Where):
            # Process WHERE clause
            where_conditions = re.sub(r'\s+', ' ', str(token)).strip().lower()
        elif token.ttype is Keyword and token.value.upper() == 'ORDER BY':
            processing_order_by = True
            continue
        elif processing_order_by:
            if isinstance(token, (sqlparse.sql.IdentifierList, sqlparse.sql.Identifier)):
                order_by_columns.extend(extract_identifiers(token))
                processing_order_by = False
            else:
                continue  # Skip other tokens in ORDER BY clause
        elif token.ttype is Keyword and token.value.upper() == 'GROUP BY':
            processing_group_by = True
            continue
        elif processing_group_by:
            if isinstance(token, (sqlparse.sql.IdentifierList, sqlparse.sql.Identifier)):
                group_by_columns.extend(extract_identifiers(token))
                processing_group_by = False
            else:
                continue  # Skip other tokens in GROUP BY clause
        elif isinstance(token, sqlparse.sql.Having):
            # Process HAVING clause
            having_conditions = re.sub(r'\s+', ' ', str(token)).strip().lower()

    # Sort columns to ignore order
    select_columns = sorted(set(col.lower() for col in select_columns))
    order_by_columns = sorted(set(col.lower() for col in order_by_columns))
    group_by_columns = sorted(set(col.lower() for col in group_by_columns))
    from_tables = sorted(set(tbl.lower() for tbl in from_tables))

    # Reconstruct the query components
    normalized_query = f"select {', '.join(select_columns)} from {', '.join(from_tables)}"
    if where_conditions:
        normalized_query += f" {where_conditions}"
    if group_by_columns:
        normalized_query += f" group by {', '.join(group_by_columns)}"
    if having_conditions:
        normalized_query += f" {having_conditions}"
    if order_by_columns:
        normalized_query += f" order by {', '.join(order_by_columns)}"

    # Remove all whitespace for strict comparison
    normalized_query = re.sub(r'\s+', '', normalized_query)
    return normalized_query.lower()

def extract_identifiers(token):
    """
    Extracts identifiers from an Identifier, IdentifierList, or Function token.
    """
    identifiers = []
    if isinstance(token, sqlparse.sql.IdentifierList):
        for identifier in token.get_identifiers():
            identifiers.extend(extract_identifiers(identifier))
    elif isinstance(token, sqlparse.sql.Identifier):
        # Remove table prefixes
        if '.' in token.get_real_name():
            identifiers.append(token.get_real_name().split('.')[-1])
        else:
            identifiers.append(token.get_real_name())
    elif isinstance(token, sqlparse.sql.Function):
        # Handle functions like COUNT(*), AVG(column), etc.
        identifiers.append(str(token).lower())
    return identifiers


def extract_queries(file_path):
    """
    Extracts SQL queries from the given file and returns them as a list.
    """
    queries = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Remove leading '//' if present
            if line.startswith('//'):
                line = line[2:].strip()
            # Remove any leading slashes
            line = line.lstrip('/').strip()
            # Split the line to separate the SQL query and the database name
            if '\t' in line:
                sql_query, db_name = line.rsplit('\t', 1)
            else:
                sql_query = line
            queries.append(sql_query)
    return queries

def compare_queries(preds_queries, dev_queries):
    """
    Compares two lists of SQL queries and returns the ones that are different.
    """
    different_queries = []
    min_length = min(len(preds_queries), len(dev_queries))

    for i in range(min_length):
        pred_query = preds_queries[i]
        dev_query = dev_queries[i]
        # Normalize both queries
        pred_normalized = normalize_query(pred_query)
        dev_normalized = normalize_query(dev_query)
        # Compare the normalized queries
        if pred_normalized != dev_normalized:
            different_queries.append({
                'line_number': i + 1,
                'filtered_preds.sql': pred_query,
                'filtered_dev.sql': dev_query
            })

    # Handle cases where files have different lengths
    if len(preds_queries) > min_length:
        for i in range(min_length, len(preds_queries)):
            different_queries.append({
                'line_number': i + 1,
                'filtered_preds.sql': preds_queries[i],
                'filtered_dev.sql': ''
            })
    elif len(dev_queries) > min_length:
        for i in range(min_length, len(dev_queries)):
            different_queries.append({
                'line_number': i + 1,
                'filtered_preds.sql': '',
                'filtered_dev.sql': dev_queries[i]
            })

    return different_queries

def write_differences_to_file(differences, output_file):
    """
    Writes the differences between the queries to the output file.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for diff in differences:
            f.write(f"Line {diff['line_number']}:\n")
            f.write(f"filtered_preds.sql: {diff['filtered_preds.sql']}\n")
            f.write(f"filtered_dev.sql: {diff['filtered_dev.sql']}\n")
            f.write("-" * 50 + "\n")

if __name__ == '__main__':
    preds_file = 'filtered_preds.sql'
    dev_file = 'filtered_dev.sql'
    output_file = 'query_differences.txt'

    preds_queries = extract_queries(preds_file)
    dev_queries = extract_queries(dev_file)

    differences = compare_queries(preds_queries, dev_queries)

    if differences:
        write_differences_to_file(differences, output_file)
        print(f"Differences have been written to {output_file}")
    else:
        print("No differences found between the queries.")