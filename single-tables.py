from sql_metadata import Parser

def is_single_table_query(sql_query):
    """
    Check if the SQL query involves only one unique table.
    """
    # Create a Parser instance with the SQL query
    parser = Parser(sql_query)
    # Extract table names from the parser
    table_names = parser.tables
    # Return True if only one unique table is found
    return len(set(table_names)) == 1


def process_preds_file(input_file, output_file):
    """
    Process the preds.sql file and write queries involving only one table to the output file.
    """
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            line = line.strip()
            if not line:
                continue
            # Split the line to separate the SQL query and the database name
            if '\t' in line:
                sql_query, db_name = line.rsplit('\t', 1)
            else:
                sql_query = line
            # Check if the query involves only one table
            if is_single_table_query(sql_query):
                outfile.write('' + line + '\n')

if __name__ == '__main__':
    input_file = 'dev_gold.sql'           
    output_file = 'filtered_dev.sql' 
    process_preds_file(input_file, output_file)
    print(f"Filtered queries have been written to {output_file}")
