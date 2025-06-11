import pandas as pd
from typing import List

def read_excel_sheets_to_dataframes(file_path):
    """
    Read Excel file with sheets named 1-12 and return list of DataFrames
    
    Args:
        file_path (str): Path to the Excel file
    
    Returns:
        list: List of DataFrames, one for each sheet
    """
    dataframes = []
    
    # Read each sheet by name (1 through 12)
    for sheet_num in range(1, 13):
        try:
            df = pd.read_excel(file_path, sheet_name=str(sheet_num))
            dataframes.append(df)
            print(f"Successfully read sheet '{sheet_num}' with shape {df.shape}")
        except Exception as e:
            print(f"Error reading sheet '{sheet_num}': {e}")
            # Append empty DataFrame if sheet doesn't exist or has error
            dataframes.append(pd.DataFrame())
    
    return dataframes

# Usage example
file_path = "Modela1Fixeddata.xlsx"  # Replace with your file path
df_list : List[pd.DataFrame] = read_excel_sheets_to_dataframes(file_path)

# Access individual DataFrames
# df_list[0] = sheet "1"
# df_list[1] = sheet "2" 
# ... and so on

# Optional: Print info about each DataFrame
for i,  df in enumerate(df_list, 1):
    print(f"\nSheet {i}:")
    print(f"Shape: {df.shape}")
    if not df.empty:
        print(f"Columns: {list(df.columns)}")
        print(f"Types: {df.dtypes}")