import os
from dotenv import load_dotenv
from orchestrator.scheduler import run_daily_pipeline

load_dotenv()

if __name__ == "__main__":
    print("="*60)
    print("ALGARVE É UM - END-TO-END PIPELINE MOCK TRIGGER")
    print("="*60)
    
    if not os.getenv("TAVILY_API_KEY") or not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️ WARNING: API Keys are missing in your .env file.")
        print("Please configure .env before triggering a real run.")
        print("="*60)
        
    print("Triggering the orchestrator pipeline manually...\n")
    try:
        run_daily_pipeline()
        print("\nPipeline execution sequence commanded. Check logs for details.")
    except Exception as e:
        print(f"\nPipeline failed during execution: {e}")
