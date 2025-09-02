 
import streamlit as st
import pandas as pd
import plotly.express as px 
 
# ------------------ Page Setup ------------------ #
st.set_page_config(page_title="Excel/CSV Comparison Tool", layout="wide", initial_sidebar_state="collapsed")
st.title("📊 Excel/CSV Comparison Tool with Interactive Charts")
 
# ------------------ Utility Functions ------------------ #
def clean_amount(value):
    if isinstance(value, str):
        value = value.replace('$', '').replace(',', '').replace('₹', '').replace('%', '')
    try:
        return float(value)
    except:
        return 0.0
 
def get_numeric_columns(df, exclude=[]):
    numeric_cols = []
    for col in df.columns:
        if col in exclude:
            continue
        try:
            cleaned = df[col].astype(str).str.replace(r'[\$,₹,%]', '', regex=True).str.replace(',', '')
            pd.to_numeric(cleaned, errors='raise')
            numeric_cols.append(col)
        except:
            continue
    return numeric_cols
 
def get_categorical_columns(df):
    return [col for col in df.columns if df[col].dtype == 'object' or df[col].nunique() < 50]
 
def create_chart(df, chart_type, x_col, y_col, title):
    try:
        df_clean = df.copy()
        if y_col in df_clean.columns:
            df_clean[y_col] = df_clean[y_col].astype(str).str.replace(r'[\\$,₹,%]', '', regex=True).str.replace(',', '')
            df_clean[y_col] = pd.to_numeric(df_clean[y_col], errors='coerce')
 
        if chart_type == "Bar Chart":
            fig = px.bar(df_clean, x=x_col, y=y_col, title=title)
        elif chart_type == "Line Chart":
            fig = px.line(df_clean, x=x_col, y=y_col, title=title)
        elif chart_type == "Scatter Plot":
            fig = px.scatter(df_clean, x=x_col, y=y_col, title=title)
        elif chart_type == "Histogram":
            fig = px.histogram(df_clean, x=y_col, title=f"Distribution of {y_col}")
        elif chart_type == "Box Plot":
            fig = px.box(df_clean, x=x_col, y=y_col, title=title)
        elif chart_type == "Pie Chart":
            pie_data = df_clean.groupby(x_col)[y_col].sum().reset_index()
            fig = px.pie(pie_data, values=y_col, names=x_col, title=title)
        else:
            fig = px.bar(df_clean, x=x_col, y=y_col, title=title)
 
        fig.update_layout(height=500)
        return fig
    except Exception as e:
        st.error(f"Error creating chart: {e}")
        return None
 
# ------------------ Tabs ------------------ #
tab1, tab2 = st.tabs(["📁 Upload & Compare", "📊 Visualize Data"])
 
with tab1:
    st.subheader("📂 Upload Excel/CSV Files")
    col1, col2 = st.columns(2)
 
    with col1:
        file1 = st.file_uploader("Upload File 1", type=["xlsx", "csv"], key="file1")
    with col2:
        file2 = st.file_uploader("Upload File 2", type=["xlsx", "csv"], key="file2")
 
    if file1 and file2:
        df1 = pd.read_excel(file1) if file1.name.endswith("xlsx") else pd.read_csv(file1)
        df2 = pd.read_excel(file2) if file2.name.endswith("xlsx") else pd.read_csv(file2)
 
        df1.columns = df1.columns.str.strip()
        df2.columns = df2.columns.str.strip()
 
        df1.dropna(how='all', inplace=True)
        df2.dropna(how='all', inplace=True)
 
        st.session_state.df1 = df1
        st.session_state.df2 = df2
 
        st.write("### File 1 Preview")
        st.dataframe(df1.head())
        st.write("### File 2 Preview")
        st.dataframe(df2.head())
 
        common_columns = list(set(df1.columns) & set(df2.columns))
 
        match_cols = st.multiselect("🧩 Select MATCH columns (common in both files):", common_columns)
        amt_cols = st.multiselect("💰 Select AMOUNT columns (common in both files):", common_columns)
 
        extra_cols_file1 = st.multiselect("📄 Extra Columns from File 1", list(df1.columns))
        extra_cols_file2 = st.multiselect("📄 Extra Columns from File 2", list(df2.columns))
 
        if (match_cols or amt_cols) and st.button("🔍 Compare and Generate Report"):
            for col in amt_cols:
                df1[col] = df1[col].apply(clean_amount)
                df2[col] = df2[col].apply(clean_amount)
 
            use_cols1 = list(set(match_cols + amt_cols + extra_cols_file1))
            use_cols2 = list(set(match_cols + amt_cols + extra_cols_file2))
 
            df1_sub = df1[use_cols1].copy()
            df2_sub = df2[use_cols2].copy()

            # Smart cumcount logic: For each project, create variance rows equal to the larger file's row count
            df1_sub['cumcount'] = df1_sub.groupby(match_cols).cumcount()
            df2_sub['cumcount'] = df2_sub.groupby(match_cols).cumcount()

            # Get row counts for each project in both files
            counts_df1 = df1_sub.groupby(match_cols).size().reset_index(name='count_file1')
            counts_df2 = df2_sub.groupby(match_cols).size().reset_index(name='count_file2')

            # Merge counts to determine strategy for each project
            project_counts = pd.merge(counts_df1, counts_df2, on=match_cols, how='outer')
            project_counts['count_file1'] = project_counts['count_file1'].fillna(0)
            project_counts['count_file2'] = project_counts['count_file2'].fillna(0)
            project_counts['max_count'] = project_counts[['count_file1', 'count_file2']].max(axis=1)

            # Create variance rows based on the larger file's count for each project
            variance_rows = []
            
            for _, project_row in project_counts.iterrows():
                project_filter = {col: project_row[col] for col in match_cols}
                count_file1 = int(project_row['count_file1'])
                count_file2 = int(project_row['count_file2'])
                max_count = int(project_row['max_count'])
                
                # Get data for this project from both files
                df1_project = df1_sub.copy()
                df2_project = df2_sub.copy()
                for col, val in project_filter.items():
                    df1_project = df1_project[df1_project[col] == val]
                    df2_project = df2_project[df2_project[col] == val]
                
                # Create exactly max_count variance rows for this project
                for i in range(max_count):
                    variance_row = {}
                    
                    # Add match columns
                    for col in match_cols:
                        variance_row[col] = project_filter[col]
                    
                    # Get File1 data for this row index
                    if i < count_file1:
                        df1_row = df1_project[df1_project['cumcount'] == i]
                        if not df1_row.empty:
                            df1_row = df1_row.iloc[0]
                            for col in amt_cols + extra_cols_file1:
                                if col in df1_row and col not in ['cumcount']:
                                    variance_row[f"{col}_File1"] = df1_row[col]
                    else:
                        # Fill with 0 for amount columns when file1 has fewer rows
                        for col in amt_cols:
                            variance_row[f"{col}_File1"] = 0
                        for col in extra_cols_file1:
                            if col not in match_cols:
                                variance_row[f"{col}_File1"] = None
                    
                    # Get File2 data for this row index
                    if i < count_file2:
                        df2_row = df2_project[df2_project['cumcount'] == i]
                        if not df2_row.empty:
                            df2_row = df2_row.iloc[0]
                            for col in amt_cols + extra_cols_file2:
                                if col in df2_row and col not in ['cumcount']:
                                    variance_row[f"{col}_File2"] = df2_row[col]
                    else:
                        # Fill with 0 for amount columns when file2 has fewer rows
                        for col in amt_cols:
                            variance_row[f"{col}_File2"] = 0
                        for col in extra_cols_file2:
                            if col not in match_cols:
                                variance_row[f"{col}_File2"] = None
                    
                    variance_rows.append(variance_row)
            
            # Convert to DataFrame and remove cumcount column if it exists
            merged = pd.DataFrame(variance_rows)
            if 'cumcount' in merged.columns:
                merged = merged.drop('cumcount', axis=1)
 
            for col in amt_cols:
                col1 = f"{col}_File1"
                col2 = f"{col}_File2"
                if col1 in merged.columns:
                    merged[col1] = merged[col1].fillna(0)
                if col2 in merged.columns:
                    merged[col2] = merged[col2].fillna(0)
                merged[f"Variance_{col}"] = merged[col2] - merged[col1]
 
            file1_amt = [f"{col}_File1" for col in amt_cols if f"{col}_File1" in merged.columns]
            file2_amt = [f"{col}_File2" for col in amt_cols if f"{col}_File2" in merged.columns]
            variance_cols = [f"Variance_{col}" for col in amt_cols if f"Variance_{col}" in merged.columns]
            extra_all = [col for col in merged.columns if col in extra_cols_file1 or col in extra_cols_file2]
 
            final_order = match_cols + file1_amt + file2_amt + extra_all + variance_cols
            remaining_cols = [col for col in merged.columns if col not in final_order]
            merged = merged[final_order + remaining_cols]
 
            st.success("✅ Variance calculated! Each row in File 1 matched to one in File 2.")
            st.write("### 📋 Variance Report")
            st.dataframe(merged)
 
            csv = merged.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV Report", data=csv, file_name='Variance_Report.csv', mime='text/csv')
 
            st.session_state.merged_df = merged
 
with tab2:
    st.header("📊 Data Visualization")
 
    if not all(k in st.session_state for k in ["df1", "df2", "merged_df"]):
        st.info("Please upload and compare files in Tab 1.")
    else:
        chart_source = st.selectbox("📌 Select Dataset", ["File 1", "File 2", "Variance Report"])
        df = {
            "File 1": st.session_state.df1,
            "File 2": st.session_state.df2,
            "Variance Report": st.session_state.merged_df
        }[chart_source]
 
        chart_type = st.selectbox("Chart Type", ["Bar Chart", "Line Chart", "Pie Chart"])
        x_col = st.selectbox("X-axis", get_categorical_columns(df) + list(df.columns))
        y_cols = st.multiselect("Y-axis", get_numeric_columns(df), max_selections=2)
 
        if x_col and y_cols:
            df_plot = df.copy()
            for col in y_cols:
                df_plot[col] = df_plot[col].apply(clean_amount)
            df_grouped = df_plot.groupby(x_col)[y_cols].sum().reset_index()
 
            if chart_type == "Bar Chart":
                fig = px.bar(df_grouped, x=x_col, y=y_cols, barmode='group', text_auto=True,
                             title=f"{chart_type}: {', '.join(y_cols)} vs {x_col}")
                fig.update_traces(textposition='outside')
            elif chart_type == "Line Chart":
                fig = px.line(df_grouped, x=x_col, y=y_cols, title=f"{chart_type}: {', '.join(y_cols)} vs {x_col}")
                for trace in fig.data:
                    trace.mode = 'lines+markers'
            elif chart_type == "Pie Chart" and len(y_cols) == 1:
                fig = px.pie(df_grouped, names=x_col, values=y_cols[0], title=f"{chart_type}: {y_cols[0]} by {x_col}")
            else:
                fig = None
                st.warning("Unsupported chart type or column combination.")
 
            if fig:
                fig.update_layout(height=500, xaxis_title=x_col, yaxis_title="Total", legend_title="Legend")
                st.plotly_chart(fig, use_container_width=True)
 
        # Side-by-side comparison section
        st.markdown("---")
        st.subheader("🆚 Side-by-Side Chart Comparison")
 
        col1, col2 = st.columns(2)
 
        with col1:
            st.markdown("#### 🔷 File 1 Chart")
            x1 = st.selectbox("X-axis (File 1)", get_categorical_columns(st.session_state.df1), key="x1")
            y1 = st.selectbox("Y-axis (File 1)", get_numeric_columns(st.session_state.df1), key="y1")
 
            if x1 and y1:
                df1_plot = st.session_state.df1.copy()
                df1_plot[y1] = df1_plot[y1].apply(clean_amount)
                df1_grouped = df1_plot.groupby(x1)[y1].sum().reset_index()
                fig1 = px.bar(df1_grouped, x=x1, y=y1, text=y1, title="File 1")
                fig1.update_traces(textposition='outside')
                fig1.update_layout(height=500, xaxis_title=x1, yaxis_title="Total", showlegend=False)
                st.plotly_chart(fig1, use_container_width=True)
 
        with col2:
            st.markdown("#### 🔶 File 2 Chart")
            x2 = st.selectbox("X-axis (File 2)", get_categorical_columns(st.session_state.df2), key="x2")
            y2 = st.selectbox("Y-axis (File 2)", get_numeric_columns(st.session_state.df2), key="y2")
 
            if x2 and y2:
                df2_plot = st.session_state.df2.copy()
                df2_plot[y2] = df2_plot[y2].apply(clean_amount)
                df2_grouped = df2_plot.groupby(x2)[y2].sum().reset_index()
                fig2 = px.bar(df2_grouped, x=x2, y=y2, text=y2, title="File 2") 
                fig2.update_traces(textposition='outside')
                fig2.update_layout(height=500, xaxis_title=x2, yaxis_title="Total", showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)