import logging
import subprocess
from datetime import datetime
import os
from scrape.main import ClinicalTrialsScraper  # Assuming your scraper script is saved as 'your_scraper_script.py'

# --- Configuration ---
LOG_FILE = f"refresh_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
SCRAPED_DATA_FILENAME = f"clinical_trials_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
VECTOR_DB_REBUILD_SCRIPT = "backend/rebuild_vector_db.py"  # Ensure this path is correct
VECTOR_DB_PATH = "./backend/vector_db"  # Adjust if your vector database is in a different location
VECTOR_DB_TYPE = "transformer"  # Assuming you're using the transformer type
EMBEDDING_MODEL = "all-MiniLM-L6-v2" # Or your preferred model

# --- Logging Setup ---
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s'
)
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def refresh_clinical_trials_db():
    """
    Scrapes clinical trial data, saves it, and rebuilds the vector database.
    """
    logger.info("Starting clinical trial database refresh process.")

    # --- Step 1: Scrape Clinical Trial Data ---
    logger.info("Initiating data scraping...")
    try:
        scraper = ClinicalTrialsScraper()
        all_studies = scraper.scrape_all_studies()
        logger.info(f"Scraped a total of {len(all_studies)} studies.")

        if all_studies:
            logger.info(f"Saving scraped data to: {SCRAPED_DATA_FILENAME}")
            scraper.save_to_json(filename=SCRAPED_DATA_FILENAME)
            logger.info("Scraped data saved successfully.")
        else:
            logger.warning("No clinical trials data was scraped.")
            return

    except Exception as e:
        logger.error(f"An error occurred during scraping: {e}", exc_info=True)
        return

    # --- Step 2: Rebuild the Vector Database ---
    logger.info("Initiating vector database rebuild...")
    try:
        command = [
            "python",
            VECTOR_DB_REBUILD_SCRIPT,
            "--db-type", VECTOR_DB_TYPE,
            "--db-path", VECTOR_DB_PATH,
            "--model-name", EMBEDDING_MODEL,
            "--trials-file", SCRAPED_DATA_FILENAME,
            "--file-type", "json"
        ]
        logger.info(f"Executing command: {' '.join(command)}")

        # Execute the rebuild script as a subprocess
        process = subprocess.run(command, capture_output=True, text=True, check=True)

        logger.info("Vector database rebuild completed successfully.")
        logger.debug(f"Rebuild script output:\n{process.stdout}")
        if process.stderr:
            logger.error(f"Rebuild script errors:\n{process.stderr}")

        # Optionally, you can delete the scraped data file after successful rebuild
        # os.remove(SCRAPED_DATA_FILENAME)
        # logger.info(f"Deleted temporary data file: {SCRAPED_DATA_FILENAME}")

    except FileNotFoundError:
        logger.error(f"Error: The vector database rebuild script '{VECTOR_DB_REBUILD_SCRIPT}' was not found.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during vector database rebuild. Command failed with exit code {e.returncode}")
        logger.error(f"Rebuild script output:\n{e.stdout}")
        logger.error(f"Rebuild script errors:\n{e.stderr}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during vector database rebuild: {e}", exc_info=True)

    logger.info("Clinical trial database refresh process finished.")

if __name__ == "__main__":
    refresh_clinical_trials_db()
