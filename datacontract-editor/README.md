# Data Contract Editor — Databricks App

Visual editor for **Open Data Contract Standard (ODCS)** contracts, built with Python + Streamlit and ready to deploy on **Databricks Apps**.

## Features

- 🧱 **Schema Builder** — Visual form-based editor: add tables, fields, types, constraints (required, unique, PII), enums and examples. Syncs to YAML in real-time.
- 📝 **YAML Editor** — Full raw YAML editing with syntax hints and one-click validation + sync back to Builder.
- 👁 **Preview & Validate** — Rendered HTML view of the contract + ODCS validation with errors/warnings/info.
- 💾 **Persistence** — Save/load contracts as YAML files in a Databricks Volume (or local filesystem for dev).
- ⬇ **Download / Upload** — Export YAML or import existing contracts via file upload.

## Project Structure

```
datacontract-editor/
├── app.py                  # Streamlit entry point
├── app.yaml                # Databricks Apps config
├── requirements.txt
├── .streamlit/config.toml  # Theme config
├── assets/style.css        # Custom dark industrial theme
├── components/
│   ├── sidebar.py          # File management sidebar
│   ├── schema_builder.py   # Visual schema editor
│   ├── editor.py           # YAML text editor
│   └── preview.py          # Rendered preview + validation
└── utils/
    ├── state.py            # Session state helpers
    ├── builder.py          # Builder → YAML
    ├── parser.py           # YAML → Builder
    ├── validator.py        # ODCS validation engine
    ├── storage.py          # Volume persistence
    └── templates.py        # Default contract + field types
```

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploying to Databricks Apps

1. **Upload project** to a Databricks Repo or Workspace folder.
2. **Edit `app.yaml`** — set `CONTRACTS_VOLUME_PATH` to your Volume path.
3. **Deploy via CLI:**
   ```bash
   databricks apps deploy datacontract-editor \
     --source-code-path /Workspace/Users/you/datacontract-editor
   ```
4. **Start the app:**
   ```bash
   databricks apps start datacontract-editor
   ```
5. Open the app URL from the Databricks Apps UI.

## Volume Setup

Create the Volume in Unity Catalog before deploying:
```sql
CREATE VOLUME main.default.data_contracts;
```
