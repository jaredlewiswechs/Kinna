# Kinna

**Kinematic Linguistics v1.4 — A geometric substrate for semantic reliability**

Kinna is an implementation of Kinematic Linguistics (KL v1.4), a theoretical framework that models natural language as geometry. Words are treated as mechanical assemblies where individual letters are "glyphs" with 3D mechanical vectors (Structure, Force, Flow), and word meaning emerges from the geometric stability of composed letter assemblies.

## Core Concepts

- **Glyph Vectors**: Each of the 26 Latin letters maps to a 3D vector representing Structure, Force, and Flow properties (e.g., `A = (0.90, 0.30, 0.10)` — triangular stability)
- **Word Assembly**: Words are decomposed into glyphs and combined with positional weighting (initial, medial, terminal) to produce a composite word vector
- **Distortion Index (DI)**: Quantifies semantic distortion between word vectors via cosine similarity, with classification thresholds:
  - `DI < 0.35` — CONGRUENT (allow)
  - `0.35 ≤ DI < 0.70` — SUSPECT (clarify)
  - `DI ≥ 0.70` — CONFLICT (reject)
- **Regime Detection**: Domain-specific physics (fluid dynamics, structural engineering, aviation, medicine, etc.) that remap glyph meanings based on context
- **Sentence Construction**: Generates sentences by solving geometric intent equations against a vocabulary index

## Installation

Requires **Python 3.10+**.

```bash
# Basic install
pip install -e .

# With WordNet support (for vocabulary crawling)
pip install -e ".[wordnet]"

# With dev tools (pytest)
pip install -e ".[dev]"
```

## Usage

Kinna provides a CLI with six commands:

### Assemble Word Vectors

Decompose words into their kinematic vectors:

```bash
python -m kinna assemble WATER FIRE STONE
```

### Compare Two Words

Compute the Distortion Index between two words:

```bash
python -m kinna compare DRAFT BREEZE
```

### Detect Regime

Identify the domain/regime for a given query:

```bash
python -m kinna regime "the fluid flows through the pipe"
```

### Build a Sentence

Generate a sentence from a geometric intent template:

```bash
python -m kinna build MOVE_UP
```

Available intents: `MOVE_UP`, `MOVE_DOWN`, `FLOW_THROUGH`, `IMPACT_STOP`, `STABLE_REST`, `ACTIVE_TRANSFER`.

### Run the KL-100 Audit

Execute the full benchmark suite (20 labeled test cases):

```bash
python -m kinna audit
```

### Crawl WordNet

Index WordNet synsets into the local `kinematic.db` SQLite database:

```bash
python -m kinna crawl --limit 500
```

Requires the `wordnet` optional dependency (`nltk`).

## Architecture

The system is organized into five phases matching the KL v1.4 specification:

### Phase 1 — Physics Kernel

The core geometry engine that maps letters to vectors and composes word-level representations.

| Module | Purpose |
|---|---|
| `glyph_db.py` | Maps 26 Latin letters to 3D mechanical vectors with topology and physical properties |
| `assembler.py` | Computes composite word vectors with positional weighting |
| `di_calculator.py` | Calculates Distortion Index via cosine similarity |

### Phase 2 — Vocabulary Engine

Indexing and phonosemantic tagging for large-scale vocabulary.

| Module | Purpose |
|---|---|
| `kinematic_crawler.py` | WordNet-to-SQLite pipeline; indexes synsets with word vectors |
| `cluster_tagger.py` | Assigns phonosemantic regime tags (e.g., `FL_VECTOR`, `ST_ANCHOR`, `CR_FRACTURE`) |

### Phase 3 — Logic Controller

Intent detection and polymorphic word handling across domains.

| Module | Purpose |
|---|---|
| `regime_locker.py` | Phase 0 intent lock via keyword detection across 7 regimes |
| `context_switch.py` | Regime-specific glyph remapping for polymorphic words (e.g., DRAFT in fluid vs. structural contexts) |

### Phase 4 — Construction Engine

Sentence generation from geometric intent templates.

| Module | Purpose |
|---|---|
| `sentence_builder.py` | Sentence synthesis via geometric intent matching against vocabulary |
| `tense_modifier.py` | Suffix morphology as vector blending (`-ED` adds structure, `-ING` adds flow) |

### Phase 5 — Safety Audit

Verification gates and benchmark testing.

| Module | Purpose |
|---|---|
| `safety_interlock.py` | Per-word verification; hard rejection for `DI ≥ 0.70` (`GeometricConflictError`) |
| `audit_suite.py` | KL-100 benchmark with 20 labeled test cases tracking regime accuracy, conflict precision/recall, and determinism |

## Supported Regimes

| Regime | Domain |
|---|---|
| `FLUID_DYNAMICS` | Fluid mechanics, flow, turbulence |
| `STRUCTURAL_ENGINEERING` | Load-bearing, stability, materials |
| `THERMAL` | Heat transfer, thermodynamics |
| `ELECTRICAL` | Circuits, conductance, signal |
| `MEDICINE` | Anatomy, pathology, treatment |
| `AVIATION` | Aerodynamics, flight systems |
| `COMPOSITION` | General-purpose writing and language |

## Testing

The test suite contains 47 test cases across two files:

```bash
# Run all tests
pytest

# Phase 1 tests (glyph database, assembler, DI calculator)
pytest tests/test_kernel.py

# Phases 2–5 tests (engines, controllers, safety)
pytest tests/test_engine.py
```

## Project Structure

```
kinna/
├── __init__.py            # Package metadata
├── __main__.py            # CLI entry point (6 commands)
├── glyph_db.py            # Glyph → 3D vector database
├── assembler.py           # Word vector assembly
├── di_calculator.py       # Distortion Index calculator
├── kinematic_crawler.py   # WordNet indexing pipeline
├── cluster_tagger.py      # Phonosemantic clustering
├── regime_locker.py       # Regime detection
├── context_switch.py      # Regime-specific remapping
├── sentence_builder.py    # Sentence generation
├── tense_modifier.py      # Morphological suffix handling
├── safety_interlock.py    # Safety verification gates
└── audit_suite.py         # KL-100 benchmark suite
tests/
├── test_kernel.py         # Phase 1 tests
└── test_engine.py         # Phases 2–5 tests
```

## Dependencies

**Core**: None — runs entirely on the Python 3.10+ standard library.

**Optional**:
- `nltk ≥ 3.8` — WordNet corpus access (for the `crawl` command)
- `pytest ≥ 7.0` — Test runner
