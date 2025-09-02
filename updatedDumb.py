import streamlit as st
import pandas as pd

def clean_amount(value):
    if isinstance(value, str):
        value = value.replace('$', '').replace(',', '')
    try:
        return float(value)
    except:
        return 0.0

st.set_page_config(page_title="📊 Excel Variance Tool", layout="wide")
st.title("📊 Excel Variance Report Tool")

# Upload both files
file1 = st.file_uploader("Upload Excel File 1", type=["xlsx", "csv"])
file2 = st.file_uploader("Upload Excel File 2", type=["xlsx", "csv"])

if file1 and file2:
    df1 = pd.read_excel(file1) if file1.name.endswith("xlsx") else pd.read_csv(file1)
    df2 = pd.read_excel(file2) if file2.name.endswith("xlsx") else pd.read_csv(file2)

    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()

    st.subheader("🔍 Select Columns")
    common_cols = list(set(df1.columns).intersection(df2.columns))

    match_cols = st.multiselect("Select Match Columns (Keys to join on)", common_cols)
    amt_cols = st.multiselect("Select Amount Columns (for variance calculation)", common_cols)

    if match_cols and amt_cols:
        if st.button("Compare and Generate Report"):
            # Clean amount columns
            for col in amt_cols:
                df1[col] = df1[col].apply(clean_amount)
                df2[col] = df2[col].apply(clean_amount)

            # Prepare prefixed columns
            df1_pref = df1[match_cols + amt_cols].copy()
            df2_pref = df2[match_cols + amt_cols].copy()

            df1_pref.columns = [f"File1_{col}" for col in df1_pref.columns]
            df2_pref.columns = [f"File2_{col}" for col in df2_pref.columns]

            # Merge on match columns
            merged = pd.merge(
                df1_pref,
                df2_pref,
                left_on=[f"File1_{col}" for col in match_cols],
                right_on=[f"File2_{col}" for col in match_cols],
                how='outer',
                suffixes=('_1', '_2')
            )

            # Calculate variances
            for col in amt_cols:
                col1 = f"File1_{col}"
                col2 = f"File2_{col}"
                merged[f"Variance_{col}"] = merged[col2] - merged[col1]

            st.success("✅ Variance calculated successfully!")
            st.subheader("📊 Variance Report")
            st.dataframe(merged)

            csv = merged.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV Report",
                data=csv,
                file_name='Variance_Report.csv',
                mime='text/csv'
            )
    else:
        st.info("👉 Please select both match and amount columns to proceed.")

