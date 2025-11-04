"""
Phase 2: Building Context and Connections
==========================================

Takes OCR text + Phase 1 brainstorm and builds:
1. HeritageNet (Historical Medical Evidence)
2. SpineNet (Modern Spine Science concepts from Phase 1 ideas)
3. Bridges (Historical-Modern connections)

All using the Phase 2 prompt directly with Gemini.
"""

import os
import google.generativeai as genai
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from pathlib import Path
from datetime import datetime
from camel.loaders import UnstructuredIO
from camel.storages import Neo4jGraph
from camel.storages.graph_storages.graph_element import GraphElement, Node, Relationship
import re
from gemini_rate_limiter import get_rate_limiter, rate_limited_request

if TYPE_CHECKING:
    from unstructured.documents.elements import Element


class Phase2ContextBuilder:
    """
    Phase 2: Building Context and Connections

    Maps Phase 1 ideas to HeritageNet and SpineNet, creating explicit bridges.
    """

    def __init__(
        self,
        neo4j_url: str = "neo4j://127.0.0.1:7687",
        neo4j_username: str = "neo4j",
        neo4j_password: str = "0123456789",
        neo4j_database: str = "chronos",
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash-exp"
    ):
        """Initialize Phase 2 Context Builder."""
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = self._configure_model(model)

        # Configure Neo4j
        self.neo4j_database = neo4j_database
        self.n4j_graph = self._configure_neo4j(
            neo4j_url, neo4j_username, neo4j_password, neo4j_database
        )

        print(f"✅ Phase 2 Context Builder initialized")
        print(f"   - Database: {neo4j_database}")
        print(f"   - Model: {model}")

    def _configure_model(self, model_name: str):
        """Configure Gemini model for Phase 2."""
        generation_config = {
            "temperature": 0.5,
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

    def _configure_neo4j(self, url: str, username: str, password: str, database: str) -> Neo4jGraph:
        """Configure Neo4j database connection."""
        print(f"🔌 Connecting to Neo4j database ({database})...")

        try:
            n4j = Neo4jGraph(
                url=url,
                username=username,
                password=password,
                database=database
            )
            print("✅ Neo4j connection established!")
            return n4j
        except Exception as e:
            print(f"⚠️  Warning: Could not connect with database parameter: {e}")
            print("   Trying default connection...")
            n4j = Neo4jGraph(url=url, username=username, password=password)
            print("✅ Neo4j connection established (using default database)")
            return n4j

    def get_phase2_prompt(self) -> str:
        """Get the Phase 2 prompt."""
        return """### **PHASE 2: Building Context and Connections**

**Goal:** Create a rich, interconnected knowledge map that deliberately bridges **TWO separate knowledge domains**:

#### **DOMAIN 1: HeritageNet (Historical Medical Evidence)**

This knowledge graph is **GIVEN** to you. It contains:
- Historical observations from diverse medical traditions
- Original terminology and theoretical frameworks
- Documented treatments and outcomes
- Cross-cultural observations and convergences

**Your task with HeritageNet:** READ and UNDERSTAND the historical observations, recognizing:
- Empirical observations (what physicians actually saw/experienced)
- Theoretical interpretations (how they explained it in their era's terms)
- Treatment approaches and reported outcomes
- Patterns across different historical sources

#### **DOMAIN 2: Modern Spine Science (SpineNet)**

This is where your deep literature work happens. Build comprehensive understanding of:

**Modern Spine Literature - Core Fields:**
- **Biomechanics & engineering:** robotics, materials science, finite element modeling, tissue mechanics
- **Neuroscience:** pain processing, neuroplasticity, central sensitization, proprioception, motor control
- **Cellular/molecular biology:** disc degeneration mechanisms, inflammation, tissue healing, mechanobiology
- **Psychology:** catastrophizing, fear-avoidance, placebo effects, pain psychology
- **Rehabilitation sciences:** motor control, movement patterns, exercise physiology
- **Clinical sciences:** diagnosis, treatment effectiveness, prognostic factors, phenotyping
- **Data science:** machine learning for imaging, wearables, predictive modeling
- **Philosophy of science:** diagnostic frameworks, what counts as "dysfunction"
- **Sociology & health equity:** access to care, cultural differences, social determinants
- **Evolutionary biology:** bipedalism adaptations, why humans have spine problems

**Reading Strategy for SpineNet:**
- **Deep dive into spine literature:**
  - Tag papers as 'primary' (directly relevant) or 'secondary' (tangentially related)
  - Note methodological approaches, control conditions, populations studied
  - Identify gaps, contradictions, and unexplored territories
  - Look for papers that almost asked your question
- **Wide interdisciplinary reading:** Actively seek connections to:
  - Fields you listed above PLUS:
    - **Vascular medicine:** venous drainage, microcirculation, ischemia
    - **Gastroenterology:** microbiome, gut-brain axis, visceral-somatic interactions
    - **Endocrinology:** hormonal influences on inflammation, tissue repair
    - **Pharmacology:** neurotransmitter systems, drug delivery, herbal medicine
    - **Immunology:** neuroinflammation, neuroimmune pathways
    - **Materials science:** for understanding tissue properties
    - **Traditional medicine research:** phytochemistry, ethnopharmacology
- **Spot hidden connections:** Look for problems in distant fields that share the same underlying 'shape':
  - Network analysis from social sciences revealing patterns in multifactorial spine pain
  - Microbiome methods from GI research applied to disc microbiology
  - Venous insufficiency research from neurology applied to spinal circulation
  - Plant pharmacology databases connecting to neuromodulation
- **Maintain detailed reasoning:** Track nascent thoughts, emerging connections, questions that arise

#### **THE CRITICAL BRIDGE: Historical-Modern Mapping**

This is where **CHRONOS magic happens.** Your goal is to create explicit connections between HeritageNet and the modern literature:

**Connection Type 1: Conceptual Translation**
Map historical terminology to modern concepts. For example:
- "Spinal blood congestion" (Ollivier, 1824) → reversible spinal venous engorgement, microcirculatory impairment
- "Suppressed evacuations" → neuroendocrine dysregulation, hormonal influences on neurological function
- "Wind element imbalance" (Thai medicine) → autonomic dysfunction, inflammatory states
- "Nerve stiffness" → neural fibrosis, reduced nerve mobility, fascial restrictions
- "Hardened nerves" → perineural scarring, fibrotic changes

**Connection Type 2: Mechanism Reframing**
Historical mechanism (outdated framework) → Modern mechanism (current understanding):
- Humoral "suppressed evacuations" → hormonal/autonomic triggers for vascular changes
- "Drawing blood away from spine" via blistering → modern concepts of referred pain, counter-irritation, neuroplastic changes
- "Elemental balance" → systemic inflammatory/metabolic states
- "Nerve congestion" from herbal oils → improved microcirculation, anti-inflammatory effects

**Connection Type 3: Treatment Translation**
Historical treatment → Modern analog/mechanism:
- Strychnine for paralysis → glycine receptor modulation, spinal cord neuromodulation
- Hydrocyanic acid for convulsions → GABAergic/glycinergic inhibitory enhancement
- Herbal stimulants (Piper longum) → pharmacological neurostimulation, piperine effects
- Herbal compresses → thermotherapy + transdermal phytochemical delivery
- Bloodletting for congestion → venous drainage optimization (non-invasive)

**Connection Type 4: Cross-Cultural Convergence**
Identify when different traditions noted similar phenomena (increases plausibility):
- Ollivier (French, 1824) + Thai manuscript (19th c.) BOTH noted transient vascular phenomena causing paralysis
- Western strychnine use + Eastern stimulant herbs (Piper longum) for similar indications
- Suppressed bodily functions (Western "evacuations") + elemental imbalance (Eastern) both pointing to systemic factors

**Connection Type 5: Modern Evidence Links**
For each historical observation, identify:
- Modern supporting evidence (e.g., microbiome studies supporting Ollivier's gut-spine observations)
- Modern contradicting evidence
- Gaps where modern research hasn't adequately explored the historical observation
- Technologies that could now rigorously test historical hypotheses

**CRITICAL: Avoid These Traps in Phase 2**
- Don't dismiss historical observations because the theoretical framework is outdated
- Don't conflate creating the knowledge graph (separate procedure) with using it for hypothesis generation
- Don't assume HeritageNet is complete - note where historical sources might have gaps
- Don't uncritically accept historical claims - maintain scientific skepticism while remaining open to insights"""

    def get_heritagenet_kg_prompt(self) -> str:
        """Get the HeritageNet knowledge graph extraction prompt."""
        return """You are tasked with extracting entities (nodes) and relationships from historical spine science texts and traditional medicine documents, then structuring them into Node and Relationship objects. Whatever the language of the documents, your extracted nodes and relationships should be translated in English. Here's the outline of what you need to do:

Content Extraction:
You should be able to process input content and identify entities mentioned within it.
Focus on entities related to historical spine treatments, observations, and medical concepts.

Node Extraction:
For each identified entity, create a Node object.
Each Node object should have a unique identifier (id) and a type (type).
Node types should be one of the following:
- ClinicalObservation (signs, symptoms, disease presentations)
- TherapeuticOutcome (treatment responses, recovery patterns)
- ContextualFactor (environmental, behavioral, constitutional factors)
- MechanisticConcept (traditional explanatory models, processes)
- TherapeuticApproach (interventions, remedies, methods)
- SourceText (reference to original documents or authors)
Additional properties associated with the node can also be extracted and stored.

Relationship Extraction:
Identify relationships between extracted entities in the content.
For each relationship, create a Relationship object.
A Relationship object should have a subject (subj) and an object (obj) which are Node objects.
Each relationship should have a type (type) from the following options:
- co_occurs_with (between related clinical observations)
- preceded_by/followed_by (temporal relationships)
- modified_by (how contexts affect observations)
- responds_to (observation responses to treatments)
- associated_with (contextual associations with observations)
- results_in (effects produced by treatments)
- described_in (attribution to source texts)
- contradicts/corroborates (consistency relationships)
Add any relevant qualifiers as additional properties if applicable.

Output Formatting:
The extracted nodes and relationships should be formatted as instances of the provided Node and Relationship classes.
Ensure that the extracted data adheres to the structure defined by the classes.
Output the structured data in a format that can be easily validated against the provided code.
Do not wrap the output in lists or dictionaries, provide the Node and Relationship with unique identifiers.
Strictly follow the format provided in the example output, do not add any additional information.

Instructions for you:
Read the provided historical spine science content thoroughly.
Identify distinct entities mentioned in the content and categorize them using the specified node types.
Determine relationships between these entities using the relationship types provided.
Provide the extracted nodes and relationships in the specified format below.

Example for you:
Example Content:
"Ollivier describes cases of paralysis linked to spinal blood congestions, where an accumulation of blood in the spinal veins leads to symptoms like incomplete paralysis without intellectual impairment. He notes that these congestions often resolve spontaneously."

Expected Output:
Nodes:
Node(id='paralysis_spinal_blood_congestion', type='ClinicalObservation')
Node(id='incomplete_paralysis', type='ClinicalObservation')
Node(id='preserved_intellect', type='ClinicalObservation')
Node(id='blood_accumulation_spinal_veins', type='MechanisticConcept')
Node(id='spontaneous_resolution', type='TherapeuticOutcome')
Node(id='Ollivier', type='SourceText')

Relationships:
Relationship(subj=Node(id='blood_accumulation_spinal_veins', type='MechanisticConcept'), obj=Node(id='paralysis_spinal_blood_congestion', type='ClinicalObservation'), type='associated_with')
Relationship(subj=Node(id='paralysis_spinal_blood_congestion', type='ClinicalObservation'), obj=Node(id='incomplete_paralysis', type='ClinicalObservation'), type='co_occurs_with')
Relationship(subj=Node(id='paralysis_spinal_blood_congestion', type='ClinicalObservation'), obj=Node(id='preserved_intellect', type='ClinicalObservation'), type='co_occurs_with')
Relationship(subj=Node(id='paralysis_spinal_blood_congestion', type='ClinicalObservation'), obj=Node(id='spontaneous_resolution', type='TherapeuticOutcome'), type='results_in')
Relationship(subj=Node(id='paralysis_spinal_blood_congestion', type='ClinicalObservation'), obj=Node(id='Ollivier', type='SourceText'), type='described_in')

===== TASK =====
Please extracts nodes and relationships from the given content and structure them
into Node and Relationship objects."""

    def _create_source_element(self, text: str) -> "Element":
        """
        Create a simple Element object for the source text.
        This mimics the Element from unstructured library.
        """
        try:
            from unstructured.documents.elements import Text
            return Text(text=text[:1000])  # Truncate for memory efficiency
        except ImportError:
            # Fallback: create a simple object that satisfies the Element protocol
            class SimpleElement:
                def __init__(self, text: str):
                    self.text = text

                def __str__(self):
                    return self.text

            return SimpleElement(text[:1000])

    def _parse_graph_elements(self, llm_output: str, source_text: str = "") -> GraphElement:
        """
        Parse nodes and relationships from LLM output in HeritageNet format.

        Args:
            llm_output: The LLM's response containing nodes and relationships
            source_text: Original source text to use as Element source
        """
        # Regular expressions to extract nodes and relationships
        node_pattern = r"Node\(id='(.*?)', type='(.*?)'\)"
        rel_pattern = (r"Relationship\(subj=Node\(id='(.*?)', type='(.*?)'\), "
                       r"obj=Node\(id='(.*?)', type='(.*?)'\), "
                       r"type='(.*?)'(?:, timestamp='(.*?)')?\)")

        nodes = {}
        relationships = []

        # Extract nodes
        for match in re.finditer(node_pattern, llm_output):
            node_id, node_type = match.groups()
            properties = {'source': 'phase2_chronos'}

            if node_id not in nodes:
                node = Node(id=node_id, type=node_type, properties=properties)
                nodes[node_id] = node

        # Extract relationships
        for match in re.finditer(rel_pattern, llm_output):
            groups = match.groups()
            if len(groups) == 6:
                subj_id, subj_type, obj_id, obj_type, rel_type, timestamp = groups
            else:
                subj_id, subj_type, obj_id, obj_type, rel_type = groups
                timestamp = None

            properties = {'source': 'phase2_chronos'}

            if subj_id in nodes and obj_id in nodes:
                subj = nodes[subj_id]
                obj = nodes[obj_id]
                relationship = Relationship(
                    subj=subj,
                    obj=obj,
                    type=rel_type,
                    timestamp=timestamp,
                    properties=properties,
                )
                relationships.append(relationship)

        # Create source element from the source text
        source_element = self._create_source_element(source_text if source_text else llm_output)

        return GraphElement(
            nodes=list(nodes.values()),
            relationships=relationships,
            source=source_element
        )

    def extract_knowledge_graph(
        self,
        phase1_brainstorm: str,
        ocr_text: str
    ) -> GraphElement:
        """
        Extract complete knowledge graph using Phase 2 methodology.

        Combines Phase 2 prompt + HeritageNet extraction format.
        """
        print("\n🔍 Extracting Knowledge Graph using Phase 2 methodology...")

        # Construct full prompt
        full_prompt = f"""{self.get_phase2_prompt()}

---

## KNOWLEDGE GRAPH EXTRACTION TASK

Based on the Phase 2 methodology above, extract a knowledge graph that bridges HeritageNet (historical observations) with SpineNet (modern concepts).

Use the following format for extraction:

{self.get_heritagenet_kg_prompt()}

---

## INPUT DATA

### Phase 1 Brainstorm (Ideas to map):
{phase1_brainstorm}

### Historical Medical Text (OCR):
{ocr_text[:10000]}
{'...[truncated]' if len(ocr_text) > 10000 else ''}

---

Now extract nodes and relationships following the format above. Create nodes for:
- Historical observations (from OCR text)
- Modern concepts (from Phase 1 ideas)
- Bridge connections between them

Use the Connection Types from Phase 2 as relationship types where applicable."""

        try:
            print("   🔄 Generating knowledge graph with Gemini...")
            # Use rate-limited request instead of direct API call
            rate_limiter = get_rate_limiter()
            response = rate_limited_request(
                self.model, 
                full_prompt, 
                delay_between_requests=15.0
            )

            if not response.text:
                raise ValueError("Empty response from Gemini model")

            llm_output = response.text
            print(f"   ✅ LLM output received ({len(llm_output):,} characters)")

            # Parse into GraphElement
            print("   📊 Parsing nodes and relationships...")
            # Combine phase1 + ocr as source text for traceability
            source_text = f"Phase1: {phase1_brainstorm[:500]}... | OCR: {ocr_text[:500]}..."
            graph_element = self._parse_graph_elements(llm_output, source_text)

            print(f"   ✅ Parsed {len(graph_element.nodes)} nodes and {len(graph_element.relationships)} relationships")

            return graph_element

        except Exception as e:
            print(f"   ❌ ERROR during KG extraction: {e}")
            import traceback
            traceback.print_exc()
            raise

    def store_in_neo4j(self, graph_element: GraphElement):
        """Store graph elements in Neo4j."""
        print("\n💾 Storing knowledge graph in Neo4j...")

        try:
            self.n4j_graph.add_graph_elements(graph_elements=[graph_element])
            print(f"   ✅ Stored {len(graph_element.nodes)} nodes and {len(graph_element.relationships)} relationships")
        except Exception as e:
            print(f"   ❌ ERROR storing in Neo4j: {e}")
            import traceback
            traceback.print_exc()
            raise

    def generate_phase2_summary(
        self,
        phase1_brainstorm: str,
        output_dir: str = "chronos_results/phase2"
    ) -> Dict[str, Any]:
        """Generate Phase 2 textual summary."""
        print("\n📝 Generating Phase 2 summary...")

        phase2_prompt = self.get_phase2_prompt()

        full_prompt = f"""{phase2_prompt}

---

## TASK: Phase 2 Summary

Based on the Phase 1 brainstorm below, provide a structured Phase 2 analysis:

1. **HeritageNet Mapping**: Identify which historical observations relate to Phase 1 ideas
2. **SpineNet Connections**: Map to modern spine science concepts
3. **Bridge Analysis**: Create explicit historical-modern connections (use Connection Types 1-5)
4. **Research Gaps**: Identify where modern research could test historical insights
5. **Cross-Cultural Convergence**: Note any cross-cultural patterns

---

PHASE 1 BRAINSTORM:
{phase1_brainstorm}

---

Provide a detailed Phase 2 analysis following the structure above."""

        try:
            print("   🔄 Generating summary with Gemini...")
            # Use rate-limited request instead of direct API call
            rate_limiter = get_rate_limiter()
            response = rate_limited_request(
                self.model, 
                full_prompt, 
                delay_between_requests=15.0
            )

            if not response.text:
                raise ValueError("Empty response from Gemini model")

            summary = response.text

            # Save summary
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(output_dir, f"phase2_summary_{timestamp}.txt")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(summary)

            print(f"   ✅ Summary generated ({len(summary):,} characters)")
            print(f"   💾 Saved to: {output_file}")

            metadata = {
                "timestamp": timestamp,
                "input_length": len(phase1_brainstorm),
                "output_length": len(summary),
                "output_file": output_file,
                "phase": "Phase 2 - Building Context and Connections"
            }

            return {
                "summary": summary,
                "metadata": metadata
            }

        except Exception as e:
            print(f"   ❌ ERROR during Phase 2 summary: {e}")
            import traceback
            traceback.print_exc()
            raise

    def run_phase2(
        self,
        phase1_brainstorm: str,
        ocr_text: str,
        output_dir: str = "chronos_results/phase2"
    ) -> Dict[str, Any]:
        """
        Run complete Phase 2: Extract KG and generate summary.
        """
        print("\n" + "="*80)
        print("🧠 PHASE 2: BUILDING CONTEXT AND CONNECTIONS")
        print("="*80)
        print(f"   Phase 1 brainstorm: {len(phase1_brainstorm):,} chars")
        print(f"   Historical text: {len(ocr_text):,} chars")
        print()

        results = {
            "phase": "Phase 2",
            "graph_element": None,
            "summary": None,
            "metadata": {}
        }

        # Extract Knowledge Graph
        try:
            graph_element = self.extract_knowledge_graph(
                phase1_brainstorm=phase1_brainstorm,
                ocr_text=ocr_text
            )
            results["graph_element"] = graph_element

            # Store in Neo4j
            self.store_in_neo4j(graph_element)

        except Exception as e:
            print(f"   ⚠️  Knowledge graph extraction failed: {e}")

        # Generate Summary
        try:
            summary_result = self.generate_phase2_summary(
                phase1_brainstorm=phase1_brainstorm,
                output_dir=output_dir
            )
            results["summary"] = summary_result["summary"]
            results["metadata"] = summary_result["metadata"]
        except Exception as e:
            print(f"   ⚠️  Summary generation failed: {e}")

        print("\n✅ Phase 2 completed!")
        return results

    def close(self):
        """Close connections."""
        print("✅ Phase 2 Context Builder connections closed")


def run_phase2(
    phase1_brainstorm: str,
    ocr_text: str,
    output_dir: str = "chronos_results/phase2",
    neo4j_url: str = "neo4j://127.0.0.1:7687",
    neo4j_username: str = "neo4j",
    neo4j_password: str = "0123456789",
    neo4j_database: str = "chronos"
) -> Dict[str, Any]:
    """Convenience function to run Phase 2."""
    builder = Phase2ContextBuilder(
        neo4j_url=neo4j_url,
        neo4j_username=neo4j_username,
        neo4j_password=neo4j_password,
        neo4j_database=neo4j_database
    )

    results = builder.run_phase2(
        phase1_brainstorm=phase1_brainstorm,
        ocr_text=ocr_text,
        output_dir=output_dir
    )

    builder.close()
    return results
