
import sys
from vnstock_data.api.trading import Trading
sys.stdout = open('manual_test_trading_stats.txt', 'w')

try:
    trading = Trading(symbol='TCB', source='VCI')
    print("--- Order Stats ---")
    # check signature or help if we could, but let's try calling it
    try:
        df = trading.order_stats(to_df=True)
        print(df.head() if df is not None else "None")
    except Exception as e:
        print(e)
        
    print("--- Side Stats ---")
    try:
        df = trading.side_stats(to_df=True)
        print(df.head() if df is not None else "None")
    except Exception as e:
        print(e)

except Exception as e:
    print(e)
