import os
import pandas as pd


# --- Folder List ----
FOLDER_NAMES = ["trades_files", "pkl_files", "mismatch_results"]


# ---- Folder Creation Func ----
def folder_creator() -> None:
    """Creates Required Folder"""

    try:
        for folder_name in FOLDER_NAMES:
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
                print(f"created folder: {folder_name}")
            else:
                print(f"folder {folder_name} already exists")

    except Exception as e:
        print(f"exception occurred while creating folders: {e} !")


# ---- Check Allowed File Func ----
def check_allowed_file(filename: str, allowed_extension: set) ->bool:
    """Checks if the file is allowed or not"""

    try:
        return  '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extension

    except Exception as e:
        print(f"exception occurred while checking file: {e} !")


# ----  ----
def df_formatting(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Filters Dataframe"""

    try:
        if dataframe.empty:
            return pd.DataFrame()

        # --- Renaming Columns ---
        result_df = dataframe.rename(columns={"SYMBOL_NEST": "Symbol", "STRIKE_NEST": "Strike", "TYPE_NEST": "Type",
                                                  "EXPIRY_NEST": "Expiry"})
        # ---- Columns -----
        result_df = result_df[
            ["Symbol", "Strike", "Type", "Expiry", "DC_BUYPRICE", "BUYPRICE_API219", "BUYPRICE_API135",
             "DC_SELLPRICE", "SELLPRICE_API219", "SELLPRICE_API135", "LTP_NEST", "LTP_API219", "LTP_API135"]]

        result_df = result_df.round(2)
        return result_df

    except Exception as e:
        print(f"exception occurred while filtering dataframe: {e} !")
        return pd.DataFrame()