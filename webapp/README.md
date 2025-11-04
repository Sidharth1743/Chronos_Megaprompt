# CHRONOS Web Application

A Flask-based web interface for the CHRONOS pipeline that extracts testable hypotheses from historical medical documents.

## Features

- 📄 **File Upload**: Drag & drop or browse to upload PDF, PNG, JPG, JPEG, or TIFF files
- ⏳ **Real-time Progress**: Live updates during the 4-phase CHRONOS analysis
- 🔬 **Hypothesis Display**: Beautiful cards showing each hypothesis with:
  - Testability scores (priority metric)
  - Historical sources
  - Proposed mechanisms
  - Innovation potential
- 🗄️ **Isolated Databases**: Each upload gets its own Neo4j database
- 📊 **Detailed Results**: View all generated hypotheses ranked by testability

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have the CHRONOS pipeline dependencies installed (see parent directory)

3. Ensure Neo4j is running:
```bash
neo4j start
```

4. Set up environment variables in `../.env`:
```
GOOGLE_API_KEY=your_google_api_key
NEO4J_URL=neo4j://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

## Usage

### Quick Test (with existing results)

First, test the parsing with existing results:

```bash
cd /home/sidharth/Desktop/chronos/webapp
python3 test_parsing.py
```

You should see all 10 hypotheses parsed correctly!

### Running the Web App

1. Start the Flask server:
```bash
cd /home/sidharth/Desktop/chronos/webapp
python3 app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. **Test the parser endpoint** (optional):
   - Visit: `http://localhost:5000/test-parse`
   - This will show you the parsed hypotheses from existing results in JSON format

4. Upload a medical document (PDF or image)

5. Wait for the analysis to complete (progress shown in real-time)

6. View the generated hypotheses with testability scores!

### Debugging

If hypotheses don't show up:

1. Check the Flask console for `[DEBUG]` messages
2. Check browser console (F12) for JavaScript errors
3. Visit `/test-parse` endpoint to verify parsing works
4. Check the Phase 4 output file location in the debug logs

## How It Works

The web app runs the complete CHRONOS 4-phase pipeline:

1. **Phase 1**: Self-critical brainstorming from OCR text
2. **Phase 2**: Building HeritageNet + SpineNet knowledge graphs in Neo4j
3. **Phase 3**: Generating alternatives through 3 analytical lenses
4. **Phase 4**: Formulating H-format testable hypotheses with ranking

Each hypothesis is displayed with:
- **Testability Score** (shown as "Priority" like in the template)
- Historical source
- Proposed mechanism
- Innovation potential (High/Moderate/Low)

## File Structure

```
webapp/
├── app.py                 # Flask application
├── templates/
│   └── index.html        # Main web interface
├── uploads/              # Uploaded files
├── results/              # Analysis results
│   └── <unique_id>/
│       ├── phase1/
│       ├── phase2/
│       ├── phase3/
│       └── phase4/
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Production Deployment

For production use, consider:

1. Using **Celery** or **RQ** for background task processing
2. Implementing **Redis** for session management
3. Adding **authentication** and user accounts
4. Setting up **nginx** as a reverse proxy
5. Using **gunicorn** or **uWSGI** instead of Flask's dev server

## Notes

- Maximum file size: 50MB
- Supported formats: PDF, PNG, JPG, JPEG, TIFF
- Each analysis creates a unique Neo4j database for isolation
- Processing time varies based on document size (typically 5-15 minutes)

## Troubleshooting

**Error: "GOOGLE_API_KEY not found"**
- Make sure you have set up the `.env` file with your Google API key

**Error: "Neo4j connection failed"**
- Ensure Neo4j is running: `neo4j status`
- Check your credentials in the `.env` file

**Upload fails**
- Check file size (max 50MB)
- Verify file format is supported
- Check server logs for detailed error messages
