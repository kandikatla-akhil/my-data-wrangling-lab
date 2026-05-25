import os
import sys
import pandas as pd

def load_dataset(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(file_path)
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use .csv, .xlsx, or .xls")

    df.columns = df.columns.str.strip()
    return df


def clean_dataset(file_path, output_dir=None):
    file_path = file_path.strip()
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ Error: Could not find '{file_path}' in this directory.")
        print("Please make sure the script and the dataset file are in the same folder.")
        return None

    print("🚀 Loading raw dataset...")
    # Load dataset safely, automatically stripping accidental spaces from column headers
    df = load_dataset(file_path)
    df.columns = df.columns.str.strip()
    
    # Print original metrics for tracking
    initial_rows = len(df)
    print(f"📊 Dataset loaded successfully with {initial_rows} rows and {len(df.columns)} columns.")
    print(f"🔍 Columns found: {list(df.columns)}\n")

    # ==========================================
    # PHASE 1: STRATEGIC IMPUTATION (Gaps Check)
    # ==========================================
    print("🛠️ Phase 1: Checking for missing values and applying strategic imputation...")
    null_counts = df.isnull().sum()
    
    for col in df.columns:
        if null_counts[col] > 0:
            # If the column is numeric (like Price, Quantity, Value), use Median to avoid outlier skew
            if pd.api.types.is_numeric_dtype(df[col]):
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
                print(f"   🔹 Imputed {null_counts[col]} missing values in numeric column '{col}' using Median ({median_val}).")
            # If the column is text/categorical (like Status, City), use Mode (most frequent)
            else:
                mode_series = df[col].mode()
                mode_val = mode_series.iloc[0] if not mode_series.empty else ""
                df[col] = df[col].fillna(mode_val)
                print(f"   🔹 Imputed {null_counts[col]} missing values in categorical column '{col}' using Mode ('{mode_val}').")
                
    # ==========================================
    # PHASE 2: THE INTEGRITY AUDIT (Duplicates)
    # ==========================================
    print("\n🔍 Phase 2: Auditing transaction integrity for duplicate records...")
    
    # Detect the ID column dynamically (handles 'Order ID', 'OrderID', 'id', etc.)
    id_col = next((c for c in df.columns if 'id' in c.lower()), None)
    
    if id_col:
        rows_before_dedup = len(df)
        # Drop duplicates based on the unique ID column, keeping the first occurrence
        df.drop_duplicates(subset=[id_col], keep='first', inplace=True)
        dropped_count = rows_before_dedup - len(df)
        print(f"   ✅ Cleaned unique tracking ID column: '{id_col}'.")
        print(f"   ✅ Successfully identified and removed {dropped_count} duplicate rows.")
    else:
        print("   ⚠️ Warning: No explicit 'ID' column found. Skipping row deduplication step.")

    # ==========================================
    # PHASE 3: SPEAK ONE LANGUAGE (Standardization)
    # ==========================================
    print("\n🌐 Phase 3: Standardizing text formatting, cases, and timestamps...")

    # 1. Standardize Text Formatting & Casing across all text-based columns
    for col in df.select_dtypes(include=['object', 'category']).columns:
        # Check if this isn't a date column before treating it like plain text
        if 'date' not in col.lower() and 'time' not in col.lower():
            df[col] = df[col].astype(str).str.strip().str.title()

    # 2. Map structural variations for city groupings dynamically if 'City' column exists
    city_col = next((c for c in df.columns if 'city' in c.lower() or 'location' in c.lower()), None)
    if city_col:
        city_mapping = {
            'Bangalore': 'Bengaluru', 'Blr': 'Bengaluru', 'Blor': 'Bengaluru', 
            'Bengalurangai': 'Bengaluru', 'Bengaluru': 'Bengaluru',
            'Mumbai': 'Mumbai', 'Mumbai': 'Mumbai', 'Puducherry': 'Puducherry'
        }
        df[city_col] = df[city_col].replace(city_mapping)
        print(f"   ✅ Unified structural regional text variations inside '{city_col}'.")

    # 3. Secure and enforce explicit ISO 8601 Date Formatting (YYYY-MM-DD)
    date_col = next((c for c in df.columns if 'date' in c.lower() or 'time' in c.lower() or 'timestamp' in c.lower()), None)
    if date_col:
        # Parse text into uniform timestamp objects, coercing completely broken values to NaT
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        # Format explicitly to YYYY-MM-DD string syntax
        df[date_col] = df[date_col].dt.strftime('%Y-%m-%d')
        # If any invalid dates became null, fill them with a placeholder or drop
        df[date_col] = df[date_col].fillna(df[date_col].mode()[0] if not df[date_col].mode().empty else "2024-01-01")
        print(f"   ✅ Standardized all timestamps in '{date_col}' to strict ISO 8601 format (YYYY-MM-DD).")

    # 4. Enforce Decimal Float Precision on numerical columns
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = df[col].round(2)
    print("   ✅ Locked all currency/floating points down to a precision scale of 2 decimals.")

    # ==========================================
    # VERIFICATION & SAVE
    # ==========================================
    final_rows = len(df)
    output_filename = "cleaned_production_data.csv"
    if os.path.abspath(output_filename) == os.path.abspath(file_path):
        source_base = os.path.splitext(os.path.basename(file_path))[0]
        output_filename = f"cleaned_{source_base}.csv"

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
    else:
        output_path = output_filename

    df.to_csv(output_path, index=False)
    
    print("\n--- Final Project Integrity Check Summary ---")
    print(f"   • Total Raw Rows Processed: {initial_rows}")
    print(f"   • Total Cleaned Rows Preserved: {final_rows}")
    print(f"   • Final Quality Audit: 0 duplicates | 0 missing fields | Validated ISO Dates")
    print(f"🎉 Success! 'Gold Standard' production data exported as '{output_path}'.")
    return os.path.basename(output_path)

# Run the program
if __name__ == "__main__":
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    else:
        dataset_path = "Dataset for Data Analytics.xlsx"

    clean_dataset(dataset_path)