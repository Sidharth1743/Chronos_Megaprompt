"""
CHRONOS Web Application
Flask-based web interface for the CHRONOS pipeline
"""

import os
import sys
import json
import re
import threading
from datetime import datetime
from pathlib import Path
from functools import wraps
from flask import Flask, render_template, request, jsonify, send_from_directory, g
from werkzeug.utils import secure_filename
from sqlalchemy import func

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "chronos" / "app"))

# Import database models
from models import db, User, Rating, Comment, Endorsement, init_db

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

# Database configuration
# Use PostgreSQL in production (Render provides DATABASE_URL), SQLite for local dev
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Render provides postgres:// but SQLAlchemy needs postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Local development: use SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chronos_community.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chronos-secret-key-change-in-production')

# Initialize database
init_db(app)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# Store processing status
processing_status = {}

# Analysis history file
HISTORY_FILE = 'results/analysis_history.json'


def load_analysis_history():
    """Load analysis history from JSON file"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_analysis_to_history(analysis_data):
    """Save completed analysis to history"""
    history = load_analysis_history()

    # Add to beginning of list (most recent first)
    history.insert(0, {
        'filename': analysis_data['filename'],
        'unique_id': analysis_data['unique_id'],
        'timestamp': analysis_data['timestamp'],
        'hypotheses_count': analysis_data['hypotheses_count'],
        'date_readable': datetime.strptime(analysis_data['timestamp'], '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y')
    })

    # Keep only last 10 analyses
    history = history[:10]

    # Save to file
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)

    return history


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# ============================================================================
# AUTHENTICATION MIDDLEWARE
# ============================================================================

def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401

        token = auth_header.split(' ')[1]
        user_id = User.verify_auth_token(token, app.config['SECRET_KEY'])

        if user_id is None:
            return jsonify({'error': 'Invalid or expired token'}), 401

        g.current_user = User.query.get(user_id)
        if g.current_user is None:
            return jsonify({'error': 'User not found'}), 401

        return f(*args, **kwargs)
    return decorated_function


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


def run_chronos_pipeline(file_path, filename, unique_id):
    """Run the CHRONOS pipeline on uploaded file"""
    try:
        print(f"\n[PIPELINE] Starting pipeline for {unique_id}")

        # Update status - Initializing
        processing_status[unique_id].update({
            'phase': 'initializing',
            'phase_display': 'Initializing pipeline...',
            'progress': 5
        })
        print(f"[PIPELINE] Status: Initializing")

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
        processing_status[unique_id].update({
            'phase': 'ocr',
            'phase_display': 'OCR started - Extracting text from document...',
            'progress': 15
        })
        print(f"[PIPELINE] Status: OCR started")

        ocr_engine = OCREngine(use_advanced_model=True)
        extracted_text = ocr_engine.process_file(file_path, **OCR_CONFIG)

        processing_status[unique_id].update({
            'phase_display': 'OCR completed - Text extracted successfully',
            'progress': 25
        })
        print(f"[PIPELINE] Status: OCR completed")

        # Save extracted text
        text_file = os.path.join(result_dir, 'extracted_text.txt')
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(extracted_text)

        # Step 2: Phase 1 - Brainstorm
        processing_status[unique_id].update({
            'phase': 'phase1',
            'phase_display': 'Phase 1: Brainstorming - Generating initial ideas...',
            'progress': 30
        })
        print(f"[PIPELINE] Status: Phase 1 started")

        phase1 = Phase1Brainstorm()
        phase1_result = phase1.generate_and_save(
            ocr_text=extracted_text,
            output_dir=os.path.join(result_dir, 'phase1')
        )
        phase1_brainstorm = phase1_result["brainstorm"]

        processing_status[unique_id].update({
            'phase_display': 'Phase 1 completed - Ideas generated',
            'progress': 45
        })
        print(f"[PIPELINE] Status: Phase 1 completed")

        # Step 3: Phase 2 - Context Building
        processing_status[unique_id].update({
            'phase': 'phase2',
            'phase_display': 'Phase 2: Context Building - Building knowledge graphs...',
            'progress': 50
        })
        print(f"[PIPELINE] Status: Phase 2 started")

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

        processing_status[unique_id].update({
            'phase_display': 'Phase 2 completed - Knowledge graphs built',
            'progress': 65
        })
        print(f"[PIPELINE] Status: Phase 2 completed")

        # Step 4: Phase 3 - Distilling (3 stages)
        processing_status[unique_id].update({
            'phase': 'phase3',
            'phase_display': 'Phase 3: Distilling - Stage 1/3: Modern Research Extensions...',
            'progress': 70
        })
        print(f"[PIPELINE] Status: Phase 3 - Lens A started")

        phase3_distiller = Phase3Distiller()

        # Stage 1: Lens A - Modern Research Extensions
        phase3_results = {
            "phase": "Phase 3",
            "lens_a": None,
            "lens_b": None,
            "lens_c": None,
            "synthesis": None
        }

        try:
            phase3_results["lens_a"] = phase3_distiller.generate_lens_a_alternatives(
                phase2_summary=phase2_results['summary'],
                output_dir=os.path.join(result_dir, 'phase3')
            )
        except Exception as e:
            print(f"   ⚠️  LENS A failed: {e}")

        # Stage 2: Lens B - Historical Observation Extensions
        processing_status[unique_id].update({
            'phase_display': 'Phase 3: Distilling - Stage 2/3: Historical Observation Extensions...',
            'progress': 73
        })
        print(f"[PIPELINE] Status: Phase 3 - Lens B started")

        try:
            phase3_results["lens_b"] = phase3_distiller.generate_lens_b_alternatives(
                phase2_summary=phase2_results['summary'],
                output_dir=os.path.join(result_dir, 'phase3')
            )
        except Exception as e:
            print(f"   ⚠️  LENS B failed: {e}")

        # Stage 3: Lens C - Bridge Questions
        processing_status[unique_id].update({
            'phase_display': 'Phase 3: Distilling - Stage 3/3: Bridge Questions...',
            'progress': 76
        })
        print(f"[PIPELINE] Status: Phase 3 - Lens C started")

        try:
            phase3_results["lens_c"] = phase3_distiller.generate_lens_c_alternatives(
                phase2_summary=phase2_results['summary'],
                output_dir=os.path.join(result_dir, 'phase3')
            )
        except Exception as e:
            print(f"   ⚠️  LENS C failed: {e}")

        # Synthesize all lenses
        processing_status[unique_id].update({
            'phase_display': 'Phase 3: Synthesizing all three lenses...',
            'progress': 79
        })
        print(f"[PIPELINE] Status: Phase 3 - Synthesizing")

        # Only synthesize if all three lenses completed successfully
        if phase3_results["lens_a"] and phase3_results["lens_b"] and phase3_results["lens_c"]:
            try:
                phase3_results["synthesis"] = phase3_distiller.generate_synthesis(
                    lens_a_result=phase3_results["lens_a"],
                    lens_b_result=phase3_results["lens_b"],
                    lens_c_result=phase3_results["lens_c"],
                    output_dir=os.path.join(result_dir, 'phase3')
                )
            except Exception as e:
                print(f"   ⚠️  Synthesis failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("   ⚠️  Skipping synthesis (not all lenses completed)")

        processing_status[unique_id].update({
            'phase_display': 'Phase 3 completed - All lenses synthesized',
            'progress': 80
        })
        print(f"[PIPELINE] Status: Phase 3 completed")

        # Step 5: Phase 4 - Formulating
        processing_status[unique_id].update({
            'phase': 'phase4',
            'phase_display': 'Phase 4: Formulating - Creating hypotheses...',
            'progress': 85
        })
        print(f"[PIPELINE] Status: Phase 4 started")

        # Check if synthesis exists
        if not phase3_results.get('synthesis') or not phase3_results['synthesis'].get('synthesis'):
            raise ValueError("Phase 3 synthesis failed - cannot proceed to Phase 4")

        phase4_formulator = Phase4Formulator()
        phase4_results = phase4_formulator.run_phase4(
            phase3_synthesis=phase3_results['synthesis']['synthesis'],
            num_questions=10,
            output_dir=os.path.join(result_dir, 'phase4'),
            use_h_format=True
        )

        # Aggregating results
        processing_status[unique_id].update({
            'phase_display': 'Aggregating results...',
            'progress': 92
        })
        print(f"[PIPELINE] Status: Aggregating results")

        # Parse results
        phase4_file = phase4_results['questions']['output_file']
        print(f"[PIPELINE] Parsing Phase 4 file: {phase4_file}")

        processing_status[unique_id].update({
            'phase_display': 'Generating hypotheses...',
            'progress': 96
        })
        print(f"[PIPELINE] Status: Generating hypotheses")

        hypotheses = parse_phase4_results(phase4_file)
        print(f"[DEBUG] Parsed {len(hypotheses)} hypotheses")

        if hypotheses:
            print(f"[DEBUG] Sample hypothesis: {hypotheses[0]['h_number']} - {hypotheses[0]['title']}")
        else:
            print("[WARNING] No hypotheses were parsed!")

        # Update status
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        processing_status[unique_id] = {
            'status': 'complete',
            'phase': 'complete',
            'phase_display': 'Analysis Complete!',
            'progress': 100,
            'filename': filename,
            'unique_id': unique_id,
            'database': UNIQUE_DB_NAME,
            'pages_analyzed': 'N/A',
            'hypotheses_count': len(hypotheses),
            'hypotheses': hypotheses,
            'timestamp': current_timestamp,
            'phase4_file': phase4_file  # For debugging
        }

        # Save to history
        save_analysis_to_history(processing_status[unique_id])
        print(f"[PIPELINE] Pipeline complete for {unique_id}")

        return

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] Pipeline failed for {unique_id}: {e}")
        print(error_trace)

        processing_status[unique_id] = {
            'status': 'error',
            'error': str(e),
            'traceback': error_trace
        }
        return


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()

    # Validate required fields
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        full_name=data.get('full_name', ''),
        institution=data.get('institution', ''),
        expertise=data.get('expertise', ''),
        bio=data.get('bio', '')
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    # Generate token
    token = user.generate_auth_token(app.config['SECRET_KEY'])

    return jsonify({
        'success': True,
        'message': 'User registered successfully',
        'token': token,
        'user': user.to_dict(include_stats=True)
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()

    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400

    # Find user
    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Generate token
    token = user.generate_auth_token(app.config['SECRET_KEY'])

    return jsonify({
        'success': True,
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict(include_stats=True)
    })


@app.route('/api/auth/me')
@login_required
def get_current_user():
    """Get current user profile with engagement stats"""
    return jsonify({
        'success': True,
        'user': g.current_user.to_dict(include_stats=True)
    })


@app.route('/api/community/members')
def get_community_members():
    """Get all community members with their engagement stats"""
    users = User.query.order_by(User.created_at.desc()).all()

    members_data = []
    for user in users:
        member_info = {
            'username': user.username,
            'full_name': user.full_name,
            'institution': user.institution,
            'engagement': user.get_engagement_stats()
        }
        members_data.append(member_info)

    # Sort by total engagement (ratings + comments + endorsements)
    members_data.sort(
        key=lambda x: (
            x['engagement']['total_ratings'] +
            x['engagement']['total_comments'] +
            x['engagement']['total_endorsements']
        ),
        reverse=True
    )

    return jsonify({
        'success': True,
        'members': members_data,
        'total_count': len(members_data)
    })


# ============================================================================
# VOTING/RATING ROUTES
# ============================================================================

@app.route('/api/hypotheses/<unique_id>/<hypothesis_id>/rate', methods=['POST'])
@login_required
def rate_hypothesis(unique_id, hypothesis_id):
    """Rate a hypothesis (1-5 stars)"""
    data = request.get_json()
    rating_value = data.get('rating')

    if not rating_value or not (1 <= rating_value <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    # Check if user already rated this hypothesis
    existing_rating = Rating.query.filter_by(
        user_id=g.current_user.id,
        hypothesis_id=hypothesis_id,
        unique_id=unique_id
    ).first()

    if existing_rating:
        # Update existing rating
        existing_rating.rating = rating_value
        existing_rating.updated_at = datetime.utcnow()
    else:
        # Create new rating
        rating = Rating(
            user_id=g.current_user.id,
            hypothesis_id=hypothesis_id,
            unique_id=unique_id,
            rating=rating_value
        )
        db.session.add(rating)

    db.session.commit()

    # Get updated rating stats
    avg_rating = db.session.query(func.avg(Rating.rating)).filter_by(
        hypothesis_id=hypothesis_id,
        unique_id=unique_id
    ).scalar() or 0

    rating_count = Rating.query.filter_by(
        hypothesis_id=hypothesis_id,
        unique_id=unique_id
    ).count()

    return jsonify({
        'success': True,
        'message': 'Rating submitted successfully',
        'avg_rating': round(float(avg_rating), 2),
        'rating_count': rating_count,
        'your_rating': rating_value
    })


@app.route('/api/hypotheses/<unique_id>/<hypothesis_id>/ratings')
def get_hypothesis_ratings(unique_id, hypothesis_id):
    """Get ratings for a hypothesis"""
    avg_rating = db.session.query(func.avg(Rating.rating)).filter_by(
        hypothesis_id=hypothesis_id,
        unique_id=unique_id
    ).scalar() or 0

    rating_count = Rating.query.filter_by(
        hypothesis_id=hypothesis_id,
        unique_id=unique_id
    ).count()

    # Get rating distribution
    ratings_dist = {}
    for i in range(1, 6):
        count = Rating.query.filter_by(
            hypothesis_id=hypothesis_id,
            unique_id=unique_id,
            rating=i
        ).count()
        ratings_dist[str(i)] = count

    return jsonify({
        'success': True,
        'avg_rating': round(float(avg_rating), 2),
        'rating_count': rating_count,
        'distribution': ratings_dist
    })


# ============================================================================
# COMMENT ROUTES
# ============================================================================

@app.route('/api/hypotheses/<unique_id>/<hypothesis_id>/comments', methods=['GET'])
def get_hypothesis_comments(unique_id, hypothesis_id):
    """Get all comments for a hypothesis"""
    comments = Comment.query.filter_by(
        hypothesis_id=hypothesis_id,
        unique_id=unique_id
    ).order_by(Comment.created_at.desc()).all()

    return jsonify({
        'success': True,
        'comments': [comment.to_dict() for comment in comments],
        'count': len(comments)
    })


@app.route('/api/hypotheses/<unique_id>/<hypothesis_id>/comments', methods=['POST'])
@login_required
def add_comment(unique_id, hypothesis_id):
    """Add a comment to a hypothesis"""
    data = request.get_json()
    comment_text = data.get('comment_text', '').strip()

    if not comment_text:
        return jsonify({'error': 'Comment text is required'}), 400

    if len(comment_text) > 5000:
        return jsonify({'error': 'Comment too long (max 5000 characters)'}), 400

    comment = Comment(
        user_id=g.current_user.id,
        hypothesis_id=hypothesis_id,
        unique_id=unique_id,
        comment_text=comment_text
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Comment added successfully',
        'comment': comment.to_dict()
    }), 201


@app.route('/api/hypotheses/<unique_id>/<hypothesis_id>/endorse', methods=['POST'])
@login_required
def endorse_hypothesis(unique_id, hypothesis_id):
    """Endorse a hypothesis"""
    data = request.get_json()
    endorsement_text = data.get('endorsement_text', '').strip()

    # Check if already endorsed
    existing = Endorsement.query.filter_by(
        user_id=g.current_user.id,
        hypothesis_id=hypothesis_id,
        unique_id=unique_id
    ).first()

    if existing:
        return jsonify({'error': 'You have already endorsed this hypothesis'}), 400

    endorsement = Endorsement(
        user_id=g.current_user.id,
        hypothesis_id=hypothesis_id,
        unique_id=unique_id,
        endorsement_text=endorsement_text
    )

    db.session.add(endorsement)
    db.session.commit()

    # Get updated endorsement count
    endorsement_count = Endorsement.query.filter_by(
        hypothesis_id=hypothesis_id,
        unique_id=unique_id
    ).count()

    return jsonify({
        'success': True,
        'message': 'Hypothesis endorsed successfully',
        'endorsement_count': endorsement_count
    })


@app.route('/api/hypotheses/<unique_id>/<hypothesis_id>/endorsements')
def get_hypothesis_endorsements(unique_id, hypothesis_id):
    """Get endorsements for a hypothesis"""
    endorsements = Endorsement.query.filter_by(
        hypothesis_id=hypothesis_id,
        unique_id=unique_id
    ).all()

    return jsonify({
        'success': True,
        'endorsements': [e.to_dict() for e in endorsements],
        'count': len(endorsements)
    })


# ============================================================================
# MAIN PAGE ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/recent-analyses')
def get_recent_analyses():
    """Get recent analyses history"""
    history = load_analysis_history()
    return jsonify(history)


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

    # Generate unique ID
    clean_filename = re.sub(r'[^a-zA-Z0-9]', '_', os.path.splitext(filename)[0])[:30]
    unique_id = f"{clean_filename}_{timestamp}"

    # Initialize status
    processing_status[unique_id] = {
        'status': 'processing',
        'phase': 'initializing',
        'phase_display': 'Initializing pipeline...',
        'progress': 5,
        'filename': filename
    }

    # Start processing in background thread
    thread = threading.Thread(target=run_chronos_pipeline, args=(file_path, filename, unique_id))
    thread.daemon = True
    thread.start()

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
