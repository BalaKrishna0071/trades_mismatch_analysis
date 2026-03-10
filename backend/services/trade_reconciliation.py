import os
import glob
import pandas as pd
import numpy as np
import xlsxwriter.utility as xl_util

# ---- Class Trade Reconciliation -----
class TradeReconciliation:

    # ---- Default Constructor ----
    def __init__(self):
        self.base_path = r"D:\Bala\trade_mismatch_analysis\backend\trades_files"
        self.nest_excel_filepath = glob.glob(os.path.join(self.base_path, "*.xlsm"))
        self.api_219_filepath = glob.glob(os.path.join(self.base_path, "data_*.csv"))
        self.api_135_filepath = glob.glob(os.path.join(self.base_path, "raw_*.csv"))

        if not self.nest_excel_filepath:
            raise FileNotFoundError(f"No Excel file found in {self.base_path} !")
        if not self.api_219_filepath:
            raise FileNotFoundError(f"No API 219 CSV file found in {self.base_path} !")
        if not self.api_135_filepath:
            raise FileNotFoundError(f"No raw CSV file found in {self.base_path} !")



    # ---- Reading Trades Files Func ----
    def read_trades_files(self):
        """Reads Trades [Excel, Csv, Pkl] files"""

        # ----  Nest DF  ----
        nest_df = pd.read_excel(self.nest_excel_filepath[0], engine="openpyxl",sheet_name="Trader Positions FO Dump", header=2,
                                usecols="A,B,C,D,E,H,K,P,Q,R,S,W")

        nest_df = nest_df.rename(columns={'Buy Price': 'BuyPrice', 'Sell Price': 'SellPrice'})
        nest_df = nest_df.dropna()

        api_219_df = pd.read_csv(self.api_219_filepath [0])
        api_135_df = pd.read_csv(self.api_135_filepath[0])

        nest_df['Maturity'] = pd.to_datetime(nest_df['Maturity'], errors='coerce')
        nest_df['Maturity'] = nest_df['Maturity'].dt.strftime('%Y-%m-%d')

        api_219_df['Maturity'] = pd.to_datetime(api_219_df['Maturity'], errors='coerce')
        api_219_df['Maturity'] = api_219_df['Maturity'].dt.strftime('%Y-%m-%d')

        api_135_df['Maturity'] = pd.to_datetime(api_135_df['Maturity'], errors='coerce')
        api_135_df['Maturity'] = api_135_df['Maturity'].dt.strftime('%Y-%m-%d')

        nest_df = nest_df[nest_df['Name'] == 'RAJEEV']
        api_219_df = api_219_df[api_219_df['Name'] == 'RAJEEV']
        api_135_df = api_135_df[api_135_df['Name'] == 'RAJEEV']

        return nest_df, api_219_df, api_135_df


    # ------- Ticker Creator Func -------
    def ticker_creator(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ticker Creation"""

        try:
            df = df.dropna()
            if 'Maturity' in df.columns:
                df = df.rename(columns={'Maturity': 'Expiry'})
            if 'Buy Price' in df.columns and 'Sell Price' in df.columns:
                df = df.rename(columns={'Buy Price': 'BuyPrice', 'Sell Price': 'SellPrice'})

            df['Expiry'] = pd.to_datetime(df['Expiry'], errors='coerce').dt.strftime('%Y-%m-%d')
            df['BuyPrice'] = df['BuyPrice'].round(2)
            df['SellPrice'] = df['SellPrice'].round(2)
            df['Strike'] = df['Strike'].astype(int)
            df.columns = df.columns.str.upper()

            # --- Create Ticker ---
            df['Ticker'] = (
                    df['SYMBOL'].astype(str) + '_' +
                    df['STRIKE'].astype(str) + '_' +
                    df['TYPE'].astype(str) + '_' +
                    df['EXPIRY'].astype(str)
            )

            # --- Correct Value Calculation ---
            df['BUYVALUE'] = df['BUYQTY'] * df['BUYPRICE']
            df['SELLVALUE'] = df['SELLQTY'] * df['SELLPRICE']

            # --- Correct Grouping ---
            data = df.groupby('Ticker', as_index=False).agg({
                'SYMBOL': 'first',
                'STRIKE': 'first',
                'TYPE': 'first',
                'EXPIRY': 'first',
                'BUYQTY': 'sum',
                'SELLQTY': 'sum',
                'BUYVALUE': 'sum',
                'SELLVALUE': 'sum',
                'LTP': 'last'
            })

            # --- Weighted Average ---
            data['BUYPRICE'] = (data['BUYVALUE'] / data['BUYQTY']).replace([float('inf')], 0).fillna(0).round(2)
            data['SELLPRICE'] = (data['SELLVALUE'] / data['SELLQTY']).replace([float('inf')], 0).fillna(0).round(2)

            return data

        except Exception as e:
            print(f"Error in ticker creation: {e}")
            return pd.DataFrame()


    # -------- Comparison Func ----------
    def compare_position_dfs(self, nest_df: pd.DataFrame, api219_df: pd.DataFrame, api135_df: pd.DataFrame, price_tolerance: float = 0.0):
        """Compares Positions Difference"""

        try:
            # Merge NEST + API219
            comparison_df = nest_df.merge(api219_df, on="Ticker", how="outer", suffixes=("_NEST", "_API219"))

            # Rename API135 columns before merging
            api135_renamed = api135_df.rename(
                columns={col: f"{col}_API135" for col in api135_df.columns if col != "Ticker"}
            )

            # Merge API135
            comparison_df = comparison_df.merge(api135_renamed, on="Ticker", how="outer")

            # Missing Tickers
            missing_df = comparison_df[comparison_df.isna().any(axis=1)]

            # Filling NaN for safe calculations
            comparison_df = comparison_df.fillna(0)

            # DIFF Columns
            cols = [
                "BUYQTY", "SELLQTY",
                "BUYPRICE", "SELLPRICE",
                "BUYVALUE", "SELLVALUE",
                "LTP"
            ]

            # Start diff_df as full comparison_df copy
            diff_df = comparison_df.copy()
            split_cols = diff_df['Ticker'].astype(str).str.split('_', expand=True)

            diff_df['SYMBOL'] = split_cols[0]
            diff_df['STRIKE'] = split_cols[1]
            diff_df['TYPE'] = split_cols[2]
            diff_df['EXPIRY'] = split_cols[3]

            for col in cols:
                diff_df[f"{col}_DIFF_219"] = (diff_df[f"{col}_NEST"] - diff_df[f"{col}_API219"])
                diff_df[f"{col}_DIFF_135"] = (diff_df[f"{col}_NEST"] - diff_df[f"{col}_API135"])

            # Mismatch Detection
            mismatch_condition = False

            for col in cols:

                if col in ["BUYPRICE", "SELLPRICE", "LTP"]:
                    mismatch_condition |= ((np.abs(diff_df[f"{col}_DIFF_219"]) > price_tolerance) |
                                           (np.abs(diff_df[f"{col}_DIFF_135"]) > price_tolerance))
                else:
                    mismatch_condition |= ((diff_df[f"{col}_DIFF_219"] != 0) |
                                           (diff_df[f"{col}_DIFF_135"] != 0))

            mismatch_df = diff_df[mismatch_condition]
            diff_only_df = diff_df[
                (diff_df.filter(like="_DIFF_") != 0).any(axis=1)
            ]

            # print("Total Tickers:", len(comparison_df))
            # print("Missing Tickers:", len(missing_df))
            # print("Mismatched Tickers:", len(mismatch_df))
            # print("Tickers With Diff:", len(diff_only_df))

            return comparison_df, mismatch_df, missing_df, diff_only_df

        except Exception as e:
            print(f"Error while comparing dataframes: {e}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


    # --------- Excel Formatting For [Nest, API 219, API 135] Func ----------
    def excel_formatting_between_nest_api_(self, df: pd.DataFrame) -> None:
        """Highlight cells which differ from DC reference columns"""

        try:
            # ---- Output File Name ----
            output_file = r"D:\Bala\trade_mismatch_analysis\backend\mismatch_results/combine_trades_comparison.xlsx"

            # ------ Excel Formatting ------
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='trades_comparison', index=False)
                workbook = writer.book
                worksheet = writer.sheets['trades_comparison']

                # ---- Highlights Color Format -----
                highlight_format = workbook.add_format({
                    'bg_color': '#FFC7CE',
                    'font_color': '#9C0006'
                })

                # ----- Comparison Pairs List -----
                comparison_pairs = [('DC_BUYPRICE', 'BUYPRICE_API219'), ('DC_BUYPRICE', 'BUYPRICE_API135'),
                                    ('DC_SELLPRICE', 'SELLPRICE_API219'), ('DC_SELLPRICE', 'SELLPRICE_API135'),
                                    ('LTP_NEST', 'LTP_API219'), ('LTP_NEST', 'LTP_API135') ]

                # ----- Iterating Through price_pairs ------
                for dc_col, target_col in comparison_pairs:
                    dc_idx = df.columns.get_loc(dc_col)
                    target_idx = df.columns.get_loc(target_col)

                    dc_letter = xl_util.xl_col_to_name(dc_idx)
                    target_letter = xl_util.xl_col_to_name(target_idx)

                    # ----- Range & Formula -----
                    range_str = f'{target_letter}2:{target_letter}{len(df) + 1}'
                    formula = f'=${target_letter}2<>${dc_letter}2'

                    # ---- Applying Range & Format ----
                    worksheet.conditional_format(range_str, {
                        'type': 'formula',
                        'criteria': formula,
                        'format': highlight_format
                    })

                # ----- Border Format ----
                border_format = workbook.add_format({'border': 1})

                # ----  Auto-adjust column width ----
                for i, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(i, i, max_len)

                # ---  Apply borders only where data exists (header + actual rows) ---
                for row in range(len(df) + 1):
                    for col in range(len(df.columns)):
                        if row == 0 or pd.notna(df.iloc[row - 1, col]):
                            cell_value = df.columns[col] if row == 0 else df.iloc[row - 1, col]
                            worksheet.write(row, col, cell_value, border_format)

                # --- apply auto filter ---
                worksheet.freeze_panes(1, 0)

            #print("Excel formatting applied successfully. !")

        except Exception as e:
            print(f"exception occurred while Formatting Excel between [Nest, API 219, API 135]: {e} !")



if __name__ == '__main__':

    trades_reco = TradeReconciliation()
    nest_df , api_219_df, api_135_df = trades_reco.read_trades_files()

    nest_trades_df = trades_reco.ticker_creator(nest_df)
    api_219_trades_df = trades_reco.ticker_creator(api_219_df)
    api_135_trades_df = trades_reco.ticker_creator(api_135_df)

    comparison_df, mismatch_df, missing_df, diff_df = trades_reco.compare_position_dfs(nest_trades_df, api_219_trades_df, api_135_trades_df)

