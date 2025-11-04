# CHRONOS Refined Pipeline - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites

1. **Neo4j Database** (running)
   ```bash
   neo4j start
   # Verify at http://localhost:7474
   ```

2. **Environment Setup**
   ```bash
   # Create .env file in project root
   cp .env.example .env

   # Add your API keys
   GOOGLE_API_KEY=your-gemini-api-key
   NEO4J_PASSWORD=your-neo4j-password
   ```

3. **Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Run Your First Pipeline

```bash
cd chronos/app
python main.py
```

**Select Option 3:**
```
🔀 PIPELINE SELECTION
================================================================================
Three analysis pipelines are available:

  3️⃣  REFINED CHRONOS PIPELINE (Recommended) ✨

Enter your choice (1, 2, or 3): 3
```

**Confirm to proceed:**
```
Proceed with processing? (y/n): y
```

---

## 📂 What Happens Next?

### Step 1: OCR Extraction (~2-5 min)
```
📋 STEP 1: Extract Text from Document (OCR)
📄 Processing PDF with 50 pages...
  ✅ Page 1/50
  ✅ Page 2/50
  ...
✅ Text extraction complete: 125,483 characters
```

### Step 2: Phase 1 Brainstorm (~1-3 min)
```
📋 STEP 2: PHASE 1 - Self-Critical Brainstorm
🧠 PHASE 1: SELF-CRITICAL BRAINSTORM
  Processing 125,483 characters of historical text...
  🔄 Generating brainstorm with Gemini...
  ✅ Brainstorm generated (8,912 characters)
  💾 Brainstorm saved to: chronos_results/phase1/phase1_brainstorm_20241024_143022.txt
```

### Step 3: Phase 2 Context Building (~3-8 min)
```
📋 STEP 3: PHASE 2 - Building Context and Connections
   Building HeritageNet (Historical Medical Evidence)
   Building SpineNet (Modern Spine Science)
   Creating Bridges (Historical-Modern Connections)

🏛️  BUILDING HERITAGENET (Historical Medical Evidence)
   Processing 2 chunk(s)...
   ✅ HeritageNet built successfully!

🔬 BUILDING SPINENET & BRIDGES (Modern-Historical Connections)
   Processing 2 chunk(s)...
   ✅ SpineNet & Bridges built successfully!

📝 GENERATING PHASE 2 SUMMARY
   ✅ Summary generated (12,456 characters)
```

---

## 📊 Review Your Results

### 1. Phase 1 Brainstorm
```bash
cat chronos_results/phase1/phase1_brainstorm_*.txt
```

**What you'll see:**
- Free-flowing exploration of spine phenomena
- Self-critical questions and assumptions
- Pattern identifications and paradoxes
- Emerging hypotheses and connections

### 2. Phase 2 Summary
```bash
cat chronos_results/phase2/phase2_summary_*.txt
```

**What you'll see:**
- HeritageNet mapping (historical observations)
- SpineNet connections (modern concepts)
- Bridge analysis (historical-modern links)
- Research gaps identified
- Cross-cultural convergence patterns

### 3. Knowledge Graph (Neo4j)

**Open Neo4j Browser:**
```
http://localhost:7474
```

**Switch to CHRONOS database:**
```cypher
:use chronos
```

**Explore the graph:**

**See all node types:**
```cypher
CALL db.labels()
```

**View historical observations:**
```cypher
MATCH (n)
WHERE n:ClinicalObservation OR n:HistoricalObservation
RETURN n
LIMIT 25
```

**Find historical-modern bridges:**
```cypher
MATCH path = (h)-[r:translates_to_modern_concept*1..2]->(m)
WHERE h:HistoricalObservation OR h:ClinicalObservation
RETURN path
LIMIT 10
```

**Find research gaps:**
```cypher
MATCH (obs)-[:has_research_gap]->(gap:ResearchGap)
RETURN obs.id as Observation, gap.id as ResearchGap
```

**See all relationship types:**
```cypher
CALL db.relationshipTypes()
```

---

## 🎯 Common Workflows

### Workflow 1: Process Multiple Documents

**Edit main.py:**
```python
documents = [
    "/path/to/doc1.pdf",
    "/path/to/doc2.pdf",
    "/path/to/doc3.pdf"
]

for i, doc in enumerate(documents, 1):
    INPUT_FILE = doc
    OUTPUT_TEXT_FILE = f"/path/to/output_{i}.txt"
    # Run pipeline
    ...
```

### Workflow 2: Extract Specific Patterns from Graph

**Query for treatment translations:**
```cypher
MATCH (h:HistoricalTreatment)-[:has_modern_analog]->(m:ModernConcept)
RETURN h.id as HistoricalTreatment,
       m.id as ModernAnalog
```

**Query for cross-cultural convergences:**
```cypher
MATCH (c:CrossCulturalEvidence)-[:corroborates]->(obs)
RETURN c.id as Convergence,
       collect(obs.id) as Observations
```

### Workflow 3: Export Results

**Export Phase 1 & 2 summaries:**
```bash
# Create combined report
cat chronos_results/phase1/phase1_brainstorm_*.txt \
    chronos_results/phase2/phase2_summary_*.txt \
    > combined_report.txt
```

**Export Neo4j graph:**
```cypher
// In Neo4j Browser
CALL apoc.export.json.all("chronos_graph.json", {})
```

---

## 🔧 Customization

### Adjust OCR Quality

**In main.py:**
```python
OCR_CONFIG = {
    "enhancement_level": "aggressive",  # Try: "light", "medium", "aggressive"
    "use_high_dpi": True,              # False for faster processing
    "save_debug_images": True,         # Save preprocessed images for inspection
}
```

### Adjust Chunking for Large Documents

**In main.py:**
```python
KG_CONFIG = {
    "kg_chunk_size": 10000,    # Reduce if getting errors (try 8000, 5000)
    "enable_chunking": True,   # Set False for small docs (<10k chars)
}
```

### Change Models

**In .env:**
```bash
# Use different Gemini model
CHRONOS_MODEL=gemini-2.0-flash  # Faster, cheaper
# or
CHRONOS_MODEL=gemini-1.5-pro    # More capable
```

---

## 🐛 Troubleshooting

### Issue: "Neo4j connection failed"

**Solution:**
```bash
# Check Neo4j status
neo4j status

# Start Neo4j
neo4j start

# Verify credentials in .env
NEO4J_PASSWORD=your-password
```

### Issue: "Empty brainstorm generated"

**Possible causes:**
- OCR text too short (< 100 characters)
- Gemini API quota exceeded
- Network connectivity issues

**Solutions:**
```python
# 1. Check extracted text length
print(f"Extracted text length: {len(extracted_text)}")

# 2. Verify API key
echo $GOOGLE_API_KEY

# 3. Check Gemini API quota at:
# https://console.cloud.google.com/apis/dashboard
```

### Issue: "Knowledge graph appears empty"

**Solution:**
```cypher
// Check if nodes were created
MATCH (n)
RETURN count(n)

// Check specific database
:use chronos
MATCH (n)
RETURN count(n)

// If count is 0, check logs for extraction errors
```

### Issue: "Out of memory"

**Solution:**
```python
# Reduce chunk size in main.py
KG_CONFIG = {
    "kg_chunk_size": 5000,  # Smaller chunks
}

# Or process smaller sections of document
# Extract specific page ranges in OCR
```

---

## 📈 Performance Tips

### Optimize for Speed

1. **Use smaller chunks:** `kg_chunk_size: 5000`
2. **Lower OCR quality:** `enhancement_level: "light"`
3. **Disable debug images:** `save_debug_images: False`
4. **Use faster model:** `CHRONOS_MODEL=gemini-2.0-flash`

### Optimize for Quality

1. **Use larger chunks:** `kg_chunk_size: 15000`
2. **Higher OCR quality:** `enhancement_level: "aggressive"`
3. **Enable debug images:** `save_debug_images: True`
4. **Use better model:** `CHRONOS_MODEL=gemini-1.5-pro`

### Optimize for Cost

1. **Medium chunk size:** `kg_chunk_size: 10000`
2. **Standard OCR:** `enhancement_level: "medium"`
3. **Use Flash model:** `CHRONOS_MODEL=gemini-2.0-flash-exp`
4. **Disable unnecessary features**

---

## 📖 Next Steps

### 1. Understand the Methodology
```bash
cat prompt.md  # Read full CHRONOS methodology
```

### 2. Explore the Code
```bash
# Phase 1 implementation
cat chronos/app/phase1_brainstorm.py

# Phase 2 implementation
cat chronos/app/phase2_context_builder.py

# Knowledge graph agents
cat chronos/app/chronos_kg_agent.py
cat chronos/app/KGAgents.py
```

### 3. Read Detailed Documentation
```bash
cat chronos/PHASE_1_2_README.md
```

### 4. Wait for Phase 3 & 4
- Phase 3: Distilling to the Essence
- Phase 4: Formulating Testable Hypotheses
- FutureHouse: Hypothesis Verification

---

## 💡 Tips & Best Practices

### 1. Start Small
- Test with a short document first (5-10 pages)
- Verify results before processing large corpus

### 2. Review Incrementally
- Check Phase 1 brainstorm before Phase 2
- Inspect Neo4j graph after each document
- Validate node IDs are descriptive (not generic)

### 3. Use Neo4j Browser
- Visualize relationships graphically
- Export interesting subgraphs
- Create custom queries for your research

### 4. Keep Results Organized
```bash
# Create dated result folders
mkdir chronos_results/2024-10-24/
mv chronos_results/phase1/* chronos_results/2024-10-24/
mv chronos_results/phase2/* chronos_results/2024-10-24/
```

### 5. Document Your Findings
- Take notes on interesting bridges
- Screenshot Neo4j visualizations
- Export key Cypher queries

---

## 🎓 Learning Resources

### CHRONOS Methodology
- `prompt.md`: Complete methodology
- `PHASE_1_2_README.md`: Implementation details

### Knowledge Graphs
- Neo4j Documentation: https://neo4j.com/docs/
- Cypher Query Language: https://neo4j.com/docs/cypher-manual/

### Medical Text Mining
- PubMed: https://pubmed.ncbi.nlm.nih.gov/
- HeritageNet concept: Historical medical databases

---

## ✅ Success Checklist

After running your first pipeline, verify:

- [ ] Phase 1 brainstorm file created
- [ ] Phase 2 summary file created
- [ ] Neo4j database contains nodes
- [ ] Can query historical observations
- [ ] Can query modern concepts
- [ ] Can find bridge relationships
- [ ] Node IDs are descriptive (not generic)
- [ ] Cross-cultural convergences identified (if applicable)
- [ ] Research gaps extracted

---

## 🆘 Getting Help

**Check in this order:**

1. This QUICKSTART.md
2. PHASE_1_2_README.md
3. Code docstrings (phase1_brainstorm.py, phase2_context_builder.py)
4. prompt.md (methodology)
5. Neo4j graph inspection

**Common Question Answers:**

**Q: How long does it take?**
A: ~10-20 minutes for a 50-page document

**Q: Can I pause and resume?**
A: Not currently - run complete pipeline

**Q: Can I process non-medical documents?**
A: Yes, but results optimized for medical/spine texts

**Q: How do I add custom node types?**
A: Edit `chronos_kg_agent.py` node type definitions

**Q: Can I use other databases besides Neo4j?**
A: CAMEL framework supports others, but not implemented yet

---

**Ready to explore historical medical knowledge with CHRONOS!** 🚀

Start with: `cd chronos/app && python main.py`
