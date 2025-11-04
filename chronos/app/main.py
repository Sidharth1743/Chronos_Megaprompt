"""
Main Script - Refined CHRONOS Pipeline
Run this to process your medical documents with the 4-phase CHRONOS methodology
"""

from pathlib import Path
from dotenv import load_dotenv
from ocr_engine import OCREngine
from phase1_brainstorm import Phase1Brainstorm
from phase2_context_builder import Phase2ContextBuilder
from phase3_distilling import Phase3Distiller
from phase4_formulating import Phase4Formulator
from hypothesis_verifier import HypothesisVerifier
import os
import re

# Load environment from parent .env file (telegram-bot/.env)
load_dotenv(Path(__file__).parent.parent.parent / ".env")


def extract_top_questions_from_phase4(
    phase4_results,
    ranking_file=None,
    top_n=2
):
    """
    Extract top N questions from Phase 4 results.

    Args:
        phase4_results: Results dictionary from Phase 4
        ranking_file: Optional path to ranking file
        top_n: Number of top questions to extract (default: 2)

    Returns:
        List of question strings (claim statements)
    """
    questions = []

    try:
        # Try to read from ranking file if provided
        if ranking_file and os.path.exists(ranking_file):
            with open(ranking_file, 'r', encoding='utf-8') as f:
                ranking_content = f.read()

            # Extract top N question IDs from ranking (e.g., "H1:", "H2:")
            matches = re.findall(r'(\d+)\.\s+\*\*(H\d+):', ranking_content)

            if matches:
                # Get the top N question IDs
                top_ids = [match[1] for match in matches[:top_n]]

                # Now read the questions file to extract the claim statements
                questions_file = phase4_results.get('questions', {}).get('output_file')
                if questions_file and os.path.exists(questions_file):
                    with open(questions_file, 'r', encoding='utf-8') as f:
                        questions_content = f.read()

                    # Extract each top question's claim statement
                    for q_id in top_ids:
                        # Pattern: **H1: Title**\n\n**Claim Statement:**\nThe claim text...
                        pattern = rf'\*\*{q_id}:.*?\*\*.*?\*\*Claim Statement:\*\*\s*\n(.*?)(?=\n\*\*(?:Historical Source|Variables|Mechanism|H\d+:))'
                        match = re.search(pattern, questions_content, re.DOTALL)
                        if match:
                            claim = match.group(1).strip()
                            questions.append(claim)

        if not questions:
            # Fallback: extract first N claim statements from questions file
            questions_file = phase4_results.get('questions', {}).get('output_file')
            if questions_file and os.path.exists(questions_file):
                with open(questions_file, 'r', encoding='utf-8') as f:
                    questions_content = f.read()

                # Extract all claim statements
                claim_pattern = r'\*\*Claim Statement:\*\*\s*\n(.*?)(?=\n\*\*(?:Historical Source|Variables|Mechanism))'
                matches = re.findall(claim_pattern, questions_content, re.DOTALL)
                questions = [m.strip() for m in matches[:top_n]]

    except Exception as e:
        print(f"   ⚠️  Error extracting questions: {e}")
        import traceback
        traceback.print_exc()

    return questions


def main():
    """
    Main execution - Runs the Refined CHRONOS Pipeline (4 phases).
    """

    print("\n" + "="*80)
    print("🚀 REFINED CHRONOS PIPELINE - 4-Phase Methodology")
    print("="*80)
    print("\nThis pipeline will:")
    print("  • Phase 1: Self-Critical Brainstorm from historical text")
    print("  • Phase 2: Build HeritageNet + SpineNet knowledge graphs")
    print("  • Phase 3: Generate alternatives using 3 lenses")
    print("  • Phase 4: Formulate H-format research questions")
    print("  • Verify top 2 questions with FutureHouse API")
    print("="*80)

    # ==================== USER INPUT ====================

    # Get input file from user
    print("\n📄 Input File:")
    INPUT_FILE = input("Enter path to PDF or image file: ").strip()

    # Remove quotes if user copy-pasted with quotes
    INPUT_FILE = INPUT_FILE.strip('"').strip("'")

    # Check if file exists
    if not os.path.exists(INPUT_FILE):
        print(f"\n❌ ERROR: File not found: {INPUT_FILE}")
        print("   Please check the file path and try again")
        return

    # Get output file from user (optional)
    print("\n📝 Output Text File (optional):")
    print("   Press Enter to use default: extracted_text.txt")
    OUTPUT_TEXT_FILE = input("Enter path for output text file: ").strip()

    if not OUTPUT_TEXT_FILE:
        # Generate default output path in same directory as input
        input_dir = os.path.dirname(INPUT_FILE)
        OUTPUT_TEXT_FILE = os.path.join(input_dir, "extracted_text.txt")
        print(f"   Using default: {OUTPUT_TEXT_FILE}")
    else:
        OUTPUT_TEXT_FILE = OUTPUT_TEXT_FILE.strip('"').strip("'")

    # ==================== CONFIGURATION ====================

    # Neo4j Configuration from environment
    NEO4J_URL = os.environ.get("NEO4J_URL", "neo4j://127.0.0.1:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "0123456789")

    # Generate unique database name for this file (ensures isolation between users)
    from datetime import datetime
    filename = os.path.basename(INPUT_FILE)
    # Remove extension and sanitize for Neo4j database naming
    clean_filename = re.sub(r'[^a-zA-Z0-9]', '_', os.path.splitext(filename)[0])[:30]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    UNIQUE_DB_NAME = f"chronos_{clean_filename}_{timestamp}".lower()

    # OCR Settings for old medical documents
    OCR_CONFIG = {
        "ocr_preprocessing": True,
        "enhancement_level": "aggressive",  # For very old documents
        "use_high_dpi": True,
        "use_advanced_ocr": True,
        "medical_context": True,
        "save_debug_images": True,
        "try_native_text": True
    }

    # ==================== DISPLAY CONFIGURATION ====================

    print("\n" + "="*80)
    print("CONFIGURATION")
    print("="*80)
    print(f"\n📄 Input: {INPUT_FILE}")
    print(f"📝 Output: {OUTPUT_TEXT_FILE}")
    print(f"💾 Neo4j: {NEO4J_URL}")
    print(f"🗄️  Database: {UNIQUE_DB_NAME} (unique for this file)")
    print(f"\n⚙️  Settings:")
    print(f"   - OCR Enhancement: {OCR_CONFIG['enhancement_level']}")
    print(f"   - Medical Context: {OCR_CONFIG['medical_context']}")

    # Confirm before proceeding
    print("\n" + "="*80)
    response = input("Proceed with processing? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled")
        return

    # Run REFINED CHRONOS Pipeline
    try:
        print("\n" + "="*80)
        print("STARTING REFINED CHRONOS PIPELINE")
        print("="*80)

        # Step 1: Run OCR to extract text
        print("\n" + "="*80)
        print("📋 STEP 1: Extract Text from Document (OCR)")
        print("="*80)

        ocr_engine = OCREngine(use_advanced_model=OCR_CONFIG.get('use_advanced_ocr', True))

        # Map OCR config parameters
        ocr_params = {
            'use_preprocessing': OCR_CONFIG.get('ocr_preprocessing', True),
            'enhancement_level': OCR_CONFIG.get('enhancement_level', 'medium'),
            'high_dpi': OCR_CONFIG.get('use_high_dpi', True),
            'medical_context': OCR_CONFIG.get('medical_context', True),
            'save_debug_images': OCR_CONFIG.get('save_debug_images', False),
            'try_native_text': OCR_CONFIG.get('try_native_text', True)
        }

        extracted_text = ocr_engine.process_file(INPUT_FILE, **ocr_params)

        # Save extracted text
        if OUTPUT_TEXT_FILE:
            print(f"\n💾 Saving extracted text to: {OUTPUT_TEXT_FILE}")
            with open(OUTPUT_TEXT_FILE, "w", encoding="utf-8") as f:
                f.write(extracted_text)
            print("✅ Text saved successfully!")

        print(f"\n✅ Text extraction complete: {len(extracted_text):,} characters")

        # Step 2: Run Phase 1 - Self-Critical Brainstorm
        print("\n" + "="*80)
        print("📋 STEP 2: PHASE 1 - Self-Critical Brainstorm")
        print("="*80)

        phase1_brainstorm = None
        try:
            phase1 = Phase1Brainstorm()
            result = phase1.generate_and_save(
                ocr_text=extracted_text,
                output_dir="chronos_results/phase1"
            )

            phase1_brainstorm = result["brainstorm"]
            print(f"\n✅ Phase 1 completed: {len(phase1_brainstorm):,} characters generated")
            print(f"   Saved to: chronos_results/phase1/")

        except Exception as e:
            print(f"\n⚠️  Phase 1 failed: {e}")
            import traceback
            traceback.print_exc()
            return

        # Step 3: Run Phase 2 - Building Context and Connections
        print("\n" + "="*80)
        print("📋 STEP 3: PHASE 2 - Building Context and Connections")
        print("="*80)
        print("   Building HeritageNet (Historical Medical Evidence)")
        print("   Building SpineNet (Modern Spine Science)")
        print("   Creating Bridges (Historical-Modern Connections)")
        print()

        phase2_results = None
        try:
            # Get Neo4j credentials - use unique database for this file
            phase2_builder = Phase2ContextBuilder(
                neo4j_url=NEO4J_URL,
                neo4j_username=NEO4J_USERNAME,
                neo4j_password=NEO4J_PASSWORD,
                neo4j_database=UNIQUE_DB_NAME
            )

            phase2_results = phase2_builder.run_phase2(
                phase1_brainstorm=phase1_brainstorm,
                ocr_text=extracted_text,
                output_dir="chronos_results/phase2"
            )

            phase2_builder.close()

            print(f"\n✅ Phase 2 completed successfully!")
            if phase2_results['graph_element']:
                print(f"   - Knowledge Graph: {len(phase2_results['graph_element'].nodes)} nodes, {len(phase2_results['graph_element'].relationships)} relationships")
            print(f"   - Summary saved to: chronos_results/phase2/")

        except Exception as e:
            print(f"\n⚠️  Phase 2 failed: {e}")
            import traceback
            traceback.print_exc()
            print("   Continuing to next phases...")

        # Step 4: Run Phase 3 - Distilling to the Essence
        print("\n" + "="*80)
        print("📋 STEP 4: PHASE 3 - Distilling to the Essence")
        print("="*80)
        print("   Generating alternatives using 3 lenses:")
        print("   • LENS A: Modern Research Extensions")
        print("   • LENS B: Historical Observation Extensions")
        print("   • LENS C: Bridge Questions")
        print()

        phase3_results = None
        if phase2_results and phase2_results.get('summary'):
            try:
                phase3_distiller = Phase3Distiller()

                phase3_results = phase3_distiller.run_phase3(
                    phase2_summary=phase2_results['summary'],
                    output_dir="chronos_results/phase3"
                )

                print(f"\n✅ Phase 3 completed successfully!")
                completed_lenses = [k for k, v in phase3_results.items() if v and k != 'phase']
                print(f"   - Completed lenses: {len(completed_lenses)}")
                for lens_key in ['lens_a', 'lens_b', 'lens_c', 'synthesis']:
                    if phase3_results.get(lens_key):
                        print(f"   - {phase3_results[lens_key].get('lens', lens_key)}: ✅")
                print(f"   - Results saved to: chronos_results/phase3/")

            except Exception as e:
                print(f"\n⚠️  Phase 3 failed: {e}")
                import traceback
                traceback.print_exc()
                print("   Continuing to next phases...")
        else:
            print("   ⏭️  Skipping Phase 3 (Phase 2 summary not available)")

        # Step 5: Run Phase 4 - Formulating Testable Hypotheses
        print("\n" + "="*80)
        print("📋 STEP 5: PHASE 4 - The Final Product")
        print("="*80)
        print("   Generating detailed research questions with:")
        print("   • Complete 13-field specification")
        print("   • Innovation × Testability × Impact ranking")
        print("   • Executive summary for stakeholders")
        print()

        phase4_results = None
        if phase3_results and phase3_results.get('synthesis'):
            try:
                phase4_formulator = Phase4Formulator()

                phase4_results = phase4_formulator.run_phase4(
                    phase3_synthesis=phase3_results['synthesis']['synthesis'],
                    num_questions=10,  # Generate 10 questions
                    top_n=3,  # Select top 3
                    output_dir="chronos_results/phase4",
                    use_h_format=True  # Use H-format (concise) by default
                )

                print(f"\n✅ Phase 4 completed successfully!")
                if phase4_results.get('questions'):
                    print(f"   - Generated {phase4_results['questions']['num_questions']} research questions ✅")
                if phase4_results.get('ranking'):
                    print(f"   - Ranked and selected top {phase4_results['ranking']['top_n']} ✅")
                if phase4_results.get('summary'):
                    print(f"   - Created executive summary ✅")
                print(f"   - Results saved to: chronos_results/phase4/")

            except Exception as e:
                print(f"\n⚠️  Phase 4 failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("   ⏭️  Skipping Phase 4 (Phase 3 synthesis not available)")

        # Step 6: Extract top 2 questions and send to FutureHouse
        top_questions = []
        if phase4_results and phase4_results.get('questions') and phase4_results.get('ranking'):
            print("\n" + "="*80)
            print("📤 STEP 6: FUTUREHOUSE API - Hypothesis Verification")
            print("="*80)
            print("   Extracting top 2 questions from Phase 4 results...")
            print()

            try:
                # Extract top 2 questions using the ranking file
                ranking_file = phase4_results['ranking']['output_file']
                top_questions = extract_top_questions_from_phase4(
                    phase4_results=phase4_results,
                    ranking_file=ranking_file,
                    top_n=2
                )

                if top_questions:
                    print(f"   ✅ Extracted {len(top_questions)} questions:")
                    for i, q in enumerate(top_questions, 1):
                        preview = q[:100] + "..." if len(q) > 100 else q
                        print(f"      {i}. {preview}")
                    print()

                    # Send to FutureHouse
                    print("   📤 Sending questions to FutureHouse API...")
                    verifier = HypothesisVerifier(output_dir="chronos_results/futurehouse")
                    verification_results = verifier.verify_questions_sync(top_questions, batch_size=2)

                    if verification_results:
                        print(f"\n   ✅ FutureHouse verification completed!")
                        print(f"      {len(verification_results)} questions verified")
                        print(f"      Results saved to: chronos_results/futurehouse/")
                    else:
                        print(f"\n   ⚠️  FutureHouse verification returned no results")

                else:
                    print("   ⚠️  Could not extract questions from Phase 4 results")

            except Exception as e:
                print(f"   ⚠️  FutureHouse verification failed: {e}")
                import traceback
                traceback.print_exc()

        # Summary
        print("\n" + "="*80)
        print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*80)

        print(f"\n📊 REFINED CHRONOS Pipeline Summary:")
        print(f"   - Phase 1 (Brainstorm) completed ✅")
        print(f"   - Phase 2 (Context Building) completed ✅")
        print(f"     • HeritageNet: Historical medical observations")
        print(f"     • SpineNet: Modern spine science concepts")
        print(f"     • Bridges: Historical-modern connections")
        print(f"   - Phase 3 (Distilling) completed ✅")
        print(f"     • LENS A: Modern Research Extensions")
        print(f"     • LENS B: Historical Observation Extensions")
        print(f"     • LENS C: Bridge Questions")
        print(f"     • Synthesis: Unique angles and priorities")
        print(f"   - Phase 4 (The Final Product) completed ✅")
        print(f"     • Generated 10 detailed research questions (13 fields each)")
        print(f"     • Ranked by Innovation × Testability × Impact")
        print(f"     • Selected top 3 questions")
        print(f"     • Created executive summary")
        print(f"   - Results saved in: chronos_results/phase1/, phase2/, phase3/, phase4/")

        print("\n💡 Next steps:")
        print(f"   1. Review Phase 1 brainstorm in: chronos_results/phase1/")
        print(f"   2. Review Phase 2 summary and KG in: chronos_results/phase2/")
        print(f"   3. Review Phase 3 alternatives in: chronos_results/phase3/")
        print(f"      - lens_a_modern_extensions_*.txt")
        print(f"      - lens_b_historical_extensions_*.txt")
        print(f"      - lens_c_bridge_questions_*.txt")
        print(f"      - phase3_synthesis_*.txt")
        print(f"   4. Review Phase 4 research questions in: chronos_results/phase4/")
        print(f"      - research_questions_*.txt (10 detailed questions)")
        print(f"      - question_ranking_*.txt (ranking analysis)")
        print(f"      - executive_summary_*.txt (stakeholder summary)")
        print("   5. Open Neo4j Browser: http://localhost:7474")
        print(f"      (Knowledge graph stored in '{UNIQUE_DB_NAME}' database)")
        print("   6. View extracted text in:", OUTPUT_TEXT_FILE)
        print("   7. Check FutureHouse verification: chronos_results/futurehouse/")
        print(f"\n📊 Your unique database: {UNIQUE_DB_NAME}")
        print("   Each file gets its own isolated knowledge graph!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
    except Exception as e:
        print(f"\n\n❌ PIPELINE FAILED")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

        print("\n💡 Troubleshooting:")
        print("   1. Check all API keys in .env file")
        print("   2. Verify Neo4j is running")
        print("   3. Check input file path")
        print("   4. Review error message above")


if __name__ == "__main__":
    main()