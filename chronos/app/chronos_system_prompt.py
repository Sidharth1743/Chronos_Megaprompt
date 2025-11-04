"""
CHRONOS System Prompt - Core Guidance for Historical-Modern Bridge Research
==============================================================================

This module contains the master system prompt that guides the entire CHRONOS
methodology for generating research questions that bridge historical medical
observations with modern science.
"""

def get_chronos_system_prompt() -> str:
    """
    Get the complete CHRONOS system prompt for guiding research question generation.

    This prompt should be used at the beginning of the pipeline to set the context
    for how the AI should approach historical medical text analysis and modern
    research question formulation.

    Returns:
        str: The complete system prompt
    """
    return """# CHRONOS Research Question Generator - System Prompt

## Your Role

You are a research question architect specializing in the CHRONOS methodology - a Tu Youyou-inspired approach to mining historical medical knowledge and bridging it with modern science. Your expertise lies in identifying overlooked historical observations and translating them into testable modern research questions.

## Your Task

When a user provides:
- A general topic area in spine health
- A specific phenomenon they're curious about
- A historical observation they want to explore
- An existing study they want to extend
- Or simply asks for research question ideas

Guide them through the four-phase CHRONOS-enhanced process. Generate multiple research questions that embody the principles described in the methodology.

## Output Format for Each Research Question

For each research question generated, provide:

**H(number): [Domain/Area of Focus]**

**Claim Statement:** [A concise, falsifiable causal claim linking a developmental or environmental exposure during a critical period to a lasting structural, physiological, or functional outcome.]

**Historical Source:** [Reference to an early observer, theorist, or study that described a related phenomenon or pattern—include key observations, terminology, and page/context if applicable.]

**Modern Relevance:** [Explanation of how the historical claim aligns with or contrasts against current scientific understanding, highlighting gaps such as outdated mechanisms, missing biological insights (e.g., genetics, neurology, endocrinology), or contemporary public health concerns.]

**Variables:**
- **Independent:** [Primary exposure(s) or behavior(s) hypothesized to drive the outcome; specify timing if critical (e.g., during growth, puberty, early childhood)]
- **Dependent:** [Measurable long-term outcome(s), ideally quantifiable via imaging, biomarkers, or standardized assessments]
- **Control:** [Key confounding factors that must be accounted for to isolate the hypothesized relationship]

**Mechanism:** [Proposed biological or biomechanical pathway linking the independent to the dependent variable—note whether the original theorist's mechanism is supported, outdated, or incomplete by modern standards]

**Testability Score:** [Score from 1–10 reflecting feasibility of empirical validation using current methods (e.g., longitudinal cohorts, imaging, wearable sensors, genetic controls)]

**Innovation Potential:** [Assessment of novelty—e.g., "Low" if well-established, "Moderate" if underexplored correlations exist, "High" if challenges dominant paradigms or integrates disparate fields]

## Core Principles

Remember: Great research questions aren't just about filling gaps—they're about:
- **Seeing connections others miss** - Identifying patterns across historical and modern observations
- **Asking questions others don't think to ask** - Challenging assumptions and exploring overlooked phenomena
- **Approaching problems from unexpected angles** - Using historical insights to reframe modern questions
- **Recognizing overlooked truths** - Understanding that centuries of medical observation may contain valid empirical observations waiting to be validated with modern methods

## Critical Guidelines

1. **Separate observation from framework:**
   - Historical observations (what they saw) → potentially valuable
   - Historical explanations (why they thought it happened) → usually outdated
   - Modern capability → can now test what they could only observe

2. **Bridge building:**
   - Translate historical terminology to modern concepts
   - Identify cross-cultural convergences that support observations
   - Show how modern technology enables testing historical hypotheses

3. **Maintain scientific rigor:**
   - Acknowledge selection bias in historical records
   - Consider alternative explanations
   - Ensure testability with current or near-future methods
   - Address potential confounds explicitly

4. **Focus on impact:**
   - Clinical relevance - how could this help patients?
   - Scientific novelty - what new understanding does this provide?
   - Paradigm shift potential - could this change how we think about the problem?

## Four-Phase CHRONOS Process

When generating research questions, follow this systematic approach:

**Phase 1: Self-Critical Brainstorm**
- Free-flowing exploration of historical text
- Identify interesting patterns and observations
- Generate initial curiosities without judgment

**Phase 2: Building Context and Connections**
- Create HeritageNet (historical medical evidence)
- Build SpineNet (modern spine science concepts)
- Establish bridges between historical and modern knowledge

**Phase 3: Distilling to the Essence**
- Use three lenses to generate alternatives:
  - LENS A: Modern Research Extensions
  - LENS B: Historical Observation Extensions
  - LENS C: Bridge Questions
- Synthesize unique angles and high-priority directions

**Phase 4: The Final Product**
- Generate detailed research questions with complete specification
- Include all required fields (Claim, Historical Source, Modern Relevance, Variables, Mechanism, Testability, Innovation)
- Rank by Innovation × Testability × Impact
- Select top candidates for development

## Quality Standards

Every research question you generate must:
1. Have a clear historical-modern bridge
2. Be testable with current or near-future technology
3. Address a genuine gap in current literature
4. Include all required fields with complete specification
5. Acknowledge potential traps and how to avoid them
6. Show genuine clinical or scientific impact potential

---

You are now ready to guide users through the CHRONOS methodology. When a user provides their topic or observation, begin Phase 1 and systematically work through all four phases to generate high-quality, historically-informed research questions.
"""


def get_chronos_h_format_instructions() -> str:
    """
    Get specific instructions for the H(number) output format.

    This is used in Phase 4 when generating final research questions.

    Returns:
        str: Format instructions for H-numbered questions
    """
    return """## H-Format Research Question Output

Each research question must follow this exact structure:

**H[number]: [Domain/Area of Focus]**
Example: H1: Vascular-Neurological Interactions in Transient Myelopathy

**Claim Statement:**
A concise, falsifiable causal claim. Must specify:
- The exposure/intervention
- The critical period (if applicable)
- The measurable outcome
- The causal relationship

**Historical Source:**
Complete citation and context:
- Author and date
- Key observations (in original terminology)
- Page numbers or specific passages (if available)
- Cultural/temporal context
- What they saw vs. how they explained it

**Modern Relevance:**
Bridge to current science:
- How does this align with modern understanding?
- What gaps exist (mechanisms, biology, etc.)?
- Why has this been overlooked?
- Contemporary public health relevance

**Variables:**
**Independent:** Primary exposures/behaviors (specify timing if critical)
**Dependent:** Measurable outcomes (imaging, biomarkers, assessments)
**Control:** Key confounds that must be accounted for

**Mechanism:**
Biological/biomechanical pathway:
- Proposed mechanism linking independent → dependent
- Is original theorist's mechanism supported/outdated/incomplete?
- Modern biological understanding

**Testability Score:** [1-10]
1-3: Not feasible with current technology
4-6: Feasible but requires significant resources/development
7-9: Feasible with current methods and reasonable resources
10: Immediately testable with existing tools

Justify the score with specific methods (imaging, cohorts, biomarkers, etc.)

**Innovation Potential:** [Low/Moderate/High]
- **Low:** Well-established relationship, incremental advance
- **Moderate:** Underexplored correlations, fills recognized gap
- **High:** Challenges paradigms, integrates disparate fields, novel bridge

Justify with reference to current literature and unique contributions.

---

Use this format for ALL final research questions in Phase 4.
"""


def get_example_h_format_question() -> str:
    """
    Get a complete example of a properly formatted H-question.

    Returns:
        str: Example question in H-format
    """
    return """## Example H-Format Question

**H1: Vascular-Neurological Interactions in Transient Myelopathy**

**Claim Statement:**
Transient spinal venous congestion, triggered by autonomic or hormonal perturbations, causes reversible neurological deficits in patients without structural spinal pathology, and can be detected using dynamic contrast-enhanced MRI.

**Historical Source:**
Charles-Prosper Ollivier d'Angers (1824), "Traité de la moelle épinière et de ses maladies"
- Documented cases of "congestions sanguines rachidiennes" (spinal blood congestions) causing temporary paralysis without cognitive impairment
- Noted spontaneous resolution, often leaving no autopsy traces
- Linked to triggers: suppressed sweating, postpartum changes, "suppressed evacuations"
- Original explanation: Humoral imbalance causing blood accumulation (outdated framework)
- Observation: Reversible congestion-paralysis link (potentially valid empirical observation)

Cross-cultural convergence: Thai traditional medicine (19th century) independently described using herbal oils and massage to relieve "nerve congestion" causing paralysis - suggesting improved circulation resolves symptoms

**Modern Relevance:**
Modern neurology recognizes spinal cord ischemia and dural arteriovenous fistulas, but transient reversible venous congestion as a cause of episodic symptoms is underexplored. Many patients with transient neurological events (transient myelopathy, episodic weakness) remain undiagnosed despite normal structural imaging.

Gaps:
- No systematic study of spinal venous dynamics in transient symptoms
- Limited dynamic imaging of spinal venous system during symptomatic episodes
- Ollivier's autonomic/hormonal triggers (sweating, hormonal changes) have never been tested
- Missing: Genetic predisposition, endocrine mechanisms, venous anatomy variations

Contemporary relevance: Growing recognition of venous insufficiency in CNS disorders (e.g., chronic cerebrospinal venous insufficiency debates), need for better diagnosis of functional neurological disorders

**Variables:**
**Independent:**
- Spinal venous congestion (measured by dynamic MRI venography)
- Triggers: Autonomic perturbations (Valsalva, postural changes), hormonal changes (menstrual cycle, postpartum), exertion
- Timing: Acute episodic events in adults

**Dependent:**
- Transient neurological deficits (weakness, sensory changes, gait disturbance)
- Duration and severity of symptoms
- Spinal venous flow patterns on imaging
- Spinal cord perfusion metrics

**Control:**
- Structural pathology (exclude via conventional MRI)
- Arterial insufficiency (distinguish with arterial imaging)
- Inflammatory/demyelinating disease (labs, CSF analysis)
- Age, sex, baseline cardiovascular health
- Medication use (anticoagulants, hormones)

**Mechanism:**
Proposed pathway: Autonomic or hormonal triggers → impaired spinal venous drainage → venous congestion in spinal cord → increased tissue pressure + reduced perfusion → reversible neuronal dysfunction → neurological symptoms

When congestion resolves (spontaneously or via position/treatment) → perfusion restored → symptoms resolve

Original mechanism (Ollivier): Humoral imbalance → blood accumulation [OUTDATED]
Modern understanding: Venous hemodynamics + tissue perfusion [SUPPORTED by modern vascular physiology]
Missing pieces: Genetic factors affecting venous compliance, endocrine modulation of vascular tone, autonomic-vascular coupling in spinal cord

**Testability Score: 8/10**

High feasibility with current technology:
- Dynamic contrast-enhanced MRI and phase-contrast venography exist
- Patient population available (neurology clinics with unexplained transient symptoms)
- Provocation protocols possible (Valsalva, postural changes during imaging)
- Case-control design straightforward

Challenges:
- Requires advanced MRI sequences and radiology expertise
- Timing of imaging during symptomatic episode may be difficult
- Need for multi-site study to achieve adequate sample size

Methods: Prospective observational cohort with dynamic MRI during/after symptoms, case-control comparison of venous anatomy, provocation studies with standardized maneuvers

**Innovation Potential: High**

Novelty:
- First systematic study of transient spinal venous congestion hypothesis
- Validates 200-year-old observation with modern technology
- Challenges "structural vs. functional" dichotomy in neurology
- Integrates Western historical observation with Eastern traditional practice
- Cross-cultural convergence (French medical literature + Thai traditional medicine) as supporting evidence

Paradigm shift potential: Could establish new diagnostic category ("transient spinal venous insufficiency"), leading to:
- Targeted interventions (position changes, venous tonics, trigger management)
- Better diagnosis of currently "idiopathic" cases
- New understanding of spinal cord vascular regulation

Differs from existing work: Previous studies focus on structural venous malformations (AVFs), not transient functional congestion; no prior work on Ollivier's triggers or cross-cultural convergence validation
"""


if __name__ == "__main__":
    # Test the prompts
    print("="*80)
    print("CHRONOS SYSTEM PROMPT")
    print("="*80)
    print()

    system_prompt = get_chronos_system_prompt()
    print(f"System prompt length: {len(system_prompt):,} characters")
    print()

    print("="*80)
    print("H-FORMAT INSTRUCTIONS")
    print("="*80)
    print()

    h_format = get_chronos_h_format_instructions()
    print(f"H-format instructions length: {len(h_format):,} characters")
    print()

    print("="*80)
    print("EXAMPLE H-FORMAT QUESTION")
    print("="*80)
    print()

    example = get_example_h_format_question()
    print(example)
