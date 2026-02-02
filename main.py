import argparse
from config import Config
from rag_engine import RAGEngine

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--init', action='store_true', help="Initialize Vector DB")
    args = parser.parse_args()

    rag = RAGEngine()

    if args.init:
        print("⚙️  Initializing Database...")
        rag.initialize_database(Config.PDF_PATH, force=True)
        print("✅ Done! You can now run 'streamlit run app.py'")
    else:
        print("Run with --init first, or use 'streamlit run app.py'")

if __name__ == "__main__":
    main()