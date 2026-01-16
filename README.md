# 🏷️ Pricer
AI Driven Multi Agent Deal Analyzer for Indian Ecommerce  
Dynamic Price Estimation and Autonomous Deal Intelligence

Pricer is an automated multi agent AI framework that scans Indian ecommerce platforms, analyzes product descriptions, predicts INR prices using multiple AI systems, and identifies the strongest deal opportunities. It also stores historical deal data and displays results in a real time dashboard.
![WhatsApp Image 2026-01-17 at 2 46 00 AM](https://github.com/user-attachments/assets/79499588-678d-4584-8026-82f4d6d282b8)
![WhatsApp Image 2026-01-17 at 2 45 12 AM](https://github.com/user-attachments/assets/e07b570e-bba7-48d8-a767-a8864a7ce881)
![WhatsApp Image 2026-01-17 at 2 45 16 AM](https://github.com/user-attachments/assets/9dfc4531-6915-4093-bb7c-d285baf59745)
![WhatsApp Image 2026-01-17 at 2 45 45 AM](https://github.com/user-attachments/assets/ada828bd-9965-49cf-9ec6-63826befda7d)
![WhatsApp Image 2026-01-17 at 2 45 53 AM](https://github.com/user-attachments/assets/880e8168-e4f2-4868-bd7b-0498b2424ca2)
![WhatsApp Image 2026-01-17 at 2 45 36 AM](https://github.com/user-attachments/assets/8c50e1cd-1006-4ec8-abf9-40ba0fd160de)
![WhatsApp Image 2026-01-17 at 2 46 27 AM](https://github.com/user-attachments/assets/0b89e509-0a55-439d-a5f7-064e7310ff96)




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

