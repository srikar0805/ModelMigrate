# ModelMigrate

ModelMigrate helps migrate a Tabular model (`.bim`) to a Microsoft Fabric Semantic Model while preserving original business-facing names.

The core idea is:

1. Encrypt names (remove unsupported/special characters and spaces) so Fabric-side modeling and shortcuts are easier.
2. Keep a change log of all renamed fields.
3. Build/update the Fabric semantic model using the encrypted naming.
4. Decrypt names back to original display names and restore hierarchies.

This reduces manual rework when transitioning from Tabular models to Fabric semantic models.

## Repository Structure

- `Encrypt.py`: CLI script to rename table/column names and generate a CSV change log.
- `Decrypt.py`: CLI script to restore names from the log and copy hierarchies from the original model.
- `Relations.py`: Extracts relationship metadata to CSV.
- `FixRelations.py`: Propagates data types across relationship graph and outputs corrected CSV.
- `backend/`: FastAPI service exposing encrypt/decrypt endpoints.
- `frontend/`: React + Vite UI for uploading files and downloading outputs.

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm (for frontend)
- A source Tabular model file (for example `Original.bim`)
- Tabular Editor / Fabric workspace access
- Optional: ALM Toolkit for transferring measures/relationships

## Why Encryption Is Needed

Fabric shortcut/model naming constraints and source naming differences can cause friction when directly reusing Tabular model names.

ModelMigrate encryption removes characters using this pattern:

- `[ ().+{}]+`

In practice, this removes spaces and selected special characters from names used during migration.

## End-to-End Workflow

1. Back up your original model.
2. Run encryption to generate:
   - an encrypted model file (for Fabric-side work)
   - a changes log CSV (for restoration)
3. Create/prepare Fabric-side tables/shortcuts to align with encrypted names.
4. Build semantic model in Fabric from those tables.
5. Export/save that model as `.bim`.
6. Run decryption with:
   - migrated encrypted `.bim`
   - updated changes log
   - original `.bim` (for hierarchy copy)
7. Use ALM Toolkit to transfer measures and relationships if needed.
8. Validate in Tabular Editor and deploy as a new semantic model.
9. Refresh and test in Power BI.

## Option A: Use the Web App (Recommended)

### 1) Start Backend (FastAPI)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

API base URL: `http://localhost:8000`

### 2) Start Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on Vite default URL (usually `http://localhost:5173`).

### 3) Use UI Steps

1. Step 1: Upload original `.bim`, download:
   - `Encrypted.bim`
   - `changes_log.csv`
2. Step 2: Perform external migration tasks in Tabular/Fabric.
3. Step 3: Upload:
   - migrated encrypted model
   - log CSV
   - original model
   and download restored model.

## Option B: Use Python Scripts Directly

The root scripts currently use hard-coded file names. Update the file path constants inside each script before running.

### Encrypt

Edit in `Encrypt.py`:

- `file_path` (input/output BIM path)
- `csv_path` (changes CSV output)

Run:

```bash
python Encrypt.py
```

### Decrypt

Edit in `Decrypt.py`:

- `log_file_path`
- `bim_file_path`
- `output_bim_file_path`
- `source_bim_file_path`

Run:

```bash
python Decrypt.py
```

### Relationship Helpers

`Relations.py`

- Reads relationship info from a model file and writes `Tabular_Relationships.csv`.
- Note: `json_file_path` currently points to `Original.cim`; update to your `.bim` file as needed.

`FixRelations.py`

- Reads relationship CSV and normalizes data types across connected graph components.
- Writes corrected output (`CorrectedRelations.csv`).

Run:

```bash
python Relations.py
python FixRelations.py
```

## API Reference

### `GET /`

Health endpoint.

### `POST /api/encrypt`

Request (multipart):

- `file`: `.bim` file

Response JSON:

- `modified_bim`: encrypted model JSON
- `changes_log_csv`: CSV content as string

### `POST /api/decrypt`

Request (multipart):

- `encrypted_file`: migrated encrypted `.bim`
- `log_file`: CSV changes log
- `original_file`: original `.bim`

Response JSON:

- Restored model JSON

## Important Notes and Limitations

- Measures are intentionally skipped during encryption traversal.
- Decryption restores names and data types for columns found in the log.
- Hierarchies are copied from the original model into matching tables.
- Relationship/measures transfer is expected to be done separately (for example with ALM Toolkit).
- Duplicate source-column mappings can still cause conflicts and should be fixed upstream.
- Fabric may enforce stricter relationship datatype compatibility than Tabular.

## Common Troubleshooting

- `422/500` from API:
  - Ensure valid JSON `.bim` file content.
  - Ensure all required files are uploaded for decryption.
- CORS or frontend request issues:
  - Confirm backend is running on `localhost:8000`.
- Empty/incorrect restore:
  - Validate `Table Name`, `Before`, `After`, and `Data Type` columns in CSV.
  - Ensure the log corresponds to the exact encrypted model lineage.

## Development Notes

- Backend tests: `backend/test_services.py`
- Frontend scripts:
  - `npm run dev`
  - `npm run build`
  - `npm run lint`

## Future Improvements

- Convert root scripts to CLI arguments instead of hard-coded paths.
- Add validation for malformed logs before decryption.
- Add integration tests for API + frontend flow.
- Add deterministic conflict handling for duplicate renamed fields.