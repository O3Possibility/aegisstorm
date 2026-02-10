# Hurricane Constraint Tracker v2.0

**Constraint-aware diagnostic analysis for Atlantic hurricanes**

Real-time analysis that runs after each NHC advisory, revealing **why** forecasted changes happen through constraint topology.

---

## 🎯 What This Does

Traditional NHC forecasting tells you:
- **WHERE** the storm is going
- **WHEN** it will arrive
- **HOW STRONG** it will be

This system adds:
- **WHY** it's intensifying or weakening (constraint analysis)
- **HOW CLOSE** to thermodynamic limits (headroom tracking)
- **WHAT REGIME** it's in (RI candidate, peak-limited, structural collapse)

---

## 🚀 Quick Start

### 1. Clone & Deploy

```bash
# Clone this repository
git clone https://github.com/YOUR_USERNAME/hurricane-constraints-v2.git
cd hurricane-constraints-v2

# Push to your GitHub
git remote set-url origin https://github.com/YOUR_USERNAME/hurricane-constraints-v2.git
git push -u origin main
```

### 2. Enable GitHub Pages

1. Go to repository **Settings** → **Pages**
2. Source: Deploy from `docs/` folder on `main` branch
3. Save

Your site will be live at: `https://YOUR_USERNAME.github.io/hurricane-constraints-v2/`

### 3. Enable GitHub Actions

1. Go to **Actions** tab
2. Click "I understand my workflows, go ahead and enable them"

**Done.** System now runs every 6 hours automatically.

---

## 📊 How It Works

### Every 6 Hours (Aligned with NHC Advisories):

1. **Fetch NHC advisory** - Get official position, intensity, forecast
2. **Fetch environmental data** - SST, shear, potential intensity
3. **Calculate constraints:**
   - **I (Indicative)**: Thermodynamic headroom (distance from max intensity)
   - **R (Relational)**: Environmental favorability (shear, SST, latitude)
   - **S (Semantic)**: Structural coherence (organization quality)
   - **L (Admissibility)**: I × R × S (overall constraint state)
4. **Generate insight** - Compare NHC forecast to constraint analysis
5. **Update dashboard** - Deploy new HTML to GitHub Pages

---

## 🔬 The Constraint Framework

### Triadic Constraint Model

**Indicative (I)** - Thermodynamic Headroom
- Measures how close storm is to maximum possible intensity
- I = 1.0 → Lots of room to intensify
- I = 0.0 → At theoretical maximum
- Formula: `I = 1 - (current_intensity / potential_intensity)`

**Relational (R)** - Environmental Favorability
- Measures how favorable environment is for intensification
- Factors: Low wind shear, warm SST, tropical latitude, moisture
- R = 1.0 → Optimal conditions
- R = 0.0 → Hostile environment

**Semantic (S)** - Structural Coherence
- Measures storm organization quality
- Proxies: Classification, pressure-wind relationship, shear impact
- S = 1.0 → Well-organized hurricane
- S = 0.0 → Disorganized or collapsing structure
- **Note:** MVP uses proxies; production will use GOES-16 eye detection

**Admissibility (L)** - Overall State
- Product t-norm: `L = I × R × S`
- Strict conjunction (all must be high for high L)
- L → 0 means constrained futures (refusal condition)

### Regime Detection

Based on constraint patterns:

- **RI_CANDIDATE**: I > 0.65, R > 0.70, S > 0.60 → Rapid intensification possible
- **PEAK_LIMITED**: I < 0.35, S > 0.60 → Near thermodynamic ceiling
- **COLLAPSE**: S < 0.35 or rapid S decline → Structural failure
- **DECAY**: General decline in all constraints
- **STABLE**: No strong pattern

---

## 📈 Example: Hurricane Ian (2022)

### Sept 28, 00:00 UTC - At Peak Intensity

**NHC:** 125 kt, forecast to intensify further

**Constraint Analysis:**
- I = 0.406 (only 40% headroom left)
- R = 1.000 (optimal environment)
- S = 0.807 (strong structure)
- L = 0.328 (declining from 0.407)
- **Gradient Hazard:** ∇L < 0 (moving into lower admissibility)

**Insight:** "Storm at 60% of thermodynamic ceiling - limited upside, peak within 12 hours"

**Outcome:** Briefly hit 160 kt ~8 hours later, then weakened

### Sept 30, 12:00 UTC - Landfall

**NHC:** 65 kt, rapid weakening

**Constraint Analysis:**
- I = 0.440 (headroom increased - cut from ocean)
- R = 0.700 (unchanged)
- S = 0.170 (CRASHED from 0.807)
- L = 0.052 (CRITICAL refusal)

**Insight:** "Structural collapse - no viable tropical futures exist"

**Outcome:** Post-tropical transition, structure lost before intensity fully crashed

---

## 🛠️ Technical Details

### Data Sources

**Current (MVP):**
- NHC CurrentStorms.json API (free, public)
- Climatology-based SST/shear estimates
- Simplified potential intensity formula

**Planned Upgrades:**
- GOES-16 satellite eye detection (real S metric)
- CIRA potential intensity products (real I metric)
- SHIPS environmental diagnostics

### Constraint Calculation

**Simple, Proven Approach:**
- No coupling matrices (premature optimization)
- Simple 70/30 memory weighting
- Physically-justified formulas
- Transparent, debuggable

**Key Design Principle:** Ship proven signal first, add complexity only when validated

### Files Structure

```
hurricane-constraints-v2/
├── scripts/
│   ├── constraint_engine_v2.py    # Core constraint calculations
│   └── generate_dashboard.py      # HTML dashboard generator
├── data/
│   ├── current/                   # Latest NHC data cache
│   ├── constraints/               # Analysis outputs
│   └── historical/                # Historical storm data
├── docs/                          # GitHub Pages (auto-generated)
│   └── index.html
├── .github/workflows/
│   └── update-analysis.yml        # Automated updates every 6 hours
└── README.md
```

---

## 🔄 Local Testing

### Test on Current Storm

```bash
cd scripts
python constraint_engine_v2.py

# Or specify storm ID
python constraint_engine_v2.py al092026
```

### Test Dashboard Generation

```bash
python scripts/generate_dashboard.py
# Output: docs/index.html
```

### View Locally

```bash
# Open in browser
open docs/index.html
# or
python -m http.server 8000 --directory docs
# Then visit http://localhost:8000
```

---

## 📅 Deployment Timeline

### Phase 1: Deploy MVP (Week 1-2) ✓

- [x] Core constraint engine
- [x] NHC integration
- [x] Dashboard generator
- [x] GitHub Actions automation
- [ ] Push to GitHub
- [ ] Enable Pages + Actions

### Phase 2: Historical Validation (Week 3-6)

- [ ] Test on 10 historical storms
- [ ] Document constraint signatures
- [ ] Write case studies (Ian, Idalia, Michael)
- [ ] Calibrate thresholds
- [ ] Build pattern library

### Phase 3: Production Upgrade (Week 7-10)

**Pick ONE (not both initially):**

Option A: Add GOES-16 eye detection (real S metric)
- Parse GOES-16 Band 13 imagery from AWS
- Detect eye presence, diameter, circularity
- Direct structural measurement

Option B: Add CIRA potential intensity (real I metric)
- Fetch PI from CIRA/Colorado State products
- Replace simplified formula with actual PI calculation
- More accurate thermodynamic ceiling

### Phase 4: Launch (June 1, 2026)

- [ ] Deploy production v2.0
- [ ] Write launch post
- [ ] Share on r/TropicalWeather
- [ ] Monitor first storms
- [ ] Document interesting cases

---

## 🎓 Scientific Basis

### Constraint Theory

Based on formal constraint semantics from hazardsemantics.org

**Core Principle:** Hurricanes navigate a space of "licensed futures" ℒ∩ defined by intersection of:
- Physical constraints (thermodynamics)
- Environmental constraints (favorability)
- Structural constraints (coherence)

When ℒ∩ collapses → **refusal condition** → storm has no viable paths forward

### Related Work

- Emanuel (1988, 1995): Potential intensity theory
- Kaplan et al. (2010): Rapid intensification indices
- DeMaria & Kaplan (1999): SHIPS statistical-dynamical model

---

## ⚠️ Limitations & Disclaimers

**This is experimental research, not operational forecasting.**

**Current Limitations:**
1. **S (structure) uses proxies** - production needs satellite imagery
2. **Environmental data is estimated** - production needs real-time APIs
3. **No ensemble forecasting** - single deterministic analysis
4. **Limited validation** - needs full season of data

**Do NOT use for:**
- Evacuation decisions
- Emergency planning
- Any safety-critical application

**For official forecasts:** https://www.nhc.noaa.gov

---

## 🤝 Contributing

This is a research project. Contributions welcome:

**Bug reports:** Open an issue
**Improvements:** Submit a pull request
**Questions:** Start a discussion

**Particularly interested in:**
- GOES-16 eye detection implementation
- CIRA PI API integration
- Historical storm database
- Visualization improvements

---

## 📜 License

MIT License - Use freely, cite appropriately

---

## 📧 Contact

Questions about constraint framework: See hazardsemantics.org documentation

Questions about implementation: Open a GitHub issue

---

## 🌀 Status

**Season:** Atlantic Hurricane Season (June 1 - November 30)

**Current:** Pre-season deployment & testing

**Next Update:** June 1, 2026 (season start)

---

**Deploy it. Watch what happens when storms enter your zone.**
