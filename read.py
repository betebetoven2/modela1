import pandas as pd
from typing import List

def read_excel_sheets_to_dataframes(file_path):
    
    dataframes = []
    
    
    for sheet_num in range(1, 13):
        try:
            df = pd.read_excel(file_path, sheet_name=str(sheet_num))
            dataframes.append(df)
            print(f"Successfully read sheet '{sheet_num}' with shape {df.shape}")
        except Exception as e:
            print(f"Error reading sheet '{sheet_num}': {e}")
            
            dataframes.append(pd.DataFrame())
    
    return dataframes


file_path = "Modela1Fixeddata.xlsx"  # Replace with your file path
df_list : List[pd.DataFrame] = read_excel_sheets_to_dataframes(file_path)

for i,  df in enumerate(df_list, 1):
    print(f"\nSheet {i}:")
    print(f"Shape: {df.shape}")
    if not df.empty:
        print(f"Columns: {list(df.columns)}")
        print(f"Types: {df.dtypes}")
        print(f"Head: {df.head()}")
        
#este script es solo para verificar que el migrado de dataset haya sido correcto