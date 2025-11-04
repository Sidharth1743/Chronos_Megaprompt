"""
CHRONOS Web Application
Flask-based web interface for the CHRONOS pipeline
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "chronos" / "app"))

from ocr_engine import OCREngine
from phase1_brainstorm import Phase1Brainstorm
from phase2_context_builder import Phase2ContextBuilder
from phase3_distilling import Phase3Distiller
from phase4_formulating import Phase4Formulator

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg', 'tiff'}

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# Store processing status
processing_status = {}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def parse_phase4_results(phase4_file):
    """Parse Phase 4 research questions file - extracts ALL hypotheses with ALL fields"""
    if not os.path.exists(phase4_file):
        return []

    with open(phase4_file, 'r', encoding='utf-8') as f:
        content = f.read()

    hypotheses = []

    # Find all H# patterns and split content into sections
    h_pattern = r'\*\*(H\d+):'
    h_matches = list(re.finditer(h_pattern, content))

    for i, match in enumerate(h_matches):
        # Get content from current H to next H (or end of file)
        start = match.start()
        end = h_matches[i + 1].start() if i + 1 < len(h_matches) else len(content)
        section = content[start:end]

        # Extract H number and title
        h_title_match = re.search(r'\*\*(H\d+):\s+([^\*]+)\*\*', section)
        if not h_title_match:
            continue

        h_number = h_title_match.group(1)
        title = h_title_match.group(2).strip()

        # Extract claim statement
        claim_match = re.search(r'\*\*Claim Statement:\*\*\s+(.*?)(?=\n\*\*Historical Source:)', section, re.DOTALL)
        claim = claim_match.group(1).strip() if claim_match else ""

        # Extract historical source
        hist_match = re.search(r'\*\*Historical Source:\*\*\s+(.*?)(?=\n\*\*Modern Relevance:)', section, re.DOTALL)
        historical_source = hist_match.group(1).strip() if hist_match else ""

        # Extract modern relevance
        modern_match = re.search(r'\*\*Modern Relevance:\*\*\s+(.*?)(?=\n\*\*Variables:)', section, re.DOTALL)
        modern_relevance = modern_match.group(1).strip() if modern_match else ""

        # Extract variables
        variables_match = re.search(r'\*\*Variables:\*\*\s+(.*?)(?=\n\*\*Mechanism:)', section, re.DOTALL)
        variables = variables_match.group(1).strip() if variables_match else ""

        # Extract mechanism
        mech_match = re.search(r'\*\*Mechanism:\*\*\s+(.*?)(?=\n\*\*Testability Score:)', section, re.DOTALL)
        mechanism = mech_match.group(1).strip() if mech_match else ""

        # Extract testability score
        testability_match = re.search(r'\*\*Testability Score:\s*(\d+)/10\*\*', section)
        testability = int(testability_match.group(1)) if testability_match else 5

        # Extract innovation potential
        innov_match = re.search(r'\*\*Innovation Potential:\s*(High|Moderate|Low)\*\*', section)
        innovation = innov_match.group(1) if innov_match else "Moderate"

        hypotheses.append({
            'h_number': h_number,
            'title': title,
            'claim': claim,
            'historical_source': historical_source,
            'modern_relevance': modern_relevance,
            'variables': variables,
            'mechanism': mechanism,
            'testability': testability,
            'innovation': innovation
        })

    return hypotheses


def run_chronos_pipeline(file_path, filename):
    """Run the CHRONOS pipeline on uploaded file"""
    try:
        # Generate unique identifiers
        clean_filename = re.sub(r'[^a-zA-Z0-9]', '_', os.path.splitext(filename)[0])[:30]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = f"{clean_filename}_{timestamp}"

        # Update status
        processing_status[unique_id] = {
            'status': 'processing',
            'phase': 'ocr',
            'progress': 10,
            'filename': filename
        }

        # Neo4j configuration
        NEO4J_URL = os.environ.get("NEO4J_URL", "neo4j://127.0.0.1:7687")
        NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
        NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "0123456789")
        UNIQUE_DB_NAME = f"chronos_{unique_id}".lower()

        # OCR configuration
        OCR_CONFIG = {
            'use_preprocessing': True,
            'enhancement_level': 'aggressive',
            'high_dpi': True,
            'medical_context': True,
            'save_debug_images': False,
            'try_native_text': True
        }

        # Create results directory
        result_dir = os.path.join(app.config['RESULTS_FOLDER'], unique_id)
        os.makedirs(result_dir, exist_ok=True)
        os.makedirs(os.path.join(result_dir, 'phase1'), exist_ok=True)
        os.makedirs(os.path.join(result_dir, 'phase2'), exist_ok=True)
        os.makedirs(os.path.join(result_dir, 'phase3'), exist_ok=True)
        os.makedirs(os.path.join(result_dir, 'phase4'), exist_ok=True)

        # Step 1: OCR
        processing_status[unique_id]['phase'] = 'ocr'
        processing_status[unique_id]['progress'] = 15

        ocr_engine = OCREngine(use_advanced_model=True)
        extracted_text = ocr_engine.process_file(file_path, **OCR_CONFIG)

        # Save extracted text
        text_file = os.path.join(result_dir, 'extracted_text.txt')
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(extracted_text)

        # Step 2: Phase 1 - Brainstorm
        processing_status[unique_id]['phase'] = 'phase1'
        processing_status[unique_id]['progress'] = 30

        phase1 = Phase1Brainstorm()
        phase1_result = phase1.generate_and_save(
            ocr_text=extracted_text,
            output_dir=os.path.join(result_dir, 'phase1')
        )
        phase1_brainstorm = phase1_result["brainstorm"]

        # Step 3: Phase 2 - Context Building
        processing_status[unique_id]['phase'] = 'phase2'
        processing_status[unique_id]['progress'] = 50

        phase2_builder = Phase2ContextBuilder(
            neo4j_url=NEO4J_URL,
            neo4j_username=NEO4J_USERNAME,
            neo4j_password=NEO4J_PASSWORD,
            neo4j_database=UNIQUE_DB_NAME
        )

        phase2_results = phase2_builder.run_phase2(
            phase1_brainstorm=phase1_brainstorm,
            ocr_text=extracted_text,
            output_dir=os.path.join(result_dir, 'phase2')
        )
        phase2_builder.close()

        # Step 4: Phase 3 - Distilling
        processing_status[unique_id]['phase'] = 'phase3'
        processing_status[unique_id]['progress'] = 70

        phase3_distiller = Phase3Distiller()
        phase3_results = phase3_distiller.run_phase3(
            phase2_summary=phase2_results['summary'],
            output_dir=os.path.join(result_dir, 'phase3')
        )

        # Step 5: Phase 4 - Formulating
        processing_status[unique_id]['phase'] = 'phase4'
        processing_status[unique_id]['progress'] = 85

        phase4_formulator = Phase4Formulator()
        phase4_results = phase4_formulator.run_phase4(
            phase3_synthesis=phase3_results['synthesis']['synthesis'],
            num_questions=10,
            top_n=3,
            output_dir=os.path.join(result_dir, 'phase4'),
            use_h_format=True
        )

        # Parse results
        phase4_file = phase4_results['questions']['output_file']
        print(f"[DEBUG] Parsing Phase 4 file: {phase4_file}")

        hypotheses = parse_phase4_results(phase4_file)
        print(f"[DEBUG] Parsed {len(hypotheses)} hypotheses")

        if hypotheses:
            print(f"[DEBUG] Sample hypothesis: {hypotheses[0]['h_number']} - {hypotheses[0]['title']}")
        else:
            print("[WARNING] No hypotheses were parsed!")

        # Update status
        processing_status[unique_id] = {
            'status': 'complete',
            'phase': 'complete',
            'progress': 100,
            'filename': filename,
            'unique_id': unique_id,
            'database': UNIQUE_DB_NAME,
            'pages_analyzed': 'N/A',
            'hypotheses_count': len(hypotheses),
            'hypotheses': hypotheses,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'phase4_file': phase4_file  # For debugging
        }

        return unique_id, None

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] Pipeline failed: {e}")
        print(error_trace)

        processing_status[unique_id] = {
            'status': 'error',
            'error': str(e),
            'traceback': error_trace
        }
        return unique_id, str(e)


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: PDF, PNG, JPG, JPEG, TIFF'}), 400

    # Save file
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    saved_filename = f"{timestamp}_{filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
    file.save(file_path)

    # Start processing in background (for production, use Celery or similar)
    unique_id, error = run_chronos_pipeline(file_path, filename)

    if error:
        return jsonify({'error': error}), 500

    return jsonify({
        'success': True,
        'unique_id': unique_id,
        'message': 'Processing started'
    })


@app.route('/status/<unique_id>')
def get_status(unique_id):
    """Get processing status"""
    if unique_id not in processing_status:
        return jsonify({'error': 'Invalid ID'}), 404

    return jsonify(processing_status[unique_id])


@app.route('/results/<unique_id>')
def get_results(unique_id):
    """Get analysis results"""
    if unique_id not in processing_status:
        return jsonify({'error': 'Invalid ID'}), 404

    status = processing_status[unique_id]

    if status['status'] != 'complete':
        return jsonify({'error': 'Analysis not complete'}), 400

    return jsonify(status)


@app.route('/test-parse')
def test_parse():
    """Test parsing with existing results"""
    test_file = "/home/sidharth/Desktop/chronos/chronos_results/phase4/research_questions_20251104_153442.txt"

    if not os.path.exists(test_file):
        return jsonify({'error': 'Test file not found'}), 404

    hypotheses = parse_phase4_results(test_file)

    return jsonify({
        'success': True,
        'count': len(hypotheses),
        'hypotheses': hypotheses
    })


if __name__ == '__main__':
    # Create directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

    # Run app
    app.run(debug=True, host='0.0.0.0', port=5000)
