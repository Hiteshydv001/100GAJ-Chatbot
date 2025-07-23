# build_cache.py

import logging
from app.core.engine import get_chat_engine
from app.core.tools.api_property_search import _fetch_all_data

# This script is for running the expensive, one-time setup tasks locally.
# It generates the 'cache/' directory which you will then commit to Git.
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("--- Starting local cache build process... ---")
    
    # This will build and save the LlamaIndex vector store to the ./cache directory
    print("Building and caching the LlamaIndex engine...")
    get_chat_engine()
    print("Engine cached successfully.")
    
    # This will fetch and cache the property data in memory just to confirm it works
    print("Fetching property data to warm up cache...")
    _fetch_all_data()
    print("Property data fetched.")

    print("\n--- Local cache build process complete. ---")
    print("The './cache' directory is now ready to be committed to Git.")
    print("Make sure your .gitignore file does NOT ignore the 'cache/' directory.")