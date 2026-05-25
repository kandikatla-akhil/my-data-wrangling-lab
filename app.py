import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
import clean_data

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
ALLOWED_EXTENSIONS = {"csv", "xls", "xlsx"}

app = Flask(__name__)
app.secret_key = "replace-with-a-strong-secret-key"
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
app.config["OUTPUT_FOLDER"] = OUTPUT_DIR
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        flash("No file part in the request.", "error")
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        flash("Please choose a file to upload.", "error")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("Unsupported file type. Upload a CSV, XLSX, or XLS file.", "error")
        return redirect(url_for("index"))

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = secure_filename(file.filename)
    save_name = f"{timestamp}_{filename}"
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], save_name)
    file.save(input_path)

    try:
        output_name = clean_data.clean_dataset(input_path, output_dir=app.config["OUTPUT_FOLDER"])
        if not output_name:
            flash("Data cleaning failed. Please inspect the uploaded file and try again.", "error")
            return redirect(url_for("index"))

        download_url = url_for("download_file", filename=output_name)
        return render_template("index.html", success=True, output_file=output_name, download_url=download_url)
    except Exception as error:
        flash(f"Processing failed: {error}", "error")
        return redirect(url_for("index"))


@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
