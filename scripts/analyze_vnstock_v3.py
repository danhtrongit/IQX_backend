
import inspect
import sys

sys.stdout = open('vnstock_analysis_v3.txt', 'w')

try:
    import vnstock_data
    print("--- vnstock_data.Trading methods ---")
    print(dir(vnstock_data.Trading))
    
    print("--- vnstock_data.Quote methods ---")
    print(dir(vnstock_data.Quote))

    print("--- vnstock_data.Market methods ---")
    print(dir(vnstock_data.Market))
    
except ImportError:
    pass

try:
    import vnstock
    print("--- vnstock.Trading methods ---")
    # vnstock might not have Trading class exposed at top level the same way or it might be same
    if hasattr(vnstock, 'Trading'):
        print(dir(vnstock.Trading))
    
    print("--- vnstock.Quote methods ---")
    if hasattr(vnstock, 'Quote'):
         print(dir(vnstock.Quote))
except ImportError:
    pass
