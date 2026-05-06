# AI Financial Assistant

## Overview
A Streamlit-based AI-powered expense tracker that helps users manage spending, stay within budget, and achieve savings goals.  
It combines deterministic financial calculations with AI-generated insights for better decision-making.

---

## Features
- Expense tracking with categories  
- Monthly budget and savings goal  
- Daily spending recommendations  
- Overspending detection  
- AI-based financial advice (Ollama – Phi3)  
- Category-wise bar chart visualization  

---

## Tech Stack
- Python  
- Streamlit  
- Pandas  
- Ollama (Local AI - Phi3 model)  

---

## How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/vaishnavi-cseds24/ai-financial-assistant.git
   cd ai-financial-assistant
2. Install dependencies:
    pip install -r requirements.txt
3. Run the application:
    streamlit run app.py
4. Make sure Ollama is running with the Phi3 model:
    ollama run phi3        