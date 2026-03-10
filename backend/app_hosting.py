import os
import shutil
import pandas as pd

from flask_cors import CORS
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
from services import trades_execution
from utilities import  folder_creator, check_allowed_file, df_formatting


# ---- Folder Name ----
UPLOAD_FOLDER = 'trades_files'

# ---- Allowed Extension ----
ALLOWED_EXTENSIONS = {"csv", "xlsm", "pkl"}


# ---- APP Config ----
app = Flask(__name__)
CORS(app)
app.config["JSON_SORT_KEYS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER



# ---- API 1 ----
@app.route("/")
def server_running():
    """Server Running Check"""

    folder_creator()
    return jsonify({
        "status": "success",
        "message": "server running",
        "code": 200
    })


# ---- API 2 ----
@app.route("/upload_trades_files", methods=["POST"])
def upload_trades_files():
    """Uploads Trades Files"""

    try:
        # --- File Check ---
        if 'file' not in request.files:
            return  jsonify({"status": "failed", "message": "No file part"}), 400

        # --- Empty File Check ---
        files = request.files.getlist('file')

        # --- File Empty Check ---
        for file in files:
            if file.filename == '':
                return jsonify({"status": "failed", "message": "No selected file"}), 400

        responses = []
        # ---- File Name & Extension Check -----
        for file in files:
            if file and check_allowed_file(file.filename, allowed_extension=ALLOWED_EXTENSIONS):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                responses.append({"status": "success", "filename": filename})
            else:
                responses.append({"status": "failed","filename": file.filename, "message": "Invalid file format"})


        return jsonify({
            "status": "success",
            "message": "file uploaded successfully",
            "code": 200,
            "files": responses
        }), 200



    except Exception as e:
        return jsonify({
            "status": "failed",
            "message": "exception occurred",
            "code": 500,
            "error": {
                "error message": str(e)
            }
        }), 500


# ---- API 3 ----
@app.route("/run_mismatch", methods=["GET"])
def run_mismatch():
    """Runs Mismatch Check"""

    trades_execution.traders_mismatch_execution()

    return jsonify({
        "status": "success",
        "message": "run mismatch",
        "code": 200
    })


# ---- API 4 ----
@app.route("/get_mismatch_result", methods=["GET"])
def get_mismatch_result():
    """Gets Mismatch Result"""

    try:
        # ---- DF ----
        if not  os.path.exists(r"D:\Bala\trade_mismatch_analysis\backend\mismatch_results\combine_trades_comparison.xlsx"):
            return jsonify({"status": "failed", "message": "file not found"}), 400

        # ---- Reading DF ----
        df = pd.read_excel(r"D:\Bala\trade_mismatch_analysis\backend\mismatch_results\combine_trades_comparison.xlsx")

        # --- Check Empty DF ---
        if df.empty:
            return jsonify({"status": "failed", "message": "No mismatch result"}), 400

        filtered_df = df_formatting(dataframe=df)
        return jsonify({
            "status": "success",
            "message": "mismatch result",
            "code": 200,
            "data": filtered_df.to_dict(orient="records")
        }), 200

    except Exception as e:
        return jsonify({
            "status": "failed",
            "message": "exception occurred",
            "code": 500,
            "error": {
                "error message": str(e)
            }
        }), 500


@app.route("/reset_mismatch", methods=["DELETE"])
def reset_mismatch():
    """Resets Mismatch Check"""

    try:
        folder_paths = [r"D:\Bala\trade_mismatch_analysis\backend\mismatch_results", r"D:\Bala\trade_mismatch_analysis\backend/trades_files"]
        for path in folder_paths:
            # Remove all contents inside the folder
            if os.path.exists(path):
                shutil.rmtree(path)
            # Recreate the folder safely
            os.makedirs(path, exist_ok=True)

        return jsonify({
            "status": "success",
            "message": "reset done",
            "code": 200
        })

    except Exception as e:
        return jsonify({
            "status": "failed",
            "message": "exception occurred",
            "code": 500,
            "error": {
                "error_message": str(e)
            }
        }), 500


if __name__ == '__main__':
   app.run(port=5007, debug=True)