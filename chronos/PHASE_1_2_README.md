# CHRONOS Refined Pipeline - Phase 1 & 2 Implementation

## Overview

This document describes the **Refined CHRONOS Pipeline** (Choice 3 in main.py), which implements the proper multi-phase CHRONOS methodology for mining historical medical knowledge.

### Current Implementation Status

✅ **Phase 1: Self-Critical Brainstorm** - COMPLETE
✅ **Phase 2: Building Context and Connections** - COMPLETE
⏳ **Phase 3: Distilling to the Essence** - PENDING
⏳ **Phase 4: Formulating Testable Hypotheses** - PENDING
⏳ **FutureHouse Verification** - PENDING

---

## Architecture

### Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CHRONOS REFINED PIPELINE                          │
└─────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐
    │   INPUT     │
    │  PDF/Image  │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  OCR ENGINE │  ← ocr_engine.py
    │   (Gemini)  │
    └──────┬──────┘
           │
           │ Extracted Text
           ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                        PHASE 1                                   │
    │              Self-Critical Brainstorm                           │
    │  ┌────────────────────────────────────────────────────────┐    │
    │  │  • Free-flowing exploration                            │    │
    │  │  • Question assumptions                                │    │
    │  │  • Identify sparks and patterns                        │    │
    │  │  • Stream-of-consciousness documentation              │    │
    │  └────────────────────────────────────────────────────────┘    │
    │                                                                  │
    │  Output: phase1_brainstorm.txt                                  │
    └──────┬───────────────────────────────────────────────────────────┘
           │
           │ Phase 1 Ideas + OCR Text
           ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                        PHASE 2                                   │
    │           Building Context and Connections                      │
    │  ┌────────────────────────────────────────────────────────┐    │
    │  │  DOMAIN 1: HeritageNet (Historical Medical Evidence)   │    │
    │  │  • Historical observations (empirical)                 │    │
    │  │  • Historical treatments                               │    │
    │  │  • Historical frameworks (theoretical)                 │    │
    │  │  • Cross-cultural convergences                         │    │
    │  │  • Source texts                                        │    │
    │  └────────────────────────────────────────────────────────┘    │
    │                           │                                      │
    │                           ▼                                      │
    │  ┌────────────────────────────────────────────────────────┐    │
    │  │  DOMAIN 2: SpineNet (Modern Spine Science)             │    │
    │  │  • Modern concepts                                     │    │
    │  │  • Modern mechanisms                                   │    │
    │  │  • Modern evidence                                     │    │
    │  │  • Modern technology                                   │    │
    │  │  • Research gaps                                       │    │
    │  │  • Patient phenotypes                                  │    │
    │  │  • Interdisciplinary insights                          │    │
    │  └────────────────────────────────────────────────────────┘    │
    │                           │                                      │
    │                           ▼                                      │
    │  ┌────────────────────────────────────────────────────────┐    │
    │  │  BRIDGE DOMAIN (Historical-Modern Connections)         │    │
    │  │  • Conceptual translations                             │    │
    │  │  • Mechanism reframing                                 │    │
    │  │  • Treatment translations                              │    │
    │  │  • Convergence patterns                                │    │
    │  │  • Hypothesis seeds                                    │    │
    │  └────────────────────────────────────────────────────────┘    │
    │                                                                  │
    │  Output: phase2_summary.txt + Neo4j Knowledge Graph            │
    └──────┬───────────────────────────────────────────────────────────┘
           │
           ▼
    ┌─────────────┐
    │   PHASE 3   │  ⏳ PENDING
    │  (Future)   │
    └─────────────┘
```

---

## File Structure

```
chronos/app/
├── phase1_brainstorm.py          # Phase 1: Self-Critical Brainstorm
├── phase2_context_builder.py     # Phase 2: Context Building
├── KGAgents.py                    # HeritageNet KG Agent (historical extraction)
├── chronos_kg_agent.py            # SpineNet/Bridge KG Agent (CHRONOS-specific)
├── pipeline_selector.py           # Pipeline orchestration (updated)
├── main.py                        # Entry point (updated)
├── ocr_engine.py                  # OCR extraction (Gemini)
└── ...

chronos_results/
├── phase1/
│   ├── phase1_brainstorm_YYYYMMDD_HHMMSS.txt
│   └── phase1_metadata_YYYYMMDD_HHMMSS.txt
└── phase2/
    ├── phase2_summary_YYYYMMDD_HHMMSS.txt
    └── phase2_metadata_YYYYMMDD_HHMMSS.txt
```

---

## Phase 1: Self-Critical Brainstorm

### Purpose
Generate free-flowing exploration of spine health phenomena from historical medical text.

### Implementation: `phase1_brainstorm.py`

#### Key Components

1. **Phase1Brainstorm Class**
   - Uses Gemini 2.0 Flash Exp
   - Temperature: 0.8 (high for creative exploration)
   - Implements full CHRONOS megaprompt + Phase 1 instructions

2. **Core Methods**
   - `generate_brainstorm(ocr_text)`: Generate brainstorm from OCR text
   - `generate_and_save(ocr_text, output_dir)`: Generate and save with metadata

3. **Prompting Strategy**
   ```
   CHRONOS Megaprompt (Core Philosophy)
   +
   Phase 1 Specific Instructions
   +
   Historical Medical Text
   ```

#### Output Format

**phase1_brainstorm_YYYYMMDD_HHMMSS.txt:**
```
[Free-flowing brainstorm including:]
- Identified sparks (captivating phenomena)
- Free-form connections and explorations
- Self-critique dialogue (assumptions, skeptics, opposites)
- Stream-of-consciousness documentation
- Clinical observations and contradictions
- Emerging technologies and patient populations
```

**phase1_metadata_YYYYMMDD_HHMMSS.txt:**
```
timestamp: 20241024_143022
input_length: 45632
output_length: 8912
output_file: chronos_results/phase1/phase1_brainstorm_20241024_143022.txt
phase: Phase 1 - Self-Critical Brainstorm
```

---

## Phase 2: Building Context and Connections

### Purpose
Create rich, interconnected knowledge map bridging historical and modern domains.

### Implementation: `phase2_context_builder.py`

#### Key Components

1. **Phase2ContextBuilder Class**
   - Orchestrates HeritageNet + SpineNet + Bridges
   - Manages Neo4j knowledge graph storage
   - Generates Phase 2 summary

2. **Two-Domain Architecture**

   **DOMAIN 1: HeritageNet (Historical Medical Evidence)**
   - Agent: `KGAgents.py` (standard historical extraction)
   - Extracts from: OCR text of historical documents
   - Node Types:
     - `ClinicalObservation`: Signs, symptoms, presentations
     - `TherapeuticOutcome`: Treatment responses, recovery
     - `ContextualFactor`: Environmental, behavioral factors
     - `MechanisticConcept`: Traditional explanatory models
     - `TherapeuticApproach`: Interventions, remedies
     - `SourceText`: Original documents, authors

   **DOMAIN 2: SpineNet + Bridges**
   - Agent: `chronos_kg_agent.py` (CHRONOS-specific bridges)
   - Extracts from: Phase 1 brainstorm + Historical context
   - Node Types:
     - **SpineNet Nodes:**
       - `ModernConcept`: Current scientific understanding
       - `ModernMechanism`: Contemporary biological explanations
       - `ModernEvidence`: Supporting/contradicting research
       - `ModernTechnology`: Imaging, measurement capabilities
       - `ResearchGap`: Unexplored historical insights
       - `PatientPhenotype`: Clinical subtypes
       - `InterdisciplinaryInsight`: Cross-field transfers
     - **Bridge Nodes:**
       - `ConceptualTranslation`: Historical → Modern mapping
       - `MechanismReframing`: Outdated → Current mechanism
       - `TreatmentTranslation`: Traditional → Modern analog
       - `ConvergencePattern`: Cross-cultural + modern validation
       - `HypothesisSeed`: Emergent testable ideas
       - `ContradictionNode`: Historical-modern tensions

3. **Relationship Types**
   - **Connection Type 1:** `translates_to_modern_concept`
   - **Connection Type 2:** `reframes_as_mechanism`, `outdated_framework_for`
   - **Connection Type 3:** `has_modern_analog`, `shares_principle_with`
   - **Connection Type 4:** `converges_with`, `corroborates`
   - **Connection Type 5:** `supported_by_modern_evidence`, `has_research_gap`, `tested_by_modern_method`
   - **Observational:** `described_in`, `co_occurs_with`, `treated_with`, `results_in`
   - **Enhanced:** `sparks`, `resolves`, `applies_method_from`, `borrows_principle_from`

4. **Core Methods**
   - `build_heritagenet(ocr_text)`: Extract historical knowledge graph
   - `build_spinenet_and_bridges(phase1_brainstorm, ocr_text)`: Extract modern concepts and bridges
   - `generate_phase2_summary(phase1_brainstorm)`: Generate textual summary
   - `run_phase2()`: Complete Phase 2 pipeline

#### Knowledge Graph Storage

**Neo4j Database:** `chronos`

**Graph Structure:**
```cypher
// Example nodes and relationships in Neo4j

// HeritageNet nodes
(obs:ClinicalObservation {id: 'spinal_blood_congestion_paralysis'})
(treat:TherapeuticApproach {id: 'herbal_oil_massage'})
(source:SourceText {id: 'ollivier_1824'})

// SpineNet nodes
(modern:ModernConcept {id: 'spinal_cord_venous_drainage'})
(gap:ResearchGap {id: 'transient_venous_congestion_imaging'})

// Bridge nodes
(bridge:ConceptualTranslation {id: 'congestion_to_venous_engorgement'})

// Relationships
(obs)-[:described_in]->(source)
(obs)-[:translates_to_modern_concept]->(bridge)
(bridge)-[:translates_to_modern_concept]->(modern)
(obs)-[:has_research_gap]->(gap)
```

#### Output Format

**phase2_summary_YYYYMMDD_HHMMSS.txt:**
```
[Structured Phase 2 analysis including:]
1. HeritageNet Mapping: Historical observations related to Phase 1 ideas
2. SpineNet Connections: Modern spine science concepts
3. Bridge Analysis: Explicit historical-modern connections
4. Research Gaps: Where modern research could test historical insights
5. Cross-Cultural Convergence: Cross-cultural patterns
```

**Neo4j Knowledge Graph:**
- Accessible via http://localhost:7474
- Database: `chronos`
- Use Cypher queries to explore relationships

---

## Usage

### Running the Refined Pipeline

1. **Start the pipeline:**
   ```bash
   cd chronos/app
   python main.py
   ```

2. **Select Choice 3:**
   ```
   Enter your choice (1, 2, or 3): 3
   ```

3. **Configure input file** (in main.py):
   ```python
   INPUT_FILE = "/path/to/your/historical_medical_document.pdf"
   OUTPUT_TEXT_FILE = "/path/to/output.txt"
   ```

4. **Pipeline execution:**
   - OCR extraction (Gemini)
   - Phase 1: Self-Critical Brainstorm
   - Phase 2: Building Context and Connections
     - HeritageNet extraction
     - SpineNet + Bridges extraction
     - Phase 2 summary generation

5. **Review results:**
   - Phase 1: `chronos_results/phase1/`
   - Phase 2: `chronos_results/phase2/`
   - Neo4j: http://localhost:7474 (database: `chronos`)

### Example Neo4j Queries

**Find all historical observations:**
```cypher
MATCH (n:ClinicalObservation)
RETURN n
LIMIT 25
```

**Find historical-modern bridges:**
```cypher
MATCH (h:HistoricalObservation)-[r:translates_to_modern_concept]->(b:ConceptualTranslation)-[]->(m:ModernConcept)
RETURN h, r, b, m
```

**Find research gaps:**
```cypher
MATCH (obs)-[:has_research_gap]->(gap:ResearchGap)
RETURN obs, gap
```

**Find cross-cultural convergences:**
```cypher
MATCH (c:CrossCulturalEvidence)-[:corroborates]->(obs)
RETURN c, obs
```

**Find all bridges from a specific historical observation:**
```cypher
MATCH (h {id: 'spinal_blood_congestion_paralysis'})-[r*1..3]->(m:ModernConcept)
RETURN h, r, m
```

---

## Configuration

### Environment Variables (.env)

```bash
# Required
GOOGLE_API_KEY=your-gemini-api-key

# Neo4j Configuration
NEO4J_URL=neo4j://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password

# Optional
CHRONOS_MODEL=gemini-2.0-flash-exp
```

### Pipeline Settings (main.py)

```python
# OCR Settings
OCR_CONFIG = {
    "ocr_preprocessing": True,
    "enhancement_level": "aggressive",  # light/medium/aggressive
    "use_high_dpi": True,
    "use_advanced_ocr": True,
    "medical_context": True,
    "save_debug_images": True,
    "try_native_text": True
}

# Knowledge Graph Settings
KG_CONFIG = {
    "use_advanced_kg": False,
    "kg_chunk_size": 10000,       # Adjust for large documents
    "enable_chunking": True,
    "element_id": "your_doc_id"
}
```

---

## Key Design Principles

### 1. Separation of Observations from Explanations
**Critical for CHRONOS methodology:**
- Historical **observations** (what they saw) → May be valid
- Historical **explanations** (why they thought it happened) → Often outdated
- Bridge nodes make this separation explicit

**Example:**
```
HistoricalObservation: "spinal_blood_congestion_paralysis"
  (What Ollivier observed - potentially valid)
     ↓
     translates_to_modern_concept
     ↓
ConceptualTranslation: "congestion_to_reversible_venous_engorgement"
  (Bridge node - explicit mapping)
     ↓
     translates_to_modern_concept
     ↓
ModernConcept: "spinal_cord_venous_drainage"
  (Current scientific understanding)

HistoricalFramework: "humoral_imbalance_theory"
  (How Ollivier explained it - outdated)
     ↓
     outdated_framework_for
     ↓
HistoricalObservation: "spinal_blood_congestion_paralysis"
  (Links obsolete theory to valid observation)
```

### 2. Descriptive Semantic Node IDs
**Never use generic counters!**

❌ **BAD:**
```
Node(id='historical_observation_1', type='HistoricalObservation')
Node(id='research_gap_2', type='ResearchGap')
```

✅ **GOOD:**
```
Node(id='spinal_blood_congestion_paralysis', type='HistoricalObservation')
Node(id='transient_venous_congestion_imaging', type='ResearchGap')
```

**Construction Rules:**
- Use lowercase with underscores (snake_case)
- Include key concepts (3-6 words)
- Make it unique and recognizable
- For source texts: `author_year` or `tradition_century`
- For translations: `historical_and_modern` concepts
- For treatments: `remedy_and_condition`

### 3. Cross-Cultural Convergence
**Increases plausibility:**
```
Western observation (Ollivier, 1824):
  "Spinal blood congestion → paralysis"
     +
Eastern observation (Thai medicine):
  "Similar paralysis treated with herbal oils"
     =
CrossCulturalEvidence: "western_thai_paralysis_convergence"
```

### 4. Research Gap Identification
**Modern technology can now test what historical physicians only observed:**
```
HistoricalObservation: "transient_paralysis_from_congestion"
  (1824 - only observable at autopsy)
     ↓
     has_research_gap
     ↓
ResearchGap: "transient_myelopathy_imaging_gap"
     ↓
     tested_by_modern_method
     ↓
ModernTechnology: "dynamic_spinal_mri"
  (2024 - can now visualize in living patients)
```

---

## Troubleshooting

### Common Issues

**1. "GOOGLE_API_KEY not found"**
```bash
# Add to .env file
GOOGLE_API_KEY=your-key-here
```

**2. "Could not connect to Neo4j"**
```bash
# Check Neo4j is running
neo4j status

# Start Neo4j
neo4j start

# Verify connection
neo4j-admin status
```

**3. "Phase 2 failed: database parameter error"**
- Phase 2 will fallback to default database
- Knowledge graph will still be created
- May need to use CHRONOS_ prefix for queries

**4. "Empty graph extraction"**
- Check if OCR text is too short (< 100 chars)
- Verify Gemini API key is valid
- Try reducing `kg_chunk_size` to 8000

**5. "Out of memory during KG extraction"**
- Reduce `kg_chunk_size` in main.py
- Enable chunking: `enable_chunking=True`
- Process document in smaller sections

---

## Next Steps (Phase 3 & 4)

### Phase 3: Distilling to the Essence
**Goal:** Synthesize Phase 2 knowledge into core insights

**Planned Implementation:**
- Query Neo4j for high-value bridges
- Identify strongest historical-modern connections
- Rank by: cross-cultural convergence, modern evidence, research gap impact
- Generate consolidated insights

### Phase 4: Formulating Testable Hypotheses
**Goal:** Convert insights into testable research questions

**Planned Implementation:**
- Transform Phase 3 insights into PICO format
- Score by: innovation × testability
- Select top 2-5 questions
- Format for FutureHouse verification

### FutureHouse Verification
**Goal:** Validate hypotheses against scientific literature

**Planned Implementation:**
- Submit top questions to FutureHouse API
- Receive evidence-based verification
- Save verification reports
- Iterate based on feedback

---

## Development Notes

### Code Quality Standards

1. **Type Hints:** All functions have type hints
2. **Docstrings:** Google-style docstrings for all classes/methods
3. **Error Handling:** Try-except blocks with informative messages
4. **Logging:** Print statements with emoji indicators for clarity
5. **Modularity:** Each phase is self-contained module

### Testing Strategy

1. **Unit Tests:** Test individual phase modules
   ```python
   python phase1_brainstorm.py  # Test Phase 1
   python phase2_context_builder.py  # Test Phase 2
   ```

2. **Integration Tests:** Test full pipeline with sample data

3. **Manual Testing:** Run with real historical medical documents

### Performance Considerations

1. **Chunking:** Automatically handles large documents
2. **Model Selection:** Gemini 2.0 Flash Exp for cost-effectiveness
3. **Temperature Tuning:**
   - Phase 1: 0.8 (creative exploration)
   - Phase 2: 0.5 (balanced mapping)
   - KG Extraction: 0.3 (precise extraction)

---

## Credits

**CHRONOS Methodology:** Following Tu Youyou's approach to mining traditional medicine (artemisinin discovery)

**Knowledge Graph Framework:** CAMEL-AI.org (Apache License 2.0)

**OCR Engine:** Google Gemini 2.0 Flash Exp

**Graph Database:** Neo4j

---

## License

This implementation follows the CHRONOS methodology as defined in prompt.md and integrates with the existing telegram-bot project structure.

---

## Contact & Support

For questions about the CHRONOS refined pipeline:
1. Review this README
2. Check `prompt.md` for methodology details
3. Inspect phase module docstrings
4. Review Neo4j graph structure

**Key Files for Understanding:**
- `prompt.md`: Complete CHRONOS methodology
- `phase1_brainstorm.py`: Phase 1 implementation
- `phase2_context_builder.py`: Phase 2 implementation
- `chronos_kg_agent.py`: Knowledge graph extraction logic
- `KGAgents.py`: HeritageNet extraction (base agent)

---

**Last Updated:** 2024-10-24
**Version:** 1.0.0 (Phase 1 & 2 Complete)
**Status:** ✅ Production Ready (Phase 1-2) | ⏳ Phase 3-4 Pending
