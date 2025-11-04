"""
Phase 1: Self-Critical Brainstorm
Generate free-flowing exploration of spine health phenomena from OCR-extracted text.
"""

import os
import google.generativeai as genai
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime


class Phase1Brainstorm:
    """
    Phase 1 of CHRONOS methodology: Self-Critical Brainstorm

    Takes OCR-extracted text and generates free-flowing reasoning rooted in
    genuine curiosity about spine health phenomena.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash"):
        """
        Initialize Phase 1 Brainstorm engine.

        Args:
            api_key: Google API key (if None, reads from GOOGLE_API_KEY env var)
            model: Gemini model to use (default: gemini-2.0-flash-exp)
        """
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables or provided")

        genai.configure(api_key=self.api_key)
        self.model = self._configure_model(model)
        print(f"✅ Phase 1 Brainstorm initialized with model: {model}")

    def _configure_model(self, model_name: str):
        """Configure Gemini model with optimal settings for creative brainstorming."""
        generation_config = {
            "temperature": 0.8,  # Higher temperature for creative exploration
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        return genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

    def get_chronos_system_prompt(self) -> str:
        """Get the core CHRONOS methodology prompt."""
        return """# Chronos Megaprompt

You are an experienced spine health expert and surgeon equipped with the **CHRONOS methodology** for mining historical medical knowledge. Your role is to help researchers develop exceptional, impactful, innovative research questions in spine health through a structured, iterative creative process that bridges historical observations with modern scientific understanding.

## Core Philosophy

Good research questions are **NOT** just clear, focused, and novel. They are:

- **Itchy and persistent** - they capture genuine enthusiasm and curiosity
- **Reframing exercises** - they challenge assumptions or demonstrate how past scientific and technological limitations obscured understanding
- **Historically informed** - they recognize that valuable insights may exist in overlooked historical medical texts
- **Innovative in approach** - they explore new methodologies, populations, or perspectives
- **Interdisciplinary** - they draw connections across fields, traditions and cultures that others might miss
- **Attentive to nuance and detail** - they recognize that breakthrough insights often hide in overlooked specifics, subtle patterns, or seemingly minor observations. The devil is in the details: a casual mention in a historical text (e.g., "paralysis following suppressed sweating"), a small subgroup with different outcomes, an unusual but consistent side effect, or a precise description of timing and context can reveal mechanisms that broader observations miss. Great questions emerge from noticing what others glossed over—the specific dose that worked, the particular patient characteristics, the exact temporal sequence, the environmental conditions, or the subtle differences between similar presentations. This attentiveness extends to recognizing when historical physicians were remarkably precise in their observations despite lacking modern frameworks, and when modern studies may have averaged away important variations

## The CHRONOS Principle

Following Tu Youyou's Nobel Prize-winning approach to mining traditional Chinese medicine for artemisinin, **CHRONOS** systematically extracts and formalizes hypotheses from historical medical texts. The innovation lies in recognizing that:

- Historical observations may be valid even when theoretical frameworks are outdated (e.g., "spinal blood congestion" observed in 1824 may correspond to real venous phenomena, even if explained via humoral theory)
- Cross-cultural convergence increases plausibility (when Western and Eastern traditions independently note similar phenomena)
- Abandoned treatments may contain kernels of truth (strychnine was toxic but the principle of neuromodulation was sound)
- Modern technology can test historical hypotheses rigorously (advanced imaging can now detect the "congestion" Ollivier could only observe at autopsy)"""

    def get_phase1_prompt(self) -> str:
        """Get the Phase 1 specific instructions."""
        return """### **PHASE 1: Self-Critical Brainstorm**

**Goal:** Free-flowing reasoning rooted in genuine curiosity about spine health phenomena.

**Actions:**
- **Identify the spark:** What spine health phenomenon captivates you? Consider:
  - Modern clinical observations and puzzles
  - Patient narratives that don't fit current models
  - Biomechanical paradoxes
  - Unexplained variability in treatment responses
- **Free-form exploration:** Generate connections without judgment:
  - Consider clinical observations, patient narratives, biomechanical puzzles
  - Link phenomena across scales (molecular → tissue → whole body → population)
  - Question conventional wisdom in spine care
  - Wonder: "What if the opposite were true?"
- **Self-critique dialogue:** For each idea, ask:
  - What assumptions am I making?
  - How would skeptics critique this?
  - What if the opposite were true?
  - What controls or comparisons would strengthen this?
- **Document everything:** Capture stream-of-consciousness thoughts about:
  - Unexplained clinical observations
  - Contradictions in existing literature
  - Emerging technologies that could answer old questions differently
  - Patient populations or conditions that are understudied

**Output Format:**
Provide a detailed brainstorm that explores multiple angles, questions assumptions, and identifies intriguing patterns or paradoxes in the historical medical text. Be creative, exploratory, and self-critical."""

    def generate_brainstorm(self, ocr_text: str, save_to_file: Optional[str] = None) -> str:
        """
        Generate Phase 1 brainstorm from OCR-extracted text.

        Args:
            ocr_text: Text extracted from historical medical document
            save_to_file: Optional path to save the brainstorm output

        Returns:
            Generated brainstorm text
        """
        print("\n" + "="*80)
        print("🧠 PHASE 1: SELF-CRITICAL BRAINSTORM")
        print("="*80)
        print(f"  Processing {len(ocr_text):,} characters of historical text...")

        # Construct the full prompt
        full_prompt = f"""{self.get_chronos_system_prompt()}

{self.get_phase1_prompt()}

---

## Historical Medical Text to Analyze:

{ocr_text}

---

Now, conduct a self-critical brainstorm following the Phase 1 instructions above. Explore the spine health phenomena in this historical text with genuine curiosity, question assumptions, and identify patterns or paradoxes that could lead to innovative research questions."""

        try:
            print("  🔄 Generating brainstorm with Gemini...")
            response = self.model.generate_content(full_prompt)

            if not response.text:
                raise ValueError("Empty response from Gemini model")

            brainstorm = response.text

            print(f"  ✅ Brainstorm generated ({len(brainstorm):,} characters)")

            # Save to file if specified
            if save_to_file:
                # Ensure parent directory exists
                os.makedirs(os.path.dirname(save_to_file), exist_ok=True)

                with open(save_to_file, "w", encoding="utf-8") as f:
                    f.write(brainstorm)

                print(f"  💾 Brainstorm saved to: {save_to_file}")

            return brainstorm

        except Exception as e:
            print(f"  ❌ ERROR during Phase 1 brainstorm: {e}")
            import traceback
            traceback.print_exc()
            raise

    def generate_and_save(
        self,
        ocr_text: str,
        output_dir: str = "chronos_results/phase1"
    ) -> Dict[str, Any]:
        """
        Generate brainstorm and save with timestamp.

        Args:
            ocr_text: OCR-extracted text
            output_dir: Directory to save results (default: chronos_results/phase1)

        Returns:
            Dictionary containing brainstorm text and metadata
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f"phase1_brainstorm_{timestamp}.txt")

        # Generate brainstorm
        brainstorm = self.generate_brainstorm(ocr_text, save_to_file=output_file)

        # Create metadata file
        metadata = {
            "timestamp": timestamp,
            "input_length": len(ocr_text),
            "output_length": len(brainstorm),
            "output_file": output_file,
            "phase": "Phase 1 - Self-Critical Brainstorm"
        }

        metadata_file = os.path.join(output_dir, f"phase1_metadata_{timestamp}.txt")
        with open(metadata_file, "w", encoding="utf-8") as f:
            for key, value in metadata.items():
                f.write(f"{key}: {value}\n")

        print(f"\n✅ Phase 1 completed successfully!")
        print(f"   Brainstorm: {output_file}")
        print(f"   Metadata: {metadata_file}")

        return {
            "brainstorm": brainstorm,
            "metadata": metadata
        }


def run_phase1(ocr_text: str, output_dir: str = "chronos_results/phase1") -> str:
    """
    Convenience function to run Phase 1 brainstorm.

    Args:
        ocr_text: OCR-extracted text from historical medical document
        output_dir: Directory to save results

    Returns:
        Generated brainstorm text
    """
    phase1 = Phase1Brainstorm()
    result = phase1.generate_and_save(ocr_text, output_dir)
    return result["brainstorm"]


if __name__ == "__main__":
    # Test with sample text
    sample_text = """
    Historical Medical Text Sample:

    The spinal column exhibits remarkable properties in maintaining postural equilibrium.
    In cases of vertebral displacement, we observe correlations with neurological deficits.
    The congestion of venous structures adjacent to the spinal cord may precipitate
    various pathological manifestations.
    """

    print("Testing Phase 1 Brainstorm Module...")
    result = run_phase1(sample_text, "test_output/phase1")
    print(f"\nGenerated brainstorm preview:\n{result[:500]}...")
