# Project Story — AI Operations Workbench

## 1. Starting point

The project started with a simple objective:

> Learn the complete AI lifecycle end to end rather than only understanding individual AI concepts.

The first instinct was to build separate examples — an ML model, an optimizer, a computer-vision use case and a GenAI use case.

That quickly evolved into a larger question:

> What would it take to turn these isolated capabilities into one coherent industrial AI application?

That became the AI Operations Workbench.

---

## 2. The design principle

The Workbench was structured around one idea:

**Every AI capability should begin with a business problem and end with a decision output.**

So each module follows the same general pattern:

```text
Problem
  ↓
Inputs
  ↓
AI / analytics engine
  ↓
API
  ↓
Application experience
  ↓
Decision output
  ↓
Validation / limitations
```

This made the project more than a collection of notebooks.

---

## 3. Module evolution

### Compressor Health

The first module began as an anomaly-detection notebook.

The learning journey included:

- creating synthetic process data
- preparing training and test periods
- scaling data correctly
- training an Isolation Forest
- understanding anomaly thresholds
- saving model artifacts
- exposing inference through FastAPI
- connecting the API to a frontend
- translating a model score into a business-facing health signal

The key lesson was that a model is only one component of an AI product.

---

### Feed Allocation Optimizer

The second module introduced a different AI/analytics paradigm.

Instead of predicting something, the model had to make a constrained decision.

The work therefore focused on:

- defining decision variables
- defining an objective function
- translating plant constraints into mathematics
- creating route economics
- understanding feasibility
- interpreting solver results
- exposing the optimizer as an API
- making operational assumptions visible in the user interface

This module reinforced the difference between machine learning and mathematical optimization.

---

### Visual Operator Rounds

The original computer-vision idea was generic equipment classification.

That was narrowed to equipment-nameplate OCR because it provided a clearer operational workflow.

The module evolved into:

```text
Photo
  ↓
Image processing
  ↓
OCR
  ↓
Structured information
```

The biggest learning point was the importance of image quality, preprocessing and confidence limitations.

---

### Technology Intelligence

The fourth module changed the most.

The first version used company-page scraping and keyword matching.

That produced a major design lesson:

> Retrieval quality matters more than adding an LLM on top of poor retrieval.

The architecture was therefore redesigned around search-enabled research:

```text
Question
  ↓
Search / retrieval
  ↓
Evidence selection
  ↓
LLM synthesis
  ↓
Sources
  ↓
History
  ↓
Future trend comparison
```

This turned the module from a basic scraper into a more realistic GenAI research architecture.

---

## 4. Application evolution

The application architecture also evolved.

### Stage 1 — notebooks

Each capability was developed independently.

### Stage 2 — Python modules

Reusable logic was separated from experiments.

### Stage 3 — FastAPI

Each capability became accessible through an API.

### Stage 4 — Streamlit

A first integrated user interface demonstrated that the modules could work together.

### Stage 5 — React

The frontend was redesigned as a professional portfolio application.

### Stage 6 — deployment design

Dockerfiles, GitHub and Azure-readiness configuration were added to understand the path from local development to cloud deployment.

---

## 5. What I learned

The project gave practical exposure to the boundaries between:

- business problem definition
- data engineering
- machine learning
- optimization
- computer vision
- GenAI
- backend engineering
- APIs
- frontend development
- application architecture
- cloud deployment

The most important lesson was that successful AI applications require these pieces to work together.

---

## 6. How I would explain the project in an interview

### 30-second version

> I built an AI Operations Workbench to learn the full AI application lifecycle. It combines compressor anomaly detection, gas-feed optimization, computer-vision OCR and a search-enabled GenAI intelligence workflow. I developed the data/model logic, wrapped each capability in FastAPI, integrated them into a React application, and prepared the architecture for cloud deployment. The operational data and economics are synthetic, so I position it as a portfolio architecture and learning project rather than a field-validated product.

### 2-minute version

> I wanted to go beyond understanding AI conceptually and learn how an actual AI product is assembled. So I built four industrial use cases covering four different technology patterns. The compressor module uses Isolation Forest for anomaly detection, the feed-allocation module uses linear programming, the visual module uses OpenCV and OCR, and the intelligence module uses a search-enabled GenAI research architecture. I separated model logic from the application layer, exposed the capabilities using FastAPI and integrated them into one React Workbench. I also worked through deployment concerns such as Docker packaging, environment-based API routing, persistence and cloud architecture. The main value of the exercise was understanding the end-to-end system rather than only building individual models.

---

## 7. Accurate professional claim

### Current claim

> Designed and developed an end-to-end AI Operations Workbench integrating predictive analytics, optimization, computer vision and GenAI/search-enabled workflows, covering data preparation, model development, API integration, application architecture and cloud-ready deployment design.

### Claim after actual public cloud deployment

> Designed and developed an end-to-end AI Operations Workbench integrating predictive analytics, optimization, computer vision and GenAI/agentic workflows, covering data preparation, model evaluation, API integration, application architecture and cloud deployment.

The distinction matters because the current repository contains deployment design and packaging, but a public production cloud deployment should only be claimed once it actually exists.
