from src.pipeline import create_rag_chain
import argparse
import logging as log

def parse_args():
    parser = argparse.ArgumentParser(description="Run the RAG chatbot.")
    parser.add_argument(
        "--rebuild-index",
        action="store_true",
        help="Rebuild the FAISS index from documents instead of loading it from disk."
    )
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    log.info("Starting RAG chatbot...")
    log.info("Loading or building FAISS index...")
    
    try:
        rag_chain = create_rag_chain()
    except Exception as e:
        log.error("Failed to create RAG chain: %s", e)
        raise SystemExit("Exiting due to failure in creating RAG chain.")
        
    log.info("RAG chatbot is ready. Type your questions below (type 'exit' or 'quit' to stop).")
        
    while True:
        try:
            question = input("You: ").strip()
            if question.lower() in ["exit", "quit"]:
                print("Bye!")
                break
            if not question:
                continue

            print("Thinking...")
            answer = rag_chain.invoke(question)
            print(f"Bot: {answer}\n")
        except KeyboardInterrupt:
            print("\nBye!")
            break
        except Exception as e:
            import traceback
            traceback.print_exc()  # in toàn bộ stack trace
            print(f"Error: {e}")
            print("Please try again or check your API key/internet connection.\n")


if __name__ == "__main__":
    main()