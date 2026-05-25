# Data Cleaning Project

## Overview
This project provides a professional data cleaning engine with a polished HTML/CSS frontend and a Python backend.

## Files
- `clean_data.py` - Main data cleaning logic.
- `app.py` - Flask web application for file upload and processing.
- `templates/index.html` - Frontend page for uploading and downloading datasets.
- `static/css/styles.css` - Modern styling for the web interface.
- `static/js/main.js` - User interaction enhancement for the upload form.
- `uploads/` - Temporary uploaded input files.
- `outputs/` - Cleaned output files.

## Requirements
- Python 3.10+ recommended
- `pandas`
- `flask`

Install dependencies:
```powershell
pip install pandas flask
```

## Run the web app
From the project folder:

```powershell
cd "<project-folder>"
python app.py
```

Then open your browser at:

```text
http://127.0.0.1:5000
```

## Run the script directly
The backend script can still be used directly from the command line:

```powershell
python clean_data.py "Dataset for Data Analytics.xlsx"
```

If no dataset path is provided, the script defaults to:
- `Dataset for Data Analytics.xlsx`

## Output
- Web uploads are processed and saved in `outputs/`.
- Direct script runs write `cleaned_production_data.csv` or `cleaned_<inputname>.csv`.

## Notes
- Close the source file in Excel or any other app before processing.
- The web interface accepts `.csv`, `.xlsx`, and `.xls` files.
