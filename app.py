import sys
import os
from io import BytesIO
import pandas as pd
import streamlit as st

# -----------------------------
# 🔍 DEPENDENCY VALIDATION
# -----------------------------
try:
    import openpyxl
    from openpyxl.utils.dataframe import dataframe_to_rows
except ImportError:
    st.error("""
    🚫 Required libraries missing! Please install using:
    ```
    pip install --upgrade openpyxl pandas streamlit
    pip install --force-reinstall jsonschema-specifications
    ```
    """)
    st.stop()

# -----------------------------
# 🌐 PAGE SETUP
# -----------------------------
st.set_page_config(page_title="📂 Smart Data Tool", layout="wide")
st.title("📂 Smart Data Tool")
st.caption("Upload CSV/Excel files, clean and visualize your data, then export in your preferred format.")

# -----------------------------
# 📤 FILE UPLOAD AREA
# -----------------------------
uploaded_files = st.file_uploader(
    "Choose your CSV or Excel files:",
    type=["csv", "xlsx"],
    accept_multiple_files=True
)

# -----------------------------
# 🔄 FILE LOOP
# -----------------------------
if uploaded_files:
    for data_file in uploaded_files:
        with st.expander(f"📁 File: {data_file.name}", expanded=True):
            try:
                extension = os.path.splitext(data_file.name)[-1].lower()
                df = pd.DataFrame()

                if extension == ".csv":
                    selected_encoding = st.selectbox(
                        f"Encoding for {data_file.name}",
                        ["utf-8", "cp1252", "latin1", "ISO-8859-1"],
                        key=f"enc_{data_file.name}"
                    )
                    df = pd.read_csv(data_file, encoding=selected_encoding)
                elif extension == ".xlsx":
                    df = pd.read_excel(data_file, engine='openpyxl')
                else:
                    st.error(f"Unsupported file type: {extension}")
                    continue

                # 📑 FILE SUMMARY
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("📘 Summary")
                    st.metric("File Size", f"{data_file.size/1024:.1f} KB")
                    st.text(f"Columns: {len(df.columns)}")
                    st.text(f"Rows: {len(df)}")

                with col2:
                    st.subheader("👀 Preview")
                    st.dataframe(df.head(5), use_container_width=True)

                # 🧼 DATA CLEANING OPTIONS
                st.subheader("🧼 Clean Your Data")
                if st.checkbox(f"Enable cleaning options", key=f"cleaning_{data_file.name}"):
                    c1, c2 = st.columns(2)

                    with c1:
                        if st.button("Remove Duplicate Rows", key=f"remove_dupes_{data_file.name}"):
                            original = len(df)
                            df = df.drop_duplicates()
                            removed = original - len(df)
                            st.success(f"{removed} duplicate rows removed.")

                    with c2:
                        if st.button("Fill Empty Values", key=f"fillna_{data_file.name}"):
                            numeric = df.select_dtypes(include='number').columns
                            df[numeric] = df[numeric].fillna(df[numeric].mean())
                            st.success("Missing numeric values filled with column mean.")

                # 📑 COLUMN FILTERING
                st.subheader("🧮 Select Columns to Keep")
                selected_columns = st.multiselect(
                    "Pick the columns you want to include:",
                    df.columns,
                    default=df.columns.tolist(),
                    key=f"cols_{data_file.name}"
                )
                df = df[selected_columns]

                # 📈 SIMPLE VISUALIZATION
                st.subheader("📈 Generate Visuals")
                if st.checkbox("Display Charts", key=f"chart_{data_file.name}"):
                    numeric_cols = df.select_dtypes(include='number').columns
                    if len(numeric_cols) >= 2:
                        st.line_chart(df[numeric_cols[:2]])
                        st.bar_chart(df[numeric_cols[:2]])
                    else:
                        st.warning("Add more numeric columns to enable charting.")

                # 🔁 EXPORT OPTIONS
                st.subheader("📥 Export Cleaned File")
                export_format = st.radio(
                    "Choose export format:",
                    ["CSV", "Excel"],
                    horizontal=True,
                    key=f"export_{data_file.name}"
                )

                if st.button("Export & Download", key=f"export_btn_{data_file.name}"):
                    try:
                        output = BytesIO()
                        if export_format == "CSV":
                            df.to_csv(output, index=False, encoding=selected_encoding if extension == ".csv" else "utf-8")
                            output_ext = ".csv"
                            mime_type = "text/csv"
                        else:
                            df.to_excel(output, index=False, engine='openpyxl')
                            output_ext = ".xlsx"
                            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                        output.seek(0)
                        st.download_button(
                            label="📥 Download File",
                            data=output,
                            file_name=data_file.name.replace(extension, output_ext),
                            mime=mime_type,
                            key=f"download_{data_file.name}"
                        )
                    except Exception as ex:
                        st.error(f"Something went wrong during export: {str(ex)}")

            except Exception as file_error:
                st.error(f"Could not process {data_file.name}: {str(file_error)}")

st.success("🎉 All files are done. Ready for download and submission!")
