# import streamlit as st
# import pandas as pd

# def clean_amount(value):
#     if isinstance(value, str):
#         value = value.replace('$', '').replace(',', '')
#     try:
#         return float(value)
#     except:
#         return 0.0

# st.set_page_config(page_title="Excel Variance Tool", layout="wide")
# st.title("📊 Excel Variance Report Tool")

# file1 = st.file_uploader("Upload Excel File 1", type=["xlsx"])
# file2 = st.file_uploader("Upload Excel File 2", type=["xlsx"])

# if file1 and file2:
#     start_row1 = st.number_input("Start reading File 1 from row (0-indexed):", min_value=0, value=0)
#     start_row2 = st.number_input("Start reading File 2 from row (0-indexed):", min_value=0, value=0)

#     df1 = pd.read_excel(file1, skiprows=start_row1)
#     df2 = pd.read_excel(file2, skiprows=start_row2)

#     df1.columns = df1.columns.str.strip()
#     df2.columns = df2.columns.str.strip()

#     st.write("### File 1 Preview")
#     st.dataframe(df1.head())
#     st.write("### File 2 Preview")
#     st.dataframe(df2.head())

#     match_cols1 = st.multiselect("Select MATCH columns from File 1:", df1.columns.tolist())
#     match_cols2 = st.multiselect("Select MATCH columns from File 2 (in same order):", df2.columns.tolist())
#     amt_cols1 = st.multiselect("Select AMOUNT columns from File 1:", df1.columns.tolist())
#     amt_cols2 = st.multiselect("Select AMOUNT columns from File 2 (in same order):", df2.columns.tolist())

#     if len(match_cols1) == len(match_cols2) and len(amt_cols1) == len(amt_cols2):
#         if st.button("Compare and Generate Report"):
#             for col in amt_cols1:
#                 df1[col] = df1[col].apply(clean_amount)
#             for col in amt_cols2:
#                 df2[col] = df2[col].apply(clean_amount)

#             df1_pref = df1[match_cols1 + amt_cols1].copy()
#             df2_pref = df2[match_cols2 + amt_cols2].copy()

#             df1_pref.columns = [f"File1_{col}" for col in match_cols1 + amt_cols1]
#             df2_pref.columns = [f"File2_{col}" for col in match_cols2 + amt_cols2]

#             merged = pd.merge(
#                 df1_pref,
#                 df2_pref,
#                 left_on=[f"File1_{col}" for col in match_cols1],
#                 right_on=[f"File2_{col}" for col in match_cols2],
#                 how='outer'
#             )

#             for i, col in enumerate(amt_cols1):
#                 col1 = f"File1_{col}"
#                 col2 = f"File2_{amt_cols2[i]}"
#                 merged[f"Variance_{col}"] = merged[col2] - merged[col1]

#             st.success("✅ Variance calculated!")
#             st.write("### Variance Report")
#             st.dataframe(merged)

#             csv = merged.to_csv(index=False).encode('utf-8')
#             st.download_button(
#                 label="📥 Download CSV Report",
#                 data=csv,
#                 file_name='Variance_Report.csv',
#                 mime='text/csv'
#             )
#     else:
#         st.warning("⚠️ Ensure MATCH and AMOUNT columns are selected in equal counts for both files.")


# import streamlit as st
# import pandas as pd

# # Function to clean and convert amount values
# def clean_amount(value):
#     if isinstance(value, str):
#         value = value.replace('$', '').replace(',', '')
#     try:
#         return float(value)
#     except:
#         return 0.0

# # Function to standardize string columns
# def standardize_column(df, cols):
#     for col in cols:
#         df[col] = df[col].astype(str).str.strip().str.lower()
#     return df

# st.set_page_config(page_title="Excel Variance Tool", layout="wide")
# st.title("📊 Excel Variance Report Tool")

# # Upload files
# file1 = st.file_uploader("Upload Excel File 1", type=["xlsx"])
# file2 = st.file_uploader("Upload Excel File 2", type=["xlsx"])

# if file1 and file2:
#     start_row1 = st.number_input("Start reading File 1 from row (0-indexed):", min_value=0, value=0)
#     start_row2 = st.number_input("Start reading File 2 from row (0-indexed):", min_value=0, value=0)

#     df1 = pd.read_excel(file1, skiprows=start_row1)
#     df2 = pd.read_excel(file2, skiprows=start_row2)

#     # Strip whitespace from headers
#     df1.columns = df1.columns.str.strip()
#     df2.columns = df2.columns.str.strip()

#     st.write("### File 1 Preview")
#     st.dataframe(df1.head())
#     st.write("### File 2 Preview")
#     st.dataframe(df2.head())

#     # Get common columns
#     common_cols = list(set(df1.columns).intersection(set(df2.columns)))

#     match_cols = st.multiselect("Select columns to match (used to align rows):", common_cols)
#     amt_cols = st.multiselect("Select amount columns (variance will be calculated):", common_cols)
#     extra_cols = st.multiselect("Optional: Select any extra columns to include (no variance, just for context):", common_cols)

#     if st.button("Compare and Generate Report"):
#         # Clean match columns
#         df1 = standardize_column(df1, match_cols)
#         df2 = standardize_column(df2, match_cols)

#         # Clean amount columns
#         for col in amt_cols:
#             df1[col] = df1[col].apply(clean_amount)
#             df2[col] = df2[col].apply(clean_amount)

#         # Build filtered dataframes
#         use_cols = match_cols + amt_cols + extra_cols
#         df1_filtered = df1[use_cols].copy()
#         df2_filtered = df2[use_cols].copy()

#         # Rename for clarity before merging
#         df1_filtered.columns = [f"File1_{col}" for col in df1_filtered.columns]
#         df2_filtered.columns = [f"File2_{col}" for col in df2_filtered.columns]

#         # Merge on match columns
#         merged = pd.merge(
#             df1_filtered,
#             df2_filtered,
#             left_on=[f"File1_{col}" for col in match_cols],
#             right_on=[f"File2_{col}" for col in match_cols],
#             how='outer'
#         )

#         # Calculate variance for amount columns
#         for col in amt_cols:
#             col1 = f"File1_{col}"
#             col2 = f"File2_{col}"
#             merged[f"Variance_{col}"] = merged[col2] - merged[col1]

#         st.success("✅ Variance calculated!")
#         st.write("### Variance Report")
#         st.dataframe(merged)

#         # Download button
#         csv = merged.to_csv(index=False).encode('utf-8')
#         st.download_button(
#             label="📥 Download CSV Report",
#             data=csv,
#             file_name='Variance_Report.csv',
#             mime='text/csv'
#         )


import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from io import BytesIO

def clean_amount(value):
    if isinstance(value, str):
        value = value.replace('$', '').replace(',', '')
    try:
        return float(value)
    except:
        return 0.0

st.set_page_config(page_title="📊 Excel Variance Tool", layout="wide")
st.title("📈 Excel Variance & Visualization Tool")

file1 = st.file_uploader("Upload Excel File 1", type=["xlsx"])
file2 = st.file_uploader("Upload Excel File 2", type=["xlsx"])

if file1 and file2:
    start_row1 = st.number_input("Start reading File 1 from row:", min_value=0, value=0)
    start_row2 = st.number_input("Start reading File 2 from row:", min_value=0, value=0)

    df1 = pd.read_excel(file1, skiprows=start_row1)
    df2 = pd.read_excel(file2, skiprows=start_row2)

    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()

    st.subheader("📄 File Previews")
    st.dataframe(df1.head())
    st.dataframe(df2.head())

    common_columns = list(set(df1.columns) & set(df2.columns))
    st.markdown("### 🔗 Common Columns Found")
    st.write(common_columns)

    match_cols = st.multiselect("🧩 Columns to Match (Variance will be computed on amount columns):", common_columns)
    amt_cols = st.multiselect("💰 Columns to Compare for Variance:", [col for col in common_columns if df1[col].dtype in [np.float64, np.int64, object]])

    extra_cols = st.multiselect("🛠️ Extra Columns to Include (No variance, optional):", list(set(df1.columns) | set(df2.columns)))

    if st.button("🔍 Compare and Generate Variance Report"):
        for col in amt_cols:
            df1[col] = df1[col].apply(clean_amount)
            df2[col] = df2[col].apply(clean_amount)

        selected_cols = match_cols + amt_cols + extra_cols
        df1_pref = df1[selected_cols].copy()
        df2_pref = df2[selected_cols].copy()

        df1_pref.columns = [f"File1_{col}" for col in df1_pref.columns]
        df2_pref.columns = [f"File2_{col}" for col in df2_pref.columns]

        merged = pd.merge(
            df1_pref,
            df2_pref,
            left_on=[f"File1_{col}" for col in match_cols],
            right_on=[f"File2_{col}" for col in match_cols],
            how="outer",
            suffixes=('_1', '_2'),
            indicator=True
        )

        for col in amt_cols:
            merged[f"Variance_{col}"] = merged[f"File2_{col}"] - merged[f"File1_{col}"]

        merged.drop_duplicates(inplace=True)

        st.success("✅ Variance Calculated!")
        st.dataframe(merged)

        csv = merged.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Variance Report CSV", data=csv, file_name="Variance_Report.csv", mime="text/csv")

        st.markdown("---")
        st.header("📊 Interactive Visualizations")

        chart_type = st.selectbox("Choose Chart Type", ["Bar Chart", "Pie Chart", "Line Chart"])
        chart_col = st.selectbox("Choose Column for Chart", amt_cols)

        chart_df = merged[[f"File1_{chart_col}", f"File2_{chart_col}"]].dropna()
        chart_df["Label"] = merged[f"File1_{match_cols[0]}"] if match_cols else range(len(chart_df))

        if chart_type == "Bar Chart":
            chart = alt.Chart(chart_df).transform_fold(
                [f"File1_{chart_col}", f"File2_{chart_col}"],
                as_=['Source', 'Amount']
            ).mark_bar().encode(
                x='Label:N',
                y='Amount:Q',
                color='Source:N',
                tooltip=['Label', 'Source', 'Amount']
            ).interactive()
        elif chart_type == "Pie Chart":
            melted = chart_df.melt(id_vars='Label', value_vars=[f"File1_{chart_col}", f"File2_{chart_col}"])
            chart = alt.Chart(melted).mark_arc().encode(
                theta='value:Q',
                color='variable:N',
                tooltip=['Label', 'variable', 'value']
            )
        elif chart_type == "Line Chart":
            chart = alt.Chart(chart_df).transform_fold(
                [f"File1_{chart_col}", f"File2_{chart_col}"],
                as_=['Source', 'Amount']
            ).mark_line(point=True).encode(
                x='Label:N',
                y='Amount:Q',
                color='Source:N',
                tooltip=['Label', 'Source', 'Amount']
            ).interactive()

        st.altair_chart(chart, use_container_width=True)

        # Save chart as HTML
        chart_path = f"/mnt/data/{chart_type.replace(' ', '_')}.html"
        chart.save(chart_path)
        with open(chart_path, "rb") as f:
            st.download_button(f"💾 Download {chart_type} Chart as HTML", f, file_name=chart_path.split("/")[-1])

    st.markdown("---")
    st.header("🔧 Explore with Pandas Tools")
    if st.checkbox("Show Summary Statistics"):
        st.dataframe(df1.describe())
    if st.checkbox("Group by a Column"):
        group_col = st.selectbox("Choose column to group by", df1.columns)
        st.dataframe(df1.groupby(group_col).sum(numeric_only=True))
    if st.checkbox("Sort by a Column"):
        sort_col = st.selectbox("Choose column to sort by", df1.columns)
        st.dataframe(df1.sort_values(by=sort_col))
