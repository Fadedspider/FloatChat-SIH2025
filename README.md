
#  FloatChat — AI Conversational System for ARGO Float Data (SIH 2025)

FloatChat is an **AI-driven conversational interface** designed to interact with, explore, and extract insights from **oceanographic ARGO float datasets**.
It is developed as part of the **Smart India Hackathon (SIH) 2025** ecosystem and includes backend APIs, data processing, visualization dashboards, and a user-friendly chat interface for scientific and research use.

---

##  Project Overview

ARGO floats are autonomous instruments that collect critical ocean data such as temperature, salinity, and currents. FloatChat aims to:

* 🔍 **Retrieve** ARGO float data automatically
* 🧩 **Process & store** large ocean datasets
* 💬 **Provide conversational AI access** to data via natural language
* 📊 **Visualize data** through dashboards and tools
* 📡 **Serve researchers, students, and scientists** with an interactive interface

---

## 📁 Repository Structure

```
.
├── api/                       # Backend API for querying and serving model responses
├── data/processed/            # Cleaned and processed ARGO float data
├── db/                        # Database storage for datasets
├── docs/                      # Project documentation and design notes
├── nlp/                       # Natural Language Processing modules
├── notebooks/                 # Experiment notebooks, visualization, EDA
├── ocean-dashboard/src/       # Web dashboard code
├── scripts/                   # Helper scripts for data pipeline
├── streamlit_app/             # Chat or visualization UI
├── ai_chatbot_server.py       # Main AI chat server entry point
├── docker-compose.yml         # Deployment automation
├── requirements.txt           # Python dependencies
└── README.md                  # (This file)
```

---

## 🚀 Features

### 💬 AI Chatbot Interface

Interact with ARGO float data using natural language questions such as:

* *“Show me the salinity variation across 2023.”*
* *“Summarize the temperature trends in the North Pacific.”*

The conversational engine processes queries, retrieves relevant data, and returns readable insights.

---

### 🧪 Data Pipeline & Processing

Scripts and modules to:

* Ingest raw ARGO float datasets
* Clean and transform into usable formats
* Store in structured databases
* Optimize for queries and visualization

---

### 🖥️ Interactive Dashboards

A dashboard UI (built with modern front-end frameworks) allows users to:

* Browse float trajectories
* Visualize metrics (temperature, pressure, etc.)
* Integrate map and chart views

---

### 🔌 Backend Services

Includes API and server code using Python frameworks to serve:

* AI responses for FloatChat
* Data queries
* Real-time updates

---

## 🛠️ Installation

### 📦 Requirements

Clone the repository:

```bash
git clone https://github.com/Fadedspider/FloatChat-SIH2025.git
cd FloatChat-SIH2025
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 🚀 Run Backend Server

```bash
python ai_chatbot_server.py
```

### 🌍 Run UI (Streamlit / Dashboard)

Depending on your folder setup (e.g., in `streamlit_app/`):

```bash
streamlit run streamlit_app/main.py
```
