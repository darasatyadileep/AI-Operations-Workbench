# Screenshot Guide

Use this guide to create a clean portfolio screenshot set.

The objective is not to capture every screen. The objective is to tell the project story in 5–6 images.

---

## Folder structure

Save screenshots here:

```text
docs/screenshots/
├── 01_overview.png
├── 02_compressor_health.png
├── 03_feed_optimizer.png
├── 04_visual_inspection.png
├── 05_technology_intelligence.png
└── 06_architecture.png
```

---

## 01 — Overview

### Capture

The Workbench landing page showing:

- title / branding
- four modules
- architecture section if visible
- enough navigation to establish that this is one integrated application

### Purpose

This is the main “hero” image.

### File

`docs/screenshots/01_overview.png`

---

## 02 — Compressor Health

### Capture

Show:

- uploaded / sample compressor data
- health status
- anomaly score
- anomaly trend chart
- thresholds if visible

### Purpose

Demonstrates predictive analytics + model-serving workflow.

### File

`docs/screenshots/02_compressor_health.png`

---

## 03 — Feed Optimizer

### Capture

Show a state where the optimizer has already run.

Ideally include:

- feed / capacity inputs
- optimized value
- uplift
- plant loading or route allocation
- synthetic-value disclaimer

### Purpose

Demonstrates mathematical optimization and decision support.

### File

`docs/screenshots/03_feed_optimizer.png`

---

## 04 — Visual Inspection

### Capture

Show:

- equipment nameplate image
- OCR / extracted result
- structured output

Choose a clear printed-nameplate example that works well.

### Purpose

Demonstrates computer vision and OCR.

### File

`docs/screenshots/04_visual_inspection.png`

---

## 05 — Technology Intelligence

### Capture

If live OpenAI API credits are available:

- research question
- evidence-backed result
- source links

If live research is not funded:

- show the research interface and architecture
- do not manufacture a successful live result

### Purpose

Demonstrates the GenAI / search-enabled workflow honestly.

### File

`docs/screenshots/05_technology_intelligence.png`

---

## 06 — Architecture

Use the existing architecture visual:

`professional_web/public/architecture-overview.png`

If desired, copy it into:

`docs/screenshots/06_architecture.png`

### Purpose

Allows a reviewer to understand the entire system at a glance.

---

# Recommended README placement

After adding screenshots, insert a short showcase section near the top of the main `README.md`.

Example:

```markdown
## Application preview

### Integrated Workbench
![Overview](docs/screenshots/01_overview.png)

### Compressor Health
![Compressor Health](docs/screenshots/02_compressor_health.png)

### Feed Allocation Optimizer
![Feed Optimizer](docs/screenshots/03_feed_optimizer.png)

### Visual Inspection
![Visual Inspection](docs/screenshots/04_visual_inspection.png)

### Technology Intelligence
![Technology Intelligence](docs/screenshots/05_technology_intelligence.png)
```

Avoid adding more than 6–8 large images to the README. Too many screenshots make the repository look less curated.

---

# Screenshot quality

Use:

- browser zoom around 90–100%
- full-width application viewport
- no browser bookmarks or personal tabs if possible
- consistent dark theme
- no terminal windows in final screenshots
- no API keys
- no personal data
- no proprietary company information

The best screenshots should make the project understandable without requiring the reviewer to run the code.
