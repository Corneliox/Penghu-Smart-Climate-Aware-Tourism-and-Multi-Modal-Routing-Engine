# 🤝 Contributing to Penghu Cool-Ride

Thank you for your interest in contributing to **Penghu Cool-Ride (Smart Climate-Aware Tourism & Node-Weight Routing Engine)**! 

This project is an open-source, biometeorological routing platform designed to safeguard tourists against heat exhaustion and heatstroke in the Penghu Archipelago, Taiwan. Contributions of all kinds—code improvements, bug fixes, data validation, biometeorological models, translations, and documentation—are warmly welcomed.

---

## 🧭 Table of Contents
1. [Code of Conduct](#-code-of-conduct)
2. [How Can I Contribute?](#-how-can-i-contribute)
3. [Local Development Setup](#-local-development-setup)
4. [Project Structure](#-project-structure)
5. [Coding & Data Standards](#-coding--data-standards)
6. [Commit & Pull Request Guidelines](#-commit--pull-request-guidelines)
7. [Reporting Bugs & Proposing Features](#-reporting-bugs--proposing-features)

---

## 📜 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please treat all community members with respect and kindness.

---

## 💡 How Can I Contribute?

* **🗺️ Geospatial & POI Data**: Report or correct inaccurate POI coordinates, missing 24h convenience stores (7-Eleven / FamilyMart), or updated ferry schedules in `data/`.
* **🔬 Biometeorological & Routing Algorithms**: Suggest or implement peer-reviewed thermal comfort models, physiological strain indices, or optimization heuristics in `benchmark_weighting_schemes.py` and `app.js`.
* **🌐 Internationalization (i18n)**: Add or improve language strings in `translations.json` (currently supporting Indonesian `id`, English `en`, and Traditional Chinese `zh`).
* **🎨 Frontend UI & Performance**: Optimize Leaflet map rendering, canvas IDW weather overlays, mobile responsiveness, or CSS theme variables in `style.css`.
* **📚 Documentation**: Fix typos, add explanations, or improve academic citations in `README.md`.

---

## 🛠️ Local Development Setup

### 1. Prerequisites
* **Git**
* **Python 3.10+**
* A modern web browser (Chrome, Edge, Firefox, Safari)

### 2. Clone the Repository
```bash
git clone https://github.com/Corneliox/MapNodeWeightRecommendation.git
cd MapNodeWeightRecommendation
```

### 3. Set Up Python Environment
```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)
```bash
cp .env.example .env
```
*(Only required if you are executing private Google Places or Google Routes crawlers. The frontend web app runs on 100% static JSON and does not require private API keys).*

### 5. Launch the Local Web Application
Because the web app uses ES module fetches (`translations.json`, `data/penghu_master_nodes.json`), launch a lightweight local HTTP server:
```bash
python -m http.server 8000
```
Open your browser at:
* **Landing Page**: [http://localhost:8000/](http://localhost:8000/)
* **Interactive Map Router**: [http://localhost:8000/app.html](http://localhost:8000/app.html)

---

## 📁 Project Structure

```text
MapNodeWeightRecommendation/
├── .github/
│   ├── ISSUE_TEMPLATE/           # GitHub Issue templates
│   ├── pull_request_template.md  # GitHub Pull Request template
│   └── workflows/
│       ├── deploy_pages.yml      # GitHub Pages automated deployment
│       └── weekly_data_update.yml# Automated weekly scraper pipeline
├── data/
│   ├── penghu_master_nodes.json  # Master dataset (2,190 POIs)
│   ├── penghu_ferry_routes.json  # Comprehensive maritime ferry schedules
│   └── benchmark_results.json    # Simulation outputs for scientific schemes
├── app.html                      # Interactive Map & Climate Router Engine
├── app.js                        # Frontend routing engine, IDW canvas & GIS logic
├── benchmark_weighting_schemes.py# Python validation benchmark for scientific schemes
├── fetch_penghu_osm.py           # OpenStreetMap Overpass API extractor
├── fetch_penghu_taiwan_opendata.py # Taiwan Tourism Admin API extractor
├── index.html                    # Root Landing Page & Scientific Showcase
├── merge_penghu_dataset.py       # Data merger, bilingual formatter & Wiki scraper
├── requirements.txt              # Python dependencies
├── style.css                     # Themes, glassmorphism & responsive CSS
├── translations.json             # Complete i18n dictionary (ID, EN, ZH)
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
└── SECURITY.md
```

---

## 📐 Coding & Data Standards

### JavaScript (`app.js`)
* Use modern Vanilla ES6+ without adding heavy frameworks (React/Vue/Angular), maintaining fast load times (<1s) on mobile devices.
* Ensure all DOM manipulations handle nullable elements gracefully.
* Always clean up map layers (`map.removeLayer(...)`) before re-rendering overlays or polylines.

### Python Scripts
* Follow **PEP 8** formatting guidelines.
* Include docstrings and meaningful variable names.
* When adding web scrapers, respect API rate limits and provide explicit `User-Agent` headers.

### Geospatial & POI Conventions
* Coordinates must fall within the bounding box of the Penghu Archipelago:
  * Latitude: `23.05` to `23.95` N
  * Longitude: `119.10` to `119.90` E
* Landmark and POI names must follow universal bilingual formatting:
  `[Traditional Chinese Name] / [English Name]`  
  *(Example: `通梁古榕 / Tongliang Great Banyan`)*

### Multi-Language Translations (`translations.json`)
* When adding a new UI key, update all three supported locales (`id`, `en`, `zh`) simultaneously to prevent fallback UI errors.

---

## 🌿 Commit & Pull Request Guidelines

### 1. Branch Naming
Create feature branches from `master`:
* `feat/new-routing-scheme`
* `fix/poi-coordinates-qimei`
* `docs/update-citation`

### 2. Conventional Commits
Write concise commit messages following the [Conventional Commits](https://www.conventionalcommits.org/) convention:
* `feat:` A new feature or capability
* `fix:` A bug fix
* `docs:` Documentation updates only
* `style:` Formatting, CSS tweaks without logic changes
* `refactor:` Code restructuring without functional changes
* `perf:` Performance improvements
* `test:` Adding or updating tests
* `chore:` Build scripts, dependencies, or maintenance tasks

### 3. Pull Request (PR) Checklist
Before submitting a PR:
- [ ] Code runs cleanly without console errors or unhandled exceptions.
- [ ] Tested responsively on mobile viewport (width <= 480px) and desktop.
- [ ] Language keys in `translations.json` remain complete and valid JSON.
- [ ] Commit history is clean and descriptive.
- [ ] Description clearly explains the *Why* and *What* of the changes.

---

## 🐛 Reporting Bugs & Proposing Features

* **Bugs**: Use the [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md) template. Please include browser version, OS, reproduction steps, and screenshots if applicable.
* **Features & Algorithms**: Use the [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md) template. Explain the motivation, use cases, and academic references if proposing a new biometeorological model.
* **Data Corrections**: Open an issue detailing the POI name, incorrect coordinates, and verified reference (e.g., Google Maps link, Taiwan Tourism Admin entry).

---
Thank you for helping keep travellers safe, cool, and hydrated across Penghu! 🏝️❄️
