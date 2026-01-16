# 🏷️ Pricer
AI Driven Multi Agent Deal Analyzer for Indian Ecommerce  
Dynamic Price Estimation and Autonomous Deal Intelligence

Pricer is an automated multi agent AI framework that scans Indian ecommerce platforms, analyzes product descriptions, predicts INR prices using multiple AI systems, and identifies the strongest deal opportunities. It also stores historical deal data and displays results in a real time dashboard.
<img width="1600" height="809" alt="image" src="https://github.com/user-attachments/assets/38ade379-1e1d-4a71-94e0-fe989ec53271" />
<img width="1600" height="802" alt="image" src="https://github.com/user-attachments/assets/95e24d1c-8d74-4434-aab8-9627d3fd4106" />
<img width="1600" height="505" alt="image" src="https://github.com/user-attachments/assets/193ef3cf-c53a-4b7b-b5aa-9a9466932b3a" />
<img width="1600" height="810" alt="image" src="https://github.com/user-attachments/assets/19a15ce7-b6cd-42d5-8f87-9459009659df" />
<img width="1600" height="768" alt="image" src="https://github.com/user-attachments/assets/c37398a2-4827-4616-9ede-93e7a29119f7" />


---


## Features

- Automated scanning of Indian ecommerce deal sources
- AI powered INR price prediction
- Multi model ensemble combining LLMs and ML models
- Push notifications for best deals
- Local LLaMA inference through Ollama
- Historical memory of past deals
- Clean Gradio dashboard with logs and vectors

---

## Indian Deal Sources


- 📦 Desidime global deals  
- 🛍️ Amazon India  
- 🚀 Flipkart  
- 🔌 Reliance Digital  
- 🏷️ Tata Cliq  
- 🖥️ Croma  
- 👗 Ajio  
- 👟 Myntra  
- 💄 Nykaa  
- 🎮 Reddit India deal communities  

---

## 🧩 System Architecture

### 🔍 Scanner Agent  
Fetches RSS feeds, cleans descriptions, extracts product summaries.

### 🎯 Specialist Agent  
Runs a fine tuned remote pricing model using Modal.

### 🦙 Frontier Agent  
Uses local LLaMA via Ollama to generate price estimates.

### 🌲 Random Forest Agent  
A machine learning model trained on embeddings of real products.

### 🔗 Ensemble Agent  
Aggregates predictions from all agents into one INR estimate.

### 🧮 Planning Agent  
Computes discount and selects the best opportunity.

### 📬 Messaging Agent  
Sends push notifications for valuable deals.

---

## Technologies Used

- Python  
- LLaMA models (Ollama)  
- Modal GPU inference  
- Chroma vector DB  
- Sentence Transformers  
- Random Forest  
- Gradio UI  
- RSS parsing  
- Pydantic structured outputs  

---

## Installation

Clone the repo:

```bash
git clone https://github.com/AdityaAdi07/Pricer-AI-Driven-Multi-Agent-Deal-Analyzer-with-Dynamic-Price-Estimatio.git 

pip install -r requirements.txt

ollama serve
ollama run llama3.2

python price_right_final.py
```

## How Price Estimation Works

Deals are fetched and cleaned from RSS feeds.

Scanner Agent summarizes product descriptions.

Three independent models generate price estimates.

Ensemble Agent merges them into a final INR estimate.

Planning Agent computes the discount.

Best deal (if valuable) is sent as a notification.

Memory JSON is updated automatically.

