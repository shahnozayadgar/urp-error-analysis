import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Function, Parenthesis
from sqlparse.tokens import Keyword, DML, Whitespace, Punctuation
import re

def normalize_query(query):
    """
    Normalize the SQL query to minimize differences.
    Steps:
    1. Remove table prefixes that match the table in FROM clause.
    2. Lowercase all SQL keywords and functions.
    3. Ensure ORDER BY directions are specified (default to ASC).
    4. Sort SELECT and ORDER BY columns for consistency.
    5. Remove excessive whitespace.
    """
    query = query.strip()
    parsed = sqlparse.parse(query)[0]
    
    select_columns = []
    order_by_columns = []
    from_tables = []
    where_conditions = ''
    group_by_columns = []
    having_conditions = ''
    
    table_name = None  # To store the main table name from FROM clause
    
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
            elif isinstance(token, (IdentifierList, Identifier, Function)):
                # Extract and process SELECT columns
                select_columns.extend(extract_identifiers(token, table_name))
            else:
                continue  # Skip other tokens in SELECT clause

        elif processing_from:
            if token.ttype is Keyword:
                processing_from = False
                continue
            elif isinstance(token, Identifier):
                # Assuming single table in FROM clause
                table_name = token.get_real_name().lower()
                from_tables.append(table_name)
            elif isinstance(token, IdentifierList):
                for identifier in token.get_identifiers():
                    tbl_name = identifier.get_real_name().lower()
                    from_tables.append(tbl_name)
            else:
                continue  # Skip other tokens in FROM clause

        elif isinstance(token, sqlparse.sql.Where):
            # Process WHERE clause
            where_conditions = process_conditions(token, table_name)
        elif token.ttype is Keyword and token.value.upper() == 'GROUP BY':
            processing_group_by = True
            continue
        elif processing_group_by:
            if isinstance(token, (IdentifierList, Identifier, Function)):
                group_by_columns.extend(extract_identifiers(token, table_name))
                processing_group_by = False
            else:
                continue
        elif isinstance(token, sqlparse.sql.Having):
            # Process HAVING clause
            having_conditions = process_conditions(token, table_name)
        elif token.ttype is Keyword and token.value.upper() == 'ORDER BY':
            processing_order_by = True
            continue
        elif processing_order_by:
            if isinstance(token, (IdentifierList, Identifier, Function)):
                order_by_columns.extend(extract_order_by_identifiers(token, table_name))
                processing_order_by = False
            else:
                continue

    # Sort and de-duplicate columns for consistency
    select_columns = sorted(set(col.lower() for col in select_columns))
    order_by_columns = sorted(set(col.lower() for col in order_by_columns))
    group_by_columns = sorted(set(col.lower() for col in group_by_columns))
    from_tables = sorted(set(tbl.lower() for tbl in from_tables))

    # Reconstruct the normalized query
    normalized_query = f"select {', '.join(select_columns)} from {', '.join(from_tables)}"

    if where_conditions:
        normalized_query += f" where {where_conditions}"
    if group_by_columns:
        normalized_query += f" group by {', '.join(group_by_columns)}"
    if having_conditions:
        normalized_query += f" having {having_conditions}"
    if order_by_columns:
        normalized_query += f" order by {', '.join(order_by_columns)}"

    # Remove all whitespace for strict comparison
    normalized_query = re.sub(r'\s+', '', normalized_query)
    return normalized_query.lower()

def extract_identifiers(token, table_name=None):
    """
    Extracts identifiers from an Identifier, IdentifierList, or Function token.
    Removes table prefixes if they match the table_name.
    """
    identifiers = []
    if isinstance(token, IdentifierList):
        for identifier in token.get_identifiers():
            identifiers.extend(extract_identifiers(identifier, table_name))
    elif isinstance(token, Identifier):
        # Remove table prefixes if they match the table_name
        value = token.value
        if table_name and value.lower().startswith(table_name + '.'):
            # Remove the table prefix
            real_name = value[len(table_name)+1:]
            identifiers.append(real_name.lower())
        else:
            real_name = token.get_real_name()
            if real_name:
                identifiers.append(real_name.lower())
    elif isinstance(token, Function):
        # Process function: lowercase function name and process its arguments
        func_name = token.get_name().lower()
        args = []
        for subtoken in token.tokens:
            if isinstance(subtoken, Parenthesis):
                inner_args = extract_identifiers(subtoken, table_name)
                args.extend(inner_args)
        if args:
            func_call = f"{func_name}({', '.join(args)})"
            identifiers.append(func_call)
        else:
            identifiers.append(f"{func_name}()")
    return identifiers

def extract_order_by_identifiers(token, table_name=None):
    """
    Extracts identifiers from ORDER BY clause.
    Ensures that direction is specified (default to ASC).
    """
    orderings = []
    if isinstance(token, IdentifierList):
        for identifier in token.get_identifiers():
            orderings.extend(extract_order_by_identifiers(identifier, table_name))
    elif isinstance(token, Identifier):
        value = token.value
        if table_name and value.lower().startswith(table_name + '.'):
            real_name = value[len(table_name)+1:]
        else:
            real_name = token.get_real_name()
        direction = 'ASC'  # default
        if token.get_ordering():
            direction = token.get_ordering().lower()
        orderings.append(f"{real_name.lower()} {direction}")
    elif isinstance(token, Function):
        func = extract_identifiers(token, table_name)[0]
        orderings.append(f"{func} ASC")  # default direction
    return orderings

def process_conditions(token, table_name=None):
    """
    Processes WHERE and HAVING clauses by removing table prefixes that match the main table
    and lowercasing the conditions.
    """
    processed_tokens = []
    for tok in token.tokens:
        if isinstance(tok, Identifier):
            processed = remove_table_prefixes(tok, table_name)
            processed_tokens.append(processed.lower())
        elif isinstance(tok, Function):
            processed = remove_table_prefixes(tok, table_name)
            processed_tokens.append(processed.lower())
        elif tok.ttype in (Keyword, DML, Punctuation):
            processed_tokens.append(tok.value.lower())
        elif tok.ttype is Whitespace:
            processed_tokens.append(' ')
        else:
            processed_tokens.append(str(tok).lower())
    
    # Reconstruct the condition string with spaces where appropriate
    condition_str = ''.join(processed_tokens)
    # Remove multiple spaces
    condition_str = re.sub(r'\s+', ' ', condition_str).strip()
    return condition_str

def remove_table_prefixes(token, table_name=None):
    """
    Recursively remove table prefixes from identifiers if they match the table name.
    """
    if isinstance(token, Identifier):
        parts = str(token).split('.')
        # Only remove prefix if it matches the table name in the FROM clause
        if len(parts) > 1 and parts[0].strip().lower() == table_name:
            return parts[-1].strip()
        else:
            return str(token).strip()
    elif isinstance(token, Function):
        func_name = token.get_name().lower()
        args = []
        for subtoken in token.tokens:
            if isinstance(subtoken, Parenthesis):
                # Extract arguments within parentheses
                inner_args = []
                for inner_token in subtoken.tokens:
                    if not inner_token.is_whitespace and not inner_token.match(Punctuation, ','):
                        normalized_arg = remove_table_prefixes(inner_token, table_name)
                        inner_args.append(normalized_arg)
            elif not subtoken.is_whitespace and not subtoken.match(Punctuation, ','):
                args.append(remove_table_prefixes(subtoken, table_name))
        return f"{func_name}({', '.join(args)})"
    elif isinstance(token, IdentifierList):
        return ', '.join(remove_table_prefixes(t, table_name) for t in token.get_identifiers())
    elif isinstance(token, Parenthesis):
        inner = [remove_table_prefixes(t, table_name) for t in token.tokens if not t.is_whitespace and not t.match(Punctuation, ',')]
        return f"({', '.join(inner)})"
    else:
        return str(token).strip()

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
        # Debugging: Print normalized queries
        #print(f"Line {i+1}:")
        #print(f"Pred Normalized: {pred_normalized}")
        #print(f"Dev Normalized:   {dev_normalized}")
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
    preds_file = 'filtered_train_pred_current.sql'        # Prediction file
    dev_file = 'filtered_train_gold_current.sql'            # Development/reference file
    output_file = 'query_differences_train_current.txt'    # Output file for differences

    preds_queries = extract_queries(preds_file)
    dev_queries = extract_queries(dev_file)

    differences = compare_queries(preds_queries, dev_queries)

    if differences:
        write_differences_to_file(differences, output_file)
        print(f"Differences have been written to {output_file}")
    else:
        print("No differences found between the queries.")
