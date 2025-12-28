
import inspect
import sys
import os

# Redirect output to file
sys.stdout = open('vnstock_analysis.txt', 'w')

print("Python executable:", sys.executable)
print("Path:", sys.path)

try:
    import vnstock_data
    print("--- vnstock_data found ---")
    print("Dir:", dir(vnstock_data))
    if hasattr(vnstock_data, 'Company'):
         print("Company methods:", dir(vnstock_data.Company))
except ImportError as e:
    print(f"vnstock_data not installed: {e}")

try:
    import vnstock
    print("--- vnstock found ---")
    print("Dir:", dir(vnstock))
    if hasattr(vnstock, 'Company'):
         print("Company methods:", dir(vnstock.Company))
    
    # Check for functions that might return foreign data
    # stock_historical_data comes to mind
    if hasattr(vnstock, 'stock_historical_data'):
        print("stock_historical_data found")
        print(inspect.signature(vnstock.stock_historical_data))
        
except ImportError as e:
    print(f"vnstock not installed: {e}")
