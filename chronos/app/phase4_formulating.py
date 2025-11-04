"""
Phase 4: The Final Product - Formulating Testable Hypotheses
==============================================================

Generates concrete research questions with complete rationale and approach.
Each question includes all 13 required fields from the CHRONOS methodology.
"""

import os
import google.generativeai as genai
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
import json
from chronos_system_prompt import (
    get_chronos_system_prompt,
    get_chronos_h_format_instructions,
    get_example_h_format_question
)


class Phase4Formulator:
    """
    Phase 4: The Final Product

    Generates detailed, testable research questions from Phase 3 alternatives.
    Each question includes complete specification following CHRONOS format.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash-exp"
    ):
        """
        Initialize Phase 4 Formulator.

        Args:
            api_key: Google API key (if None, reads from GOOGLE_API_KEY env var)
            model: Gemini model to use
        """
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        genai.configure(api_key=self.api_key)
        self.model = self._configure_model(model)
        print(f"✅ Phase 4 Formulator initialized with model: {model}")

    def _configure_model(self, model_name: str):
        """Configure Gemini model for Phase 4."""
        generation_config = {
            "temperature": 0.6,  # Balanced - precise but still creative
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

    def get_phase4_prompt(self) -> str:
        """Get the complete Phase 4 prompt with all critical traps and output format."""
        return """### **PHASE 4: The Final Product**

**Goal:** Specify the concrete research question with clear rationale and approach.

**Actions:**
- **Select your focus** from alternatives based on:
  - Resources and expertise available
  - Current state of the field
  - Strength of historical-modern bridge
  - Potential impact if validated
  - Feasibility with current/near-future technologies
- **Specify the design:**
  - Paradigms and tools you'll use
  - Population and sample characteristics
  - Measurement approaches
  - How you'll test the historically-informed hypothesis with modern rigor
  - Timeline and follow-up plans
- **Anticipate alternatives:**
  - Potential confounds
  - Alternative explanations for expected findings
  - How to distinguish between historical framework (outdated) and observation (potentially valid)
  - How to rule out confounds or acknowledge them
- **Frame the question** ensuring it reflects:
  - Clarity and focus
  - Tractability with available methods
  - The novel historical-modern bridge that inspired it
  - Your genuine enthusiasm for answering it
  - How it addresses current clinical needs

## Critical Traps to Avoid

**Trap 1: The Hypothesis Requirement**
**The trap:** Believing every question needs a specific, falsifiable hypothesis
**The reality:** Valuable questions can be:
- Descriptive: "What movement patterns do people with chronic low back pain exhibit during daily activities?"
- Mechanistic: "How does intervertebral disc degeneration influence proprioception?"
- Normative: "Why do humans maintain lumbar lordosis during bipedal locomotion?"
- Exploratory: "Can we detect the spinal venous congestion that Ollivier described using modern imaging?"
**Action:** Embrace exploratory and descriptive research when appropriate, especially when testing historical observations with modern methods

**Trap 2: Excessive Attachment**
**The trap:** Sunk cost fallacy makes you cling to initial questions (or to fascinating historical observations that may not pan out)
**The reality:** Your question may:
- Already be answered through literature review
- Lack necessary precision upon deeper reflection
- Turn out that the historical observation was artifact, not signal
- Need to evolve into something quite different
**Action:** Stay flexible, iterate without guilt, return to earlier phases if needed. Just because a historical observation is interesting doesn't mean it must become a research question.

**Trap 3: "Someone Already Did This!"**
**The trap:** Despair when finding similar published work
**The reality:** Questions are rarely identical. Previous work likely:
- Used different techniques
- Overlooked alternative explanations
- Studied different populations
- Had methodological limitations you can address
- Didn't consider the historical context or cross-cultural convergence you've identified
**Action:** Deploy critical analysis to find how **YOUR** historically-informed approach differs and improves. The CHRONOS bridge itself may be your novelty.

**Trap 4: The Hammer and Nail**
**The trap:** Forcing your specialized expertise onto every problem (or forcing historical observations to fit modern frameworks too rigidly)
**The reality:** Your expertise is valuable but shouldn't constrain thinking. Also, historical observations shouldn't be forced into modern categories where they don't fit.
**Action:** Continuously ask:
- "Is my preferred method truly best for THIS question?"
- "How can my unique historical-modern perspective provide novel insights?"
- "Am I respecting the historical observation or distorting it to fit modern frameworks?"
- "What complementary approaches might I be overlooking?"

**Trap 5: Historical Uncritical Acceptance**
**The trap:** Assuming all historical observations are valid just because they're old or from respected sources
**The reality:** Historical texts contain:
- Genuine empirical observations (potentially valuable)
- Theoretical interpretations (often outdated)
- Observer biases and limited sample sizes
- Lack of controls and confounding factors
- Cultural/temporal context that affects interpretation
**Action:** Maintain scientific skepticism:
- Separate observation from interpretation
- Consider alternative explanations for historical phenomena
- Recognize selection bias (successful cases more likely to be recorded)
- Understand limitations of historical methods
- Use convergence across sources as supporting (not conclusive) evidence

**Trap 6: Framework Confusion**
**The trap:** Conflating outdated theoretical frameworks with valid observations
**The reality:** Historical physicians often:
- Made accurate observations (e.g., "congestion causes paralysis")
- Explained them incorrectly (e.g., "imbalance of humors")
- Used treatments that sometimes worked for reasons they didn't understand
**Action:** Deliberately separate:
- What they saw (empirical observation) ← potentially valuable
- How they explained it (theoretical framework) ← usually outdated
- What they did (treatment) ← may contain valid principles despite wrong theory
- What actually happened (outcome) ← most important but hardest to verify

## Question Types to Consider in Spine Health

Generate questions across these categories, these are only suggestions. See if they are relevant otherwise, extrapolate.

1. **Biomechanical Questions**
   Force transmission, loading patterns, tissue mechanics
   Stability and control systems
   Movement variability and adaptation
   Historical observations of posture, movement, or mechanical interventions

2. **Neurophysiological Questions**
   Pain mechanisms (nociceptive, neuropathic, central sensitization)
   Proprioception and motor control
   Neuroplasticity in chronic conditions
   Historical neuromodulation approaches, observations of nerve function

3. **Tissue Biology Questions**
   Disc degeneration mechanisms
   Healing and regeneration capacity
   Cellular responses to mechanical loading
   Inflammatory processes
   Historical observations of tissue changes, traditional remedies for tissue healing

4. **Clinical Questions**
   Diagnosis and assessment approaches
   Treatment mechanisms and effectiveness
   Prognostic factors and risk stratification
   Phenotyping and patient subgroups
   Historical diagnostic frameworks, treatment outcomes, patient descriptions

5. **Biopsychosocial Questions**
   Psychological factors in pain and disability
   Social determinants of spine health
   Cultural influences on treatment seeking and outcomes
   Patient beliefs and expectations
   Cross-cultural observations, historical patient experiences, traditional healing contexts

6. **Technology and Innovation Questions**
   Novel imaging or assessment technologies
   Wearable sensors and continuous monitoring
   AI/ML for diagnosis, prognosis, or treatment matching
   Virtual reality or digital therapeutics
   Using modern technology to test historical hypotheses, detecting phenomena historical physicians could only observe at autopsy

7. **Population and Equity Questions**
   Understudied populations
   Healthcare access and disparities
   Occupational and environmental factors
   Lifespan considerations (pediatric, aging)
   Populations described in historical texts, traditional medicine practices in specific communities

8. **Translational Questions**
   Bench-to-bedside pathways
   Animal model validity and limitations
   Implementation science in spine care
   Translating historical treatments into modern therapeutic approaches, natural product drug discovery

9. **Vascular and Circulatory Questions (CHRONOS-inspired)**
   Spinal cord perfusion and venous drainage
   Microcirculatory impairment in spine disorders
   Transient vascular phenomena causing neurological symptoms
   Based on: Ollivier's congestion observations, Thai medicine's circulation concepts

10. **Systemic-Spinal Interaction Questions (CHRONOS-inspired)**
    Gut-spine axis mechanisms
    Hormonal influences on spinal cord function
    Autonomic dysfunction and spinal symptoms
    Systemic inflammation affecting local spine pathology
    Based on: Ollivier's visceral-spinal observations, Thai elemental balance frameworks

11. **Phytochemical and Natural Product Questions (CHRONOS-inspired)**
    Herbal compounds for neuromodulation
    Transdermal delivery of plant-based anti-inflammatories
    Animal-derived substances for nerve repair
    Traditional formulations and their mechanisms
    Based on: Thai herbal remedies, historical pharmacological interventions

## Output Format

For each research question generated, provide:

1. **The Question** (clear, concise statement)
2. **The Spark**
   What phenomenon or curiosity drives this?
   Include both modern observations AND historical context if applicable
3. **The Historical-Modern Bridge (CHRONOS-specific)**
   What historical observation(s) inspired this? (if applicable)
   How do you translate historical terminology to modern concepts?
   What convergences across traditions support this?
   How does modern science now enable testing what historical physicians could only observe?
4. **The Gap**
   What's missing in current literature?
   Why has this historical insight been overlooked?
5. **The Innovation**
   What makes this approach novel?
   Is it reframing an old question?
   Challenging an assumption?
   Using a new method/population/lens?
   Making an unexpected connection?
   Bridging historical and modern knowledge?
6. **Interdisciplinary Connections**
   Relevant modern fields and how they inform the question
   Historical medical traditions that contribute insights
   Cross-domain bridges you're creating
7. **Question Type**
   Descriptive/mechanistic/normative/hypothesis-driven
   Which category from the list above
8. **Potential Approaches**
   Brief overview of methods
   How modern technology enables testing historical hypotheses
   What measurements would bridge historical observations with modern data
9. **Alternative Explanations to Consider**
   Potential confounds
   How to distinguish between historical framework (outdated) and observation (potentially valid)
   Competing modern explanations
10. **Evidence Landscape**
    Historical evidence (strength, limitations)
    Modern supporting evidence
    Modern contradicting evidence
    Gaps where research is needed
11. **Why This Matters**
    Potential impact on spine health science and/or patient care
    Clinical needs addressed
    How validating historical insights could shift current paradigms
12. **Feasibility Assessment**
    Testability with current/near-future methods
    Resources required
    Timeline estimate (immediate/short-term 1-3yr/medium-term 3-7yr/long-term 7+yr)
13. **Possible Traps**
    Which of the six traps might threaten this question?
    Specific warnings about historical observation validity
    How to avoid them

### Example Output Structure

**Question**
How does transient spinal venous congestion contribute to episodic neurological symptoms in patients without structural pathology, and can modern imaging detect these reversible phenomena?

**The Spark**
Clinical observation: Patients present with transient paralysis or sensory deficits that resolve spontaneously, with normal structural imaging. Neurologists often attribute these to "functional" disorders or miss diagnoses.

**The Historical-Modern Bridge**
Historical observation: Charles-Prosper Ollivier d'Angers (1824) documented cases of "congestions sanguines rachidiennes" (spinal blood congestions) causing temporary paralysis without intellectual impairment. He noted these resolved spontaneously and often left no visible traces at autopsy. He linked them to triggers like suppressed sweating or postpartum changes.
Translation: "Spinal blood congestion" → reversible venous engorgement or microcirculatory impairment of spinal cord
Cross-cultural convergence: Thai traditional medicine (19th c.) independently described using herbal oils and massage to relieve "nerve congestion" causing paralysis - suggesting improved local circulation resolves symptoms
Modern capability: Ollivier could only observe congestion at autopsy. We now have dynamic MRI, spinal venography, and ultrasound to detect these phenomena in living patients.

**The Gap**
Modern neurology recognizes spinal cord ischemia and dural AVMs, but the concept of transient, reversible venous congestion as a cause of episodic symptoms is underexplored. Many patients with transient neurological events remain undiagnosed.

**The Innovation**
Reframes: Idiopathic transient neurological symptoms as potentially vascular rather than purely functional
Challenges: Assumption that structural imaging rules out vascular causes
Novel method: Using dynamic imaging to detect episodic congestion that standard imaging misses
Historical bridge: Tests 200-year-old observation with modern technology
Cross-cultural: Integrates Western clinical observation with Eastern therapeutic principle

**Interdisciplinary Connections**
Neurology: transient ischemic attacks, spinal cord ischemia
Vascular medicine: venous insufficiency, venous drainage patterns
Radiology: advanced MRI techniques, contrast dynamics
Traditional medicine: Thai circulation-enhancing therapies
Physiology: spinal cord perfusion, venous anatomy
Autonomic medicine: Ollivier's noted triggers (sweating, hormonal changes)

**Question Type**
Mechanistic and hypothesis-driven; explores "how" a historical observation manifests physiologically

**Potential Approaches**
Imaging study: Dynamic contrast-enhanced MRI or phase-contrast imaging in patients during/after transient symptoms to detect venous congestion
Provocation study: Monitor spinal venous flow during maneuvers that alter venous pressure
Case-control: Compare spinal venous anatomy/drainage patterns in patients with unexplained transient symptoms vs. controls
Animal model: Induce reversible venous congestion in animal spinal cord to see if it produces temporary deficits without lasting damage
Therapeutic trial: Test interventions to improve venous drainage (positioning, medications) in patients with recurrent episodes

**Alternative Explanations**
Symptoms are functional/psychogenic (need objective imaging to rule out)
Arterial rather than venous phenomena (distinguish with imaging)
Inflammatory rather than vascular (measure inflammatory markers)
Historical observations were misinterpretations of other conditions (test directly)
Convergence with Thai medicine is coincidental (independent validation needed)

**Evidence Landscape**
**Historical evidence:**
Ollivier's case series (1824) - anecdotal, no controls, autopsy-based
Thai manuscript treatment reports - traditional use, unclear outcomes
**Strength:** Cross-cultural convergence increases plausibility
**Modern supporting evidence:**
Spinal dural AVFs cause venous congestion with neurological symptoms
Venous insufficiency in brain causes reversible deficits
Some transient myelopathies have unknown cause (gap this could fill)
**Modern contradicting evidence:**
Limited cases of pure venous congestion documented
Most spinal vascular issues involve arterial supply
**Gaps:**
No systematic study of spinal venous dynamics in transient symptoms
Limited dynamic imaging of spinal venous system
No testing of Ollivier's noted triggers (autonomic, hormonal changes)

**Why This Matters**
Clinical impact: Could explain and lead to treatment for currently "idiopathic" transient neurological symptoms. If venous congestion is confirmed, interventions could include:
- Position changes
- Medications to improve venous tone
- Addressing triggers (hormonal management, autonomic optimization)
Scientific impact: Validates a 200-year-old observation using modern methods, demonstrates value of historical medical text mining, opens new area of spinal vascular research
Paradigm shift: Moves beyond "structural vs. functional" dichotomy to recognize reversible physiological causes

**Feasibility Assessment**
Testability: **HIGH** - imaging technology exists, patient population available
Resources: Moderate - requires advanced MRI access, radiology expertise
Timeline: Short to medium-term (1-5 years)
- Year 1-2: Pilot imaging studies
- Year 2-4: Larger case-control studies
- Year 4-5: Intervention trials if mechanism confirmed

**Possible Traps**
**Trap 5 (Historical Uncritical Acceptance):** Must verify Ollivier's observations weren't due to:
- Selection bias (only recording interesting cases)
- Misdiagnosis (other conditions presenting similarly)
- Autopsy artifacts
**Mitigation:** Use modern diagnostic criteria, prospective enrollment, objective imaging
**Trap 6 (Framework Confusion):** Don't accept Ollivier's humoral explanations for why congestion occurred (suppressed evacuations) - but DO test his empirical observation that congestion caused symptoms
**Mitigation:** Separate observation (congestion-paralysis link) from explanation (humoral theory)
**Trap 3 (Someone did this):** Some spinal vascular phenomena are studied, but not this specific transient congestion hypothesis
**Mitigation:** Emphasize the episodic/reversible nature, historical context, and cross-cultural convergence as differentiators
"""

    def generate_research_questions(
        self,
        phase3_synthesis: str,
        num_questions: int = 10,
        output_dir: str = "chronos_results/phase4",
        use_h_format: bool = True
    ) -> Dict[str, Any]:
        """
        Generate detailed research questions from Phase 3 synthesis.

        Args:
            phase3_synthesis: Phase 3 synthesis output
            num_questions: Number of questions to generate
            output_dir: Directory to save results
            use_h_format: If True, use H-format (concise). If False, use 13-field format (detailed)

        Returns:
            Dictionary with generated questions and metadata
        """
        print(f"\n📝 Generating {num_questions} detailed research questions...")
        print(f"   Format: {'H-format (concise)' if use_h_format else '13-field format (detailed)'}")

        if use_h_format:
            # Use H-format: concise, focused on key elements
            system_prompt = get_chronos_system_prompt()
            h_format_instructions = get_chronos_h_format_instructions()
            example = get_example_h_format_question()

            full_prompt = f"""{system_prompt}

{h_format_instructions}

{example}

---

## TASK: Generate H-Format Research Questions

Based on the Phase 3 synthesis below, generate {num_questions} concrete research questions.

**CRITICAL REQUIREMENTS:**
- Each question MUST use the H-format structure (H[number]: Domain)
- Include ALL required fields: Claim Statement, Historical Source, Modern Relevance, Variables, Mechanism, Testability Score, Innovation Potential
- Maintain the historical-modern bridge emphasis throughout
- Provide specific testability scores (1-10) with justification
- Assess innovation potential (Low/Moderate/High) with clear reasoning

**IMPORTANT:**
- Select questions from the Phase 3 high-priority alternatives
- Focus on questions with strong historical-modern bridges
- Ensure testability with current or near-future technologies
- Vary question types and domains
- Include both immediate feasibility and longer-term visionary questions

---

## PHASE 3 SYNTHESIS:
{phase3_synthesis}

---

Generate {num_questions} research questions following the H-format specified above. Number them H1, H2, H3, etc."""

        else:
            # Use original 13-field format: comprehensive, detailed
            phase4_prompt = self.get_phase4_prompt()

            full_prompt = f"""{phase4_prompt}

---

## TASK: Generate Detailed Research Questions (13-Field Format)

Based on the Phase 3 synthesis below, generate {num_questions} concrete research questions.

**CRITICAL REQUIREMENTS:**
- Each question MUST include ALL 13 fields from the output format above
- Use the exact field structure provided in the example
- Don't omit any fields - every question needs complete specification
- Maintain the historical-modern bridge emphasis throughout
- Address the critical traps explicitly in field 13

**IMPORTANT:**
- Select questions from the Phase 3 high-priority alternatives
- Focus on questions with strong historical-modern bridges
- Ensure testability with current or near-future technologies
- Vary question types (mechanistic, descriptive, clinical, etc.)
- Include both immediate feasibility and longer-term visionary questions

---

## PHASE 3 SYNTHESIS:
{phase3_synthesis}

---

Generate {num_questions} research questions following the EXACT output format specified above. Number them Q1, Q2, Q3, etc."""

        try:
            print("   🔄 Generating questions with Gemini...")
            response = self.model.generate_content(full_prompt)

            if not response.text:
                raise ValueError("Empty response from Gemini model")

            questions_output = response.text

            # Save full output
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(output_dir, f"research_questions_{timestamp}.txt")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(questions_output)

            print(f"   ✅ Generated {len(questions_output):,} characters")
            print(f"   💾 Saved to: {output_file}")

            return {
                "questions_output": questions_output,
                "output_file": output_file,
                "timestamp": timestamp,
                "num_questions": num_questions
            }

        except Exception as e:
            print(f"   ❌ ERROR during question generation: {e}")
            import traceback
            traceback.print_exc()
            raise

    def rank_and_select_questions(
        self,
        questions_output: str,
        top_n: int = 3,
        output_dir: str = "chronos_results/phase4"
    ) -> Dict[str, Any]:
        """
        Rank questions by innovation × testability × impact and select top N.

        Args:
            questions_output: Full questions output from generate_research_questions
            top_n: Number of top questions to select
            output_dir: Directory to save results

        Returns:
            Dictionary with ranked questions
        """
        print(f"\n📊 Ranking questions and selecting top {top_n}...")

        ranking_prompt = f"""## TASK: Rank Research Questions

You are given a set of research questions. Rank them by the formula:

**Score = Innovation × Testability × Impact**

Where:
- **Innovation** (0-10): How novel is the historical-modern bridge? How unique is the approach?
- **Testability** (0-10): How feasible with current/near-future technology? Resource requirements?
- **Impact** (0-10): Potential to change clinical practice or scientific understanding?

For each question, provide:
1. Innovation score (0-10) with brief justification
2. Testability score (0-10) with brief justification
3. Impact score (0-10) with brief justification
4. Overall score (product of the three)

Then list the top {top_n} questions in rank order.

---

## RESEARCH QUESTIONS:
{questions_output}

---

Provide ranking analysis and top {top_n} selections."""

        try:
            print("   🔄 Ranking questions with Gemini...")
            response = self.model.generate_content(ranking_prompt)

            if not response.text:
                raise ValueError("Empty response from Gemini model")

            ranking_output = response.text

            # Save ranking output
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(output_dir, f"question_ranking_{timestamp}.txt")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(ranking_output)

            print(f"   ✅ Ranked questions")
            print(f"   💾 Saved to: {output_file}")

            return {
                "ranking_output": ranking_output,
                "output_file": output_file,
                "timestamp": timestamp,
                "top_n": top_n
            }

        except Exception as e:
            print(f"   ❌ ERROR during ranking: {e}")
            import traceback
            traceback.print_exc()
            raise

    def generate_executive_summary(
        self,
        questions_output: str,
        ranking_output: str,
        output_dir: str = "chronos_results/phase4"
    ) -> Dict[str, Any]:
        """
        Generate executive summary of top research questions for stakeholders.

        Args:
            questions_output: Full questions output
            ranking_output: Ranking analysis
            output_dir: Directory to save results

        Returns:
            Dictionary with summary
        """
        print("\n📋 Generating executive summary...")

        summary_prompt = f"""## TASK: Generate Executive Summary

Create a concise executive summary (2-3 pages) for stakeholders summarizing:

1. **CHRONOS Methodology Overview** (1 paragraph)
   - Brief explanation of the historical-modern bridge approach

2. **Top Research Questions** (1-2 paragraphs each for top 3)
   - The question in plain language
   - Why it matters (clinical/scientific impact)
   - The historical insight that inspired it
   - Feasibility and timeline
   - Required resources

3. **Next Steps** (bullet points)
   - Immediate actions (0-6 months)
   - Short-term goals (6-24 months)
   - Longer-term vision (2-5 years)

4. **Unique Value Proposition**
   - What makes this approach different from standard research?
   - Why mining historical knowledge matters
   - Expected benefits of cross-cultural convergence validation

**Keep it accessible for non-specialists while maintaining scientific rigor.**

---

## RESEARCH QUESTIONS:
{questions_output}

---

## RANKING ANALYSIS:
{ranking_output}

---

Generate the executive summary."""

        try:
            print("   🔄 Generating summary with Gemini...")
            response = self.model.generate_content(summary_prompt)

            if not response.text:
                raise ValueError("Empty response from Gemini model")

            summary_output = response.text

            # Save summary
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(output_dir, f"executive_summary_{timestamp}.txt")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(summary_output)

            print(f"   ✅ Generated executive summary")
            print(f"   💾 Saved to: {output_file}")

            return {
                "summary_output": summary_output,
                "output_file": output_file,
                "timestamp": timestamp
            }

        except Exception as e:
            print(f"   ❌ ERROR during summary generation: {e}")
            import traceback
            traceback.print_exc()
            raise

    def run_phase4(
        self,
        phase3_synthesis: str,
        num_questions: int = 10,
        top_n: int = 3,
        output_dir: str = "chronos_results/phase4",
        use_h_format: bool = True
    ) -> Dict[str, Any]:
        """
        Run complete Phase 4: Generate questions, rank, and create summary.

        Args:
            phase3_synthesis: Phase 3 synthesis output
            num_questions: Number of questions to generate
            top_n: Number of top questions to select
            output_dir: Directory to save results
            use_h_format: If True, use H-format (concise). If False, use 13-field format (detailed)

        Returns:
            Dictionary with all results
        """
        print("\n" + "="*80)
        print("📝 PHASE 4: THE FINAL PRODUCT")
        print("="*80)
        print(f"   Input: Phase 3 synthesis ({len(phase3_synthesis):,} chars)")
        print(f"   Generating {num_questions} detailed research questions")
        print(f"   Format: {'H-format (concise)' if use_h_format else '13-field format (detailed)'}")
        print(f"   Will rank and select top {top_n}")
        print()

        results = {
            "phase": "Phase 4",
            "format": "H-format" if use_h_format else "13-field",
            "questions": None,
            "ranking": None,
            "summary": None
        }

        # Step 1: Generate research questions
        try:
            results["questions"] = self.generate_research_questions(
                phase3_synthesis=phase3_synthesis,
                num_questions=num_questions,
                output_dir=output_dir,
                use_h_format=use_h_format
            )
        except Exception as e:
            print(f"   ⚠️  Question generation failed: {e}")
            return results

        # Step 2: Rank and select top questions
        try:
            results["ranking"] = self.rank_and_select_questions(
                questions_output=results["questions"]["questions_output"],
                top_n=top_n,
                output_dir=output_dir
            )
        except Exception as e:
            print(f"   ⚠️  Ranking failed: {e}")

        # Step 3: Generate executive summary
        if results["questions"] and results["ranking"]:
            try:
                results["summary"] = self.generate_executive_summary(
                    questions_output=results["questions"]["questions_output"],
                    ranking_output=results["ranking"]["ranking_output"],
                    output_dir=output_dir
                )
            except Exception as e:
                print(f"   ⚠️  Executive summary generation failed: {e}")

        print("\n✅ Phase 4 completed!")
        return results


def run_phase4(
    phase3_synthesis: str,
    num_questions: int = 10,
    top_n: int = 3,
    output_dir: str = "chronos_results/phase4",
    use_h_format: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to run Phase 4.

    Args:
        phase3_synthesis: Phase 3 synthesis output
        num_questions: Number of questions to generate
        top_n: Number of top questions to select
        output_dir: Directory to save results
        use_h_format: If True, use H-format (concise). If False, use 13-field format (detailed)

    Returns:
        Dictionary with Phase 4 results
    """
    formulator = Phase4Formulator()

    results = formulator.run_phase4(
        phase3_synthesis=phase3_synthesis,
        num_questions=num_questions,
        top_n=top_n,
        output_dir=output_dir,
        use_h_format=use_h_format
    )

    return results


if __name__ == "__main__":
    # Test Phase 4
    sample_phase3_synthesis = """
    PHASE 3 SYNTHESIS: Distilling to the Essence

    Unique Angles We Can See:
    1. Transient spinal venous congestion - Ollivier's 1824 observation now testable with dynamic MRI
    2. Hormonal-autonomic triggers for spinal symptoms - convergence of Western and Thai observations
    3. Herbal neuromodulation mechanisms - Thai Piper longum linked to modern piperine pharmacology

    High-Priority Alternatives:
    1. [Innovation: 9/10, Testability: 8/10, Impact: 9/10] Imaging study of transient venous congestion
    2. [Innovation: 8/10, Testability: 9/10, Impact: 7/10] Autonomic dysfunction in transient myelopathy
    3. [Innovation: 7/10, Testability: 7/10, Impact: 8/10] Phytochemical analysis of traditional remedies

    Synergistic Combinations:
    - Combine historical venous observation with modern perfusion imaging
    - Link autonomic triggers (sweating, hormonal) to vascular changes
    - Test traditional treatments with modern mechanistic understanding
    """

    print("Testing Phase 4 Formulator...")
    results = run_phase4(sample_phase3_synthesis, num_questions=5, top_n=2, output_dir="test_output/phase4")
    print(f"\nResults: {len([k for k, v in results.items() if v])} components generated")
