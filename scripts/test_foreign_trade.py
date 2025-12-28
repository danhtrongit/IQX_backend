
import sys
from vnstock_data import Trading

# Redirect output for safety (though I will run it and check output)
sys.stdout = open('vnstock_foreign_test.txt', 'w')

print("--- Testing Foreign Trade Data ---")
try:
    # Initialize Trading with a symbol
    trading = Trading(symbol='VCB', source='VCI')
    print("Trading initialized.")
    
    # Call foreign_trade
    # Try with no arguments first, as symbol is already in init
    df = trading.foreign_trade()
    
    if df is not None:
        print("Data type:", type(df))
        try:
             # Assume pandas DataFrame
             print("Columns:", df.columns.tolist())
             print("First 5 rows:")
             print(df.head())
        except:
             print("Content:", df)
    else:
        print("Returned None")
        
except Exception as e:
    print(f"Error: {e}")
