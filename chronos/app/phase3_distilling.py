"""
Phase 3: Distilling to the Essence
===================================

Refines Phase 2 ideas by systematically asking "What if they had done [something else]?"
Uses THREE lenses to generate alternative research directions:
- LENS A: Modern Research Extensions
- LENS B: Historical Observation Extensions
- LENS C: Bridge Questions
"""

import os
import google.generativeai as genai
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime


class Phase3Distiller:
    """
    Phase 3: Distilling to the Essence

    Takes Phase 2 knowledge graph bridges and systematically generates
    alternative research directions using three analytical lenses.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash"
    ):
        """
        Initialize Phase 3 Distiller.

        Args:
            api_key: Google API key (if None, reads from GOOGLE_API_KEY env var)
            model: Gemini model to use
        """
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        genai.configure(api_key=self.api_key)
        self.model = self._configure_model(model)
        print(f"✅ Phase 3 Distiller initialized with model: {model}")

    def _configure_model(self, model_name: str):
        """Configure Gemini model for Phase 3."""
        generation_config = {
            "temperature": 0.7,  # Higher for creative "what if" generation
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

    def get_phase3_prompt(self) -> str:
        """Get the Phase 3 prompt."""
        return """### **PHASE 3: Distilling to the Essence**

**Goal:** Refine ideas by systematically asking "What if they had done [something else]?" - now enriched with historical-modern bridges.

**Actions:**
- **Return to primary papers** (both modern AND relevant historical sources)
- **Generate alternatives systematically using THREE lenses:**

  **LENS A: Modern Research Extensions**
  For each key modern study, ask what if they had used:
  - Different populations (e.g., different age groups, ethnicities, disease stages)
  - Different measurements (e.g., advanced imaging, biomarkers, wearables)
  - Different analytical methods (e.g., machine learning, network analysis)
  - Different controls (e.g., active controls, sham procedures)
  - Different stimulus sets (e.g., varied loading conditions, environmental factors)
  - Different time scales (e.g., longitudinal vs. cross-sectional)
  - Different contexts (e.g., occupational, athletic, post-surgical)
  - Different theoretical frameworks (e.g., mechanistic vs. phenomenological)

  **LENS B: Historical Observation Extensions**
  For each key historical observation, ask:
  - What if we tested this with modern imaging/measurement technology?
  - What if we applied this to different patient populations than historical texts described?
  - What if we isolated the active mechanism from the outdated theoretical framework?
  - What if we combined historical treatment principles with modern delivery methods?

  **LENS C: Bridge Questions**
  - What if historical treatment X actually worked via mechanism Y (which we now understand)?
  - What if modern condition Z is what historical physicians called A (just described differently)?
  - What if the historical observation was correct but the explanation was wrong?
  - What if cross-cultural convergence on observation B indicates real phenomenon worth investigating?

- **Don't select yet:** Generate multiple alternatives across all three lenses
- **Identify unique angles:** What can **YOU** see that others missed, given your:
  - Interdisciplinary reading in modern spine science
  - Access to historical observations others haven't considered
  - Ability to translate across conceptual frameworks
  - Recognition of cross-cultural convergences

**Example of Phase 3 in Action:**
Historical observation (Ollivier, 1824): Patients with suddenly suppressed sweating or menstruation developed paralysis
Bridge translation: Acute hormonal/autonomic changes → altered spinal cord blood flow or immune function
Modern lens questions:
- What if we studied MS relapses in relation to menstrual cycle disruptions? (different population)
- What if we measured autonomic function and spinal cord perfusion simultaneously? (different measurements)
- What if we used wearable sensors to track sweating patterns in people prone to transient neurological symptoms? (different technology)
Historical lens questions:
- What if we applied advanced imaging to detect the "congestion" Ollivier could only see at autopsy?
- What if we tested hormone replacement therapy as neuroprotection in at-risk patients?
Bridge questions:
- What if "suppressed evacuations" actually represented measurable autonomic dysfunction that we can now quantify?
- What if Thai elemental imbalance diagnosis corresponds to measurable inflammatory/metabolic profiles?"""

    def generate_lens_a_alternatives(
        self,
        phase2_summary: str,
        output_dir: str = "chronos_results/phase3"
    ) -> Dict[str, Any]:
        """
        Generate LENS A: Modern Research Extensions.
        """
        print("\n🔬 LENS A: Modern Research Extensions")
        print("   Generating 'what if' alternatives for modern studies...")

        full_prompt = f"""{self.get_phase3_prompt()}

---

## TASK: Generate LENS A Alternatives (Modern Research Extensions)

Based on the Phase 2 analysis below, systematically generate "what if" questions for modern research extensions.

For each modern concept or study mentioned in Phase 2, generate alternatives asking:
- What if they used different populations?
- What if they used different measurements?
- What if they used different analytical methods?
- What if they used different controls?
- What if they used different time scales?
- What if they used different contexts?

**Format your output as:**

## LENS A: Modern Research Extensions

### Alternative Set 1: [Brief description]
- **What if**: [Alternative approach]
- **Rationale**: [Why this is interesting]
- **Expected insight**: [What we might learn]

### Alternative Set 2: [Brief description]
...

---

## PHASE 2 ANALYSIS:
{phase2_summary}

---

Generate at least 10 alternative sets for LENS A."""

        try:
            print("   🔄 Generating alternatives with Gemini...")
            response = self.model.generate_content(full_prompt)

            if not response.text:
                raise ValueError("Empty response from Gemini model")

            lens_a_output = response.text

            # Save output
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(output_dir, f"lens_a_modern_extensions_{timestamp}.txt")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(lens_a_output)

            print(f"   ✅ Generated {len(lens_a_output):,} characters")
            print(f"   💾 Saved to: {output_file}")

            return {
                "lens": "A - Modern Research Extensions",
                "output": lens_a_output,
                "output_file": output_file,
                "timestamp": timestamp
            }

        except Exception as e:
            print(f"   ❌ ERROR during LENS A generation: {e}")
            import traceback
            traceback.print_exc()
            raise

    def generate_lens_b_alternatives(
        self,
        phase2_summary: str,
        output_dir: str = "chronos_results/phase3"
    ) -> Dict[str, Any]:
        """
        Generate LENS B: Historical Observation Extensions.
        """
        print("\n🏛️  LENS B: Historical Observation Extensions")
        print("   Generating 'what if' alternatives for historical observations...")

        full_prompt = f"""{self.get_phase3_prompt()}

---

## TASK: Generate LENS B Alternatives (Historical Observation Extensions)

Based on the Phase 2 analysis below, systematically generate "what if" questions for historical observation extensions.

For each historical observation mentioned in Phase 2, generate alternatives asking:
- What if we tested this with modern imaging/measurement technology?
- What if we applied this to different patient populations than historical texts described?
- What if we isolated the active mechanism from the outdated theoretical framework?
- What if we combined historical treatment principles with modern delivery methods?

**Format your output as:**

## LENS B: Historical Observation Extensions

### Alternative Set 1: [Historical observation]
- **What if**: [Modern technology/method to test it]
- **Rationale**: [Why this is worth investigating]
- **Expected insight**: [What we might discover]

### Alternative Set 2: [Historical observation]
...

---

## PHASE 2 ANALYSIS:
{phase2_summary}

---

Generate at least 10 alternative sets for LENS B."""

        try:
            print("   🔄 Generating alternatives with Gemini...")
            response = self.model.generate_content(full_prompt)

            if not response.text:
                raise ValueError("Empty response from Gemini model")

            lens_b_output = response.text

            # Save output
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(output_dir, f"lens_b_historical_extensions_{timestamp}.txt")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(lens_b_output)

            print(f"   ✅ Generated {len(lens_b_output):,} characters")
            print(f"   💾 Saved to: {output_file}")

            return {
                "lens": "B - Historical Observation Extensions",
                "output": lens_b_output,
                "output_file": output_file,
                "timestamp": timestamp
            }

        except Exception as e:
            print(f"   ❌ ERROR during LENS B generation: {e}")
            import traceback
            traceback.print_exc()
            raise

    def generate_lens_c_alternatives(
        self,
        phase2_summary: str,
        output_dir: str = "chronos_results/phase3"
    ) -> Dict[str, Any]:
        """
        Generate LENS C: Bridge Questions.
        """
        print("\n🌉 LENS C: Bridge Questions")
        print("   Generating 'what if' questions that bridge historical-modern...")

        full_prompt = f"""{self.get_phase3_prompt()}

---

## TASK: Generate LENS C Alternatives (Bridge Questions)

Based on the Phase 2 analysis below, systematically generate bridge questions that connect historical and modern understanding.

For each historical-modern bridge identified in Phase 2, generate questions asking:
- What if historical treatment X actually worked via mechanism Y (which we now understand)?
- What if modern condition Z is what historical physicians called A (just described differently)?
- What if the historical observation was correct but the explanation was wrong?
- What if cross-cultural convergence on observation B indicates real phenomenon worth investigating?

**Format your output as:**

## LENS C: Bridge Questions

### Bridge Set 1: [Historical → Modern connection]
- **What if**: [Bridge hypothesis]
- **Historical context**: [What they saw/did]
- **Modern mechanism**: [How we'd explain/test it now]
- **Testability**: [How we could investigate this]

### Bridge Set 2: [Historical → Modern connection]
...

---

## PHASE 2 ANALYSIS:
{phase2_summary}

---

Generate at least 10 bridge question sets for LENS C."""

        try:
            print("   🔄 Generating bridge questions with Gemini...")
            response = self.model.generate_content(full_prompt)

            if not response.text:
                raise ValueError("Empty response from Gemini model")

            lens_c_output = response.text

            # Save output
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(output_dir, f"lens_c_bridge_questions_{timestamp}.txt")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(lens_c_output)

            print(f"   ✅ Generated {len(lens_c_output):,} characters")
            print(f"   💾 Saved to: {output_file}")

            return {
                "lens": "C - Bridge Questions",
                "output": lens_c_output,
                "output_file": output_file,
                "timestamp": timestamp
            }

        except Exception as e:
            print(f"   ❌ ERROR during LENS C generation: {e}")
            import traceback
            traceback.print_exc()
            raise

    def generate_synthesis(
        self,
        lens_a_result: Dict[str, Any],
        lens_b_result: Dict[str, Any],
        lens_c_result: Dict[str, Any],
        output_dir: str = "chronos_results/phase3"
    ) -> Dict[str, Any]:
        """
        Generate synthesis of all three lenses.
        """
        print("\n📊 Synthesizing all three lenses...")

        full_prompt = f"""{self.get_phase3_prompt()}

---

## TASK: Synthesize Three Lenses

You have generated alternatives from three different lenses. Now synthesize them to identify:

1. **Unique Angles**: What can YOU see that others missed, given:
   - Interdisciplinary reading in modern spine science
   - Access to historical observations others haven't considered
   - Ability to translate across conceptual frameworks
   - Recognition of cross-cultural convergences

2. **High-Priority Alternatives**: Which alternatives across all three lenses are:
   - Most innovative (unlikely to have been studied before)
   - Most testable (with current technology/resources)
   - Most impactful (could change clinical practice or understanding)

3. **Synergistic Combinations**: Which alternatives from different lenses could be combined into even stronger research directions?

**Format your output as:**

## PHASE 3 SYNTHESIS: Distilling to the Essence

### Unique Angles We Can See
[List 5-10 unique angles across all three lenses]

### High-Priority Alternatives
[Rank top 10-15 alternatives by innovation × testability × impact]

### Synergistic Combinations
[Identify 3-5 ways to combine alternatives from different lenses]

---

## LENS A OUTPUT:
{lens_a_result['output']}

---

## LENS B OUTPUT:
{lens_b_result['output']}

---

## LENS C OUTPUT:
{lens_c_result['output']}

---

Provide the synthesis above."""

        try:
            print("   🔄 Generating synthesis with Gemini...")
            response = self.model.generate_content(full_prompt)

            if not response.text:
                raise ValueError("Empty response from Gemini model")

            synthesis_output = response.text

            # Save output
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(output_dir, f"phase3_synthesis_{timestamp}.txt")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(synthesis_output)

            print(f"   ✅ Generated {len(synthesis_output):,} characters")
            print(f"   💾 Saved to: {output_file}")

            return {
                "synthesis": synthesis_output,
                "output_file": output_file,
                "timestamp": timestamp
            }

        except Exception as e:
            print(f"   ❌ ERROR during synthesis generation: {e}")
            import traceback
            traceback.print_exc()
            raise

    def run_phase3(
        self,
        phase2_summary: str,
        output_dir: str = "chronos_results/phase3"
    ) -> Dict[str, Any]:
        """
        Run complete Phase 3: Generate all three lenses + synthesis.

        Args:
            phase2_summary: Phase 2 summary output
            output_dir: Directory to save results

        Returns:
            Dictionary with all results
        """
        print("\n" + "="*80)
        print("🔬 PHASE 3: DISTILLING TO THE ESSENCE")
        print("="*80)
        print(f"   Input: Phase 2 summary ({len(phase2_summary):,} chars)")
        print(f"   Generating alternatives using 3 lenses...")
        print()

        results = {
            "phase": "Phase 3",
            "lens_a": None,
            "lens_b": None,
            "lens_c": None,
            "synthesis": None
        }

        # Generate LENS A: Modern Research Extensions
        try:
            results["lens_a"] = self.generate_lens_a_alternatives(
                phase2_summary=phase2_summary,
                output_dir=output_dir
            )
        except Exception as e:
            print(f"   ⚠️  LENS A failed: {e}")

        # Generate LENS B: Historical Observation Extensions
        try:
            results["lens_b"] = self.generate_lens_b_alternatives(
                phase2_summary=phase2_summary,
                output_dir=output_dir
            )
        except Exception as e:
            print(f"   ⚠️  LENS B failed: {e}")

        # Generate LENS C: Bridge Questions
        try:
            results["lens_c"] = self.generate_lens_c_alternatives(
                phase2_summary=phase2_summary,
                output_dir=output_dir
            )
        except Exception as e:
            print(f"   ⚠️  LENS C failed: {e}")

        # Generate Synthesis
        if results["lens_a"] and results["lens_b"] and results["lens_c"]:
            try:
                results["synthesis"] = self.generate_synthesis(
                    lens_a_result=results["lens_a"],
                    lens_b_result=results["lens_b"],
                    lens_c_result=results["lens_c"],
                    output_dir=output_dir
                )
            except Exception as e:
                print(f"   ⚠️  Synthesis failed: {e}")
        else:
            print("   ⏭️  Skipping synthesis (not all lenses completed)")

        print("\n✅ Phase 3 completed!")
        return results


def run_phase3(
    phase2_summary: str,
    output_dir: str = "chronos_results/phase3"
) -> Dict[str, Any]:
    """
    Convenience function to run Phase 3.

    Args:
        phase2_summary: Phase 2 summary output
        output_dir: Directory to save results

    Returns:
        Dictionary with Phase 3 results
    """
    distiller = Phase3Distiller()

    results = distiller.run_phase3(
        phase2_summary=phase2_summary,
        output_dir=output_dir
    )

    return results


if __name__ == "__main__":
    # Test Phase 3
    sample_phase2 = """
    Phase 2 Analysis:

    HeritageNet Mapping:
    - Ollivier (1824): Spinal blood congestion causing transient paralysis
    - Thai medicine: Wind element imbalance treated with herbal oils
    - Cross-cultural convergence on autonomic-vascular phenomena

    SpineNet Connections:
    - Modern concept: Reversible spinal venous engorgement
    - Modern mechanism: Hormonal/autonomic triggers for vascular changes
    - Research gap: Transient myelopathy imaging

    Bridges:
    - "Spinal blood congestion" → reversible venous engorgement
    - "Suppressed evacuations" → neuroendocrine dysregulation
    - Herbal oils → improved microcirculation + anti-inflammatory effects
    """

    print("Testing Phase 3 Distiller...")
    results = run_phase3(sample_phase2, "test_output/phase3")
    print(f"\nResults: {len([k for k, v in results.items() if v])} components generated")
