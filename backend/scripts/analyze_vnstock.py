
import inspect
import sys

def print_foreign_methods(module_name, obj):
    print(f"--- Analyzing {module_name} ---")
    try:
        # Inspect all members
        for name, member in inspect.getmembers(obj):
            if "foreign" in name.lower() or "khoi_ngoai" in name.lower() or "daily" in name.lower() or "trade" in name.lower():
                print(f"Found candidate: {name} (Type: {type(member)})")
                if inspect.isfunction(member) or inspect.ismethod(member):
                   try:
                       print(f"  Signature: {inspect.signature(member)}")
                   except:
                       pass
                       
        # specific check for Company class if present
        if hasattr(obj, 'Company'):
            print(f"--- Analyzing Company class in {module_name} ---")
            company_cls = getattr(obj, 'Company')
            for name, member in inspect.getmembers(company_cls):
                 if "foreign" in name.lower() or "khoi_ngoai" in name.lower() or "daily" in name.lower() or "trade" in name.lower():
                     print(f"  Company method/attr: {name}")

        # specific check for stock_historical_data or similar
        potential_funcs = ['stock_historical_data', 'quote', 'foreign_trade']
        for func in potential_funcs:
            if hasattr(obj, func):
                print(f"  Found known function: {func}")

    except Exception as e:
        print(f"Error analyzing {module_name}: {e}")

print("Start analysis...")

try:
    import vnstock_data
    print_foreign_methods("vnstock_data", vnstock_data)
    
    # Check if there is a 'Trading' class as hinted by search results
    if hasattr(vnstock_data, 'Trading'):
        print("--- Analyzing Trading class in vnstock_data ---")
        print_foreign_methods("vnstock_data.Trading", vnstock_data.Trading)
        
except ImportError:
    print("vnstock_data not installed")

try:
    import vnstock
    print_foreign_methods("vnstock", vnstock)
except ImportError:
    print("vnstock not installed")

