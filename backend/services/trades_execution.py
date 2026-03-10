import os
import time

from .trade_reconciliation import TradeReconciliation


# ---- Traders Mismatch Execution Func ----
def traders_mismatch_execution() -> None:
    """Executes Trade Reconciliation"""

    try:
        trades_reco = TradeReconciliation()

        # ------------  Ticker Creation     ------------
        nest_df, api_219_df, api_135_df = trades_reco.read_trades_files()
        nest_excel_df = trades_reco.ticker_creator(nest_df)
        api_219_csv_df = trades_reco.ticker_creator(api_219_df)
        api_135_csv_df = trades_reco.ticker_creator(api_135_df)

        # ------------   Trades Comparison     ------------
        comparison_df, mismatch_df, missing_df, diff_df = trades_reco.compare_position_dfs(nest_excel_df, api_219_csv_df,
                                                                               api_135_csv_df, price_tolerance=0)

        # ---------------  Excel Formatting    -------------
        required_columns = ['SYMBOL_NEST', 'STRIKE_NEST', 'TYPE_NEST', 'EXPIRY_NEST', 'DC_BUYPRICE', 'BUYPRICE_API219',
                            'BUYPRICE_API135', 'DC_SELLPRICE', 'SELLPRICE_API219', 'SELLPRICE_API135', 'LTP_NEST',
                            'LTP_API219', 'LTP_API135']

        diff_df = diff_df.rename(columns={'BUYPRICE_NEST': 'DC_BUYPRICE', 'SELLPRICE_NEST': 'DC_SELLPRICE'})

        # ---- Excel Formatting ----
        trades_reco.excel_formatting_between_nest_api_(df=diff_df[required_columns])
        final_df = diff_df[required_columns]

        # ---- DF Check ---
        if not final_df.empty:
            trades_reco.excel_formatting_between_nest_api_(df=diff_df[required_columns])
        else:
            print(f"No Mismatch between in [NEST & API_219, API_135] !")

    except Exception as e:
        print(f"exception occurred while executing trades mismatch: {e}")









if __name__ == '__main__':

    traders_mismatch_execution()