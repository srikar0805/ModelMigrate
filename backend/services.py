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
    # Create a deep copy to avoid modifying original if passed by reference (though usually parsed fresh)
    # Using json dump/load is a lazy way to deep copy, but here we assume bim_data is fresh.
    
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

            # Update 'name' field
            if 'name' in json_data and 'columns' in json_data: # Identifying a table or similar structure? Original script logic
                # Actually original logic was: if 'name' in json_data and 'columns' in json_data:
                # Wait, generic tables usually have columns. 
                # Original logic:
                # if 'name' in json_data and 'columns' in json_data: -> It updates name
                # Let's inspect the original logic carefully.
                pass 

            # Refined logic based on original script structure which was a bit loose
            # It checks specific patterns.
            
            # Pattern 1: Table or Column definition usually
            if 'name' in json_data:
                 # Check if this node is a table or column by context of keys?
                 # Original script used: if 'name' in json_data and 'columns' in json_data: -> Table?
                 # No, 'columns' in json_data implies it IS a table.
                 if 'columns' in json_data:
                     before = json_data['name']
                     after = remove_spaces(before)
                     data_type = json_data.get('dataType')
                     # Note: Original logs table_name only if instance_level ends with columns[list]
                     # But here we are at table level.
                     log_table_name = None
                     log_data_type = None
                     
                     if before != after:
                        # Original: log_change(..., table_name if field_name == 'name' and instance_level.endswith('columns[list]') else None ...)
                        # Since we are likely at Table level, table_name param is None or previous.
                        # For Table Rename:
                        log_change(instance_level, 'name', before, after, None, None)
                        json_data['name'] = after
                        # Update current_table_name for children
                        current_table_name = after
                 
                 # Pattern 2: Column (usually inside columns list)
                 # Original script logic for generic walking:
                 # if 'name' in json_data and 'sourceColumn' in json_data:
                 elif 'sourceColumn' in json_data:
                     before = json_data['name']
                     source_column = json_data.get('sourceColumn')
                     after = remove_spaces(source_column)
                     data_type = json_data.get('dataType')
                     
                     # Determine if we log table name
                     # The original script passed 'table_name' down.
                     # log_change logic: table_name if field_name == 'name' and instance_level.endswith('columns[list]') else None
                     
                     is_column_list = instance_level.endswith('columns[list]')
                     log_tbl = current_table_name if is_column_list else None
                     log_dt = data_type if is_column_list else None
                     
                     # if before != after: # Original had this commented out
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
