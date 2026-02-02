Here is a professional **README.md** file for your project. You can copy and paste this directly into your repository.

---

# 🤖 Agentic AI RAG Chatbot with Reinforcement Learning

**Developed by Likhitha Bollu**

An intelligent **Retrieval-Augmented Generation (RAG)** chatbot designed to analyze complex documents (like `Ebook-Agentic-AI.pdf`) and answer user queries with precision. It features a **Human-in-the-Loop Reinforcement Learning** system that allows users to teach the bot new rules and correct answers in real-time.

---

## 🚀 Key Features

* **Advanced RAG Engine:** Uses **Google Gemini 2.0 Pro** to synthesize answers from PDF documents with page-level citations.
* **Self-Learning (RL):** If the bot makes a mistake, you can provide feedback. The system "learns" this correction and applies it to future queries automatically.
* **Table Intelligence:** Automatically detects requests for lists or comparisons and formats data into clean Markdown tables.
* **Dual Interface:**
* **Streamlit Web UI:** For interactive chatting and teaching.
* **CLI:** For database management and initialization.



---

## 🛠️ Installation & Setup

Follow these steps to set up the project on your local machine.

### 1. Clone the Repository

Open your terminal or command prompt and run:

```bash
git clone https://github.com/likhithabollu/agentic-ai-rag.git
cd agentic-ai-rag

```

*(Note: Replace the URL with your actual repository link if you have pushed it to GitHub).*

### 2. Install Dependencies

Ensure you have Python 3.10+ installed. Then run:

```bash
pip install -r requirements.txt

```

### 3. Configure Environment Variables

Create a file named `.env` in the root directory (same folder as `main.py`). Add your Google API key:

```ini
GOOGLE_API_KEY=your_actual_api_key_here
MODEL_NAME=gemini-2.0-pro
CHUNK_SIZE=2500
CHUNK_OVERLAP=500

```

### 4. Add the PDF

Ensure your source document is named correctly and placed in the root folder:

* File Name: **`Ebook-Agentic-AI.pdf`**

---

## ⚡ How to Run

You must initialize the knowledge base before running the chat application.

### Step 1: Initialize the Database

Run this command to read the PDF and build the vector search index:

```bash
python main.py --init

```

*Wait for the message: `✅ Done! You can now run 'streamlit run app.py'*`

### Step 2: Start the Chatbot

Launch the web interface:

```bash
python -m streamlit run app.py

```

The application will open automatically in your browser (usually at `http://localhost:8501`).

---

## 🧠 How to Teach the Bot (RL Loop)

1. **Ask a Question** (e.g., *"What is Agentic AI?"*).
2. **Review the Answer.**
3. If the answer is missing details:
* Go to the **Feedback Panel** at the bottom.
* Click **"Teach & Improve"**.
* Type your instruction (e.g., *"Include a bullet point list of benefits"*).
* Click **"Teach & Regenerate"**.


4. The bot will instantly regenerate the answer and **remember this rule** for next time!

---

## 📂 Project Structure

* **`app.py`**: The main frontend application (Streamlit).
* **`rag_engine.py`**: The logic core (Gemini + Retrieval).
* **`feedback_manager.py`**: Handles user corrections (Memory).
* **`main.py`**: CLI script for system initialization.
* **`config.py`**: Central configuration settings.
* **`table_parser.py`**: Utility for extracting data tables.

---
