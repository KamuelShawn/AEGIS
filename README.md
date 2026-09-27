# 🌍 AIGES
### *Develop Without Destroying*

**A cinematic geospatial intelligence platform that helps India decide *where*, *how*, and *how much* to develop — without crossing the point of no return for its forests, water, and ecosystems.**

Built by **Team Pentagon**.

---

## 📌 Table of Contents

- [The Problem](#-the-problem)
- [Our Solution](#-our-solution)
- [How It Works](#-how-it-works)
- [Core Modules](#-core-modules)
- [The Intelligence Behind It](#-the-intelligence-behind-it)
- [Data Honesty](#-data-honesty)
- [Design Philosophy](#-design-philosophy)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Team](#-team)
- [License](#-license)

---

## 🚨 The Problem

India is growing fast — new highways, industries, mines, ports, and cities are planned every year. But development decisions are still largely made **without a unified view** of what's at stake.

Planners, governments, and communities are constantly forced to ask questions that today have no single, reliable place to answer:

- **Where can we actually develop**, without triggering irreversible ecological damage?
- **How much** of a resource — forest, groundwater, mineral reserve — can be used before it's gone for good?
- **What has already changed** in a region over the last 10–25 years, and why?
- **What happens if current trends continue** unchecked?
- **If we shouldn't build here, where *should* we build instead?**

Environmental data, resource data, infrastructure data, industrial data, and population data today live in **disconnected silos**. Because of this, the true cost of a decision — a road through a forest corridor, a factory near a water-stressed village, a port near a mangrove — is often only understood *after* the damage is done.

**The land doesn't announce its own decline. Someone has to go looking for it — before it's too late.**

---

## 💡 Our Solution

**AIGES** is a geospatial decision-support platform that connects the full chain of cause and effect:

```
ENVIRONMENT → NATURAL RESOURCES → INFRASTRUCTURE → INDUSTRY → POPULATION → DECISION
```

Instead of a static dashboard full of numbers, AIGES is built as an **investigative experience**. It takes a user from a beautiful, living map of India all the way down to a single, explainable, sustainable recommendation — showing exactly *what exists*, *what changed*, *why it changed*, *what's at risk*, and *what the alternatives are*.

The guiding principle behind every feature is simple:

> **Balance Environment + Resources + Development.**

AIGES doesn't just flag problems. For every warning it raises, it proposes an alternative — a different route, a different site, a different threshold — so the answer is never just *"don't build here,"* but always **"build here instead."**

---

## 🧭 How It Works

The user's journey through the platform follows one continuous arc:

**EXPLORE → UNDERSTAND → COMPARE → MEASURE → PREDICT → SIMULATE → OPTIMIZE → DECIDE**

At every step, the platform is answering one of these questions:

1. Where am I?
2. What exists here?
3. What changed?
4. Why did it change?
5. What is under pressure?
6. What happens next?
7. What choices do I have?
8. Which choice is best?

**Geographic drill-down:** India → State → District → City → Village → Forest / River Basin / Lake / Wetland / Coastal Region / Industrial Region / Infrastructure Corridor / Protected Ecosystem.

---

## 🧩 Core Modules

| Module | What it does |
|---|---|
| **Environment** | Tracks forests, wetlands, grasslands, biodiversity zones, coastal ecosystems and mangroves — condition, history, rate of change, and threat level. |
| **Environmental Risk Engine** | Classifies every region as **Safe / Warning / Critical / Severe**, and always explains *why*, and *what to do about it*. |
| **Natural Resources (Water, Minerals)** | Models availability vs. replenishment vs. consumption to calculate a **sustainable extraction limit** — not just "resource available." |
| **Coastal Development** | Evaluates mangroves, erosion, flood risk, and fishing communities before recommending coastal sites. |
| **Infrastructure & Route Optimization** | Scores candidate roads/rail routes on cost, environmental damage, and social impact, with **interactive weight sliders** that live-recalculate the best route. |
| **Industrial Site Suitability** | Scores proposed industrial sites on pollution risk, water availability, and proximity to people and protected land. |
| **Encroachment Detection** | Visualizes development creeping into forests, lakes, wetlands, and protected zones over time. |
| **Air & Environmental Quality** | Surfaces AQI and pollution trends geographically and historically. |
| **Scenario Simulation ("What If?")** | Lets users adjust industrial growth, population, water consumption, and forest protection to see the future change in real time. |
| **Recommendation Engine** | Every detected problem is paired with concrete, explainable interventions — never a warning without a next step. |

---

## 🧠 The Intelligence Behind It

AIGES is built on real computational logic, not decorative numbers:

- **Trend analysis** — direction, rate, and acceleration of environmental/resource change
- **Risk scoring** — a combined, interpretable score across environmental, resource, and population pressure
- **Sustainability modeling** — consumption vs. replenishment for water, minerals, and land
- **Forecasting** — regression, moving averages, and time-series methods to project future conditions
- **Route optimization** — weighted shortest-path / multi-objective algorithms (e.g. Dijkstra/A*-style scoring) across cost, environment, and social impact
- **Site suitability scoring** — weighted spatial criteria for industrial and infrastructure siting

Every score is broken down into its contributing factors, and every recommendation is traceable back to the specific problem that triggered it. Nothing is a black box — if the platform says *"Route B is preferred,"* it also explains *why*.

---

## 🔍 Data Honesty

This matters a lot to us. Every dataset in AIGES is explicitly labeled as one of:

- **Real** — verified external/government/satellite data
- **Simulated** — synthetic data created for demonstration where real data isn't accessible
- **Derived** — calculated from real or simulated inputs
- **Modelled** — produced by a forecasting/prediction process

We never present simulated numbers as fact, and we never fabricate official statistics. Where real datasets aren't available, we build clearly labeled, realistic demo data instead — because a credible tool has to be honest about what it actually knows.

Reference sources we look to for real data: ISRO/Bhuvan, India-WRIS, Forest Survey of India, CPCB, Census/open demographic data, OpenStreetMap, and NASA/ESA Earth observation datasets.

---

## 🎨 Design Philosophy

AIGES is deliberately **not** another generic dashboard or "AI-themed" website. The visual identity is meant to feel like:

**Earth + Data + Science + Decision + Future**

- The **map stays the central element** of the experience — never buried under UI.
- Color is used with intent: **green** = healthy, **amber** = warning, **red** = critical/severe, **blue** = water/resources.
- Information is revealed progressively — **What → Why → What Next → What Can We Do** — never dumped all at once.
- No neon gradients, glowing "AI" graphics, or empty visual noise. Every animation and visualization exists to communicate something real.

---

## 🛠 Tech Stack

> _Update this section with your team's actual implementation details._

- **Mapping/GIS:** MapLibre / Mapbox GL / Leaflet, GeoJSON, vector & raster tiles
- **3D & Motion:** Three.js, GSAP
- **Frontend:** _e.g. React / Next.js_
- **Backend:** _e.g. Node.js / Python (FastAPI)_
- **Data & Modeling:** _e.g. Python, pandas, scikit-learn for forecasting_
- **Data Sources:** ISRO/Bhuvan, India-WRIS, Forest Survey of India, CPCB, OpenStreetMap, NASA/ESA Earth observation data (real + clearly labeled simulated data)

---

## 🚀 Getting Started

> _Update these steps to match your actual repo structure._

```bash
# Clone the repository
git clone https://github.com/<your-org>/sustaina.git
cd sustaina

# Install dependencies
npm install

# Run the development server
npm run dev
```

Then open `http://localhost:3000` in your browser.

---

## 👥 Team

**Team Pentagon**
Joel Jacob Roji
Darren Samuel Dcruz
P Kamuel Shawn
Shreya Elizabeth Joseph
Michelle Devasia 

---

## 📄 License

> _Add your chosen license here (e.g. MIT)._

---

<p align="center">
  <strong>The future is not predetermined. We can choose where we build, how we develop —<br>and develop without destroying.</strong>
</p>
