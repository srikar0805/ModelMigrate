import json
import re
import pandas as pd

# ==========================================
# ENCRYPTION LOGIC
# ==========================================

def remove_spaces(name):
    """Remove spaces from the name and return the updated name."""
    if not isinstance(name, str):
        return name
    return re.sub(r"[ ().+{}]+", '', name)

def encrypt_logic(bim_data):
    """
    Applies the encryption logic: removes spaces from names and logs changes.
    Returns: (modified_bim_data, changes_log_list)
    """
    changes_log = []

    def log_change(instance_level, field_name, before, after, table_name=None, data_type=None):
        change_entry = {
            'Instance Level': instance_level,
            'Field Name': field_name,
            'Before': before,
            'After': after,
            'Table Name': table_name,
            'Data Type': data_type
        }
        changes_log.append(change_entry)

    def update_json(json_data, instance_level='Root', table_name=None):
        if isinstance(json_data, dict):
            if instance_level.endswith('.measures[list]'):
                return

            current_table_name = table_name
            if 'name' in json_data and instance_level.endswith('tables[list]'):
                current_table_name = json_data['name']

            if 'name' in json_data:
                 # A node with columns is a table: rename it and pass the new name to its children.
                 if 'columns' in json_data:
                     before = json_data['name']
                     after = remove_spaces(before)
                     data_type = json_data.get('dataType')
                     log_table_name = None
                     log_data_type = None

                     if before != after:
                        log_change(instance_level, 'name', before, after, None, None)
                        json_data['name'] = after
                        current_table_name = after

                 # A node with a sourceColumn is a column: its new name comes from the source column.
                 elif 'sourceColumn' in json_data:
                     before = json_data['name']
                     source_column = json_data.get('sourceColumn')
                     after = remove_spaces(source_column)
                     data_type = json_data.get('dataType')

                     # Columns log their table and data type so the decrypt step can find them again.
                     is_column_list = instance_level.endswith('columns[list]')
                     log_tbl = current_table_name if is_column_list else None
                     log_dt = data_type if is_column_list else None

                     log_change(instance_level, 'name', before, after, log_tbl, log_dt)
                     json_data['name'] = after

            # Recursion
            for key, value in json_data.items():
                if isinstance(value, (dict, list)):
                    update_json(value, instance_level=f"{instance_level}.{key}", table_name=current_table_name)
                    
        elif isinstance(json_data, list):
            for item in json_data:
                if isinstance(item, (dict, list)):
                    update_json(item, instance_level=f"{instance_level}[list]", table_name=table_name)

    # Run update
    update_json(bim_data)
    
    return bim_data, changes_log


# ==========================================
# DECRYPTION LOGIC
# ==========================================

def decrypt_logic(encrypted_bim, changes_log_df, original_bim):
    """
    Restores the BIM file using the changes log and original BIM (for hierarchies).
    """
    
    # helper: update table names
    tables = encrypted_bim.get('model', {}).get('tables', [])
    
    # PASS 1: Column Renaming (while Tables still have Encrypted Names)
    for index, row in changes_log_df.iterrows():
        if not pd.isna(row['Table Name']) and str(row['Table Name']).strip() != "":
            target_table_name = str(row['Table Name']).strip()
            
            field_name = row['Field Name']
            before_value = row['Before']
            after_value = row['After']
            data_type = row.get('Data Type')
            
            for table in tables:
                if table.get('name') == target_table_name:
                    columns = table.get('columns', [])
                    for column in columns:
                        if column.get('name') == after_value:
                            column['name'] = before_value
                            if data_type and 'dataType' in column:
                                column['dataType'] = data_type

    # PASS 2: Table Renaming
    for index, row in changes_log_df.iterrows():
        if pd.isna(row['Table Name']) or str(row['Table Name']).strip() == "":
            before_value = row['Before']
            after_value = row['After']
            for table in tables:
                if table.get('name') == after_value:
                    table['name'] = before_value

    # Copy Hierarchies
    source_tables = {table['name']: table for table in original_bim['model']['tables']}
    target_tables = {table['name']: table for table in encrypted_bim['model']['tables']}

    for t_name, s_table in source_tables.items():
        if t_name in target_tables:
            t_table = target_tables[t_name]
            if 'hierarchies' in s_table:
                if 'hierarchies' not in t_table:
                    t_table['hierarchies'] = []
                # Simple extend
                t_table['hierarchies'].extend(s_table['hierarchies'])

    return encrypted_bim
