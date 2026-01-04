import json
from services import encrypt_logic, decrypt_logic
import pandas as pd

def test_encryption_decryption():
    # Mock BIM Data
    original_bim = {
        "name": "SemanticModel",
        "compatibilityLevel": 1550,
        "model": {
            "culture": "en-US",
            "tables": [
                {
                    "name": "Sales Table",
                    "columns": [
                        {
                            "name": "Order Date",
                            "dataType": "dateTime",
                            "sourceColumn": "Order Date"
                        },
                        {
                            "name": "Sales Amount",
                            "dataType": "decimal",
                            "sourceColumn": "Sales Amount"
                        }
                    ]
                }
            ]
        }
    }

    print("Running Encryption...")
    modified_bim, changes_log = encrypt_logic(original_bim)
    
    # Check if spaces removed
    table_name = modified_bim['model']['tables'][0]['name']
    col1_name = modified_bim['model']['tables'][0]['columns'][0]['name']
    col2_name = modified_bim['model']['tables'][0]['columns'][1]['name']
    
    print(f"Modified Table Name: {table_name}")
    print(f"Modified Col1 Name: {col1_name}")
    
    assert table_name == "SalesTable"
    assert col1_name == "OrderDate"
    assert col2_name == "SalesAmount"
    
    print("Encryption Passed.")
    
    # Simulate External Modification (Identical for this test)
    encrypted_bim = modified_bim
    
    changes_df = pd.DataFrame(changes_log)
    
    print("Running Decryption...")
    restored_bim = decrypt_logic(encrypted_bim, changes_df, original_bim)
    
    r_table_name = restored_bim['model']['tables'][0]['name']
    r_col1_name = restored_bim['model']['tables'][0]['columns'][0]['name']
    
    print(f"Restored Table Name: {r_table_name}")
    print(f"Restored Col1 Name: {r_col1_name}")
    
    assert r_table_name == "Sales Table"
    assert r_col1_name == "Order Date"
    
    print("Decryption Passed.")

if __name__ == "__main__":
    test_encryption_decryption()
