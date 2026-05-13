Place your backend knowledge files here before running the AI pipeline:

1. `symptoms_disease.csv`
   Required columns:
   - `text`
   - `disease`

2. `disease_info.csv`
   Required columns:
   - `disease`
   - `description`
   - `precautions`

3. PDF files
   Put them inside `app/data/pdfs/`

Suggested structure:

app/data/
├── symptoms_disease.csv
├── disease_info.csv
└── pdfs/
    ├── encyclopedia.pdf
    └── research_notes.pdf
