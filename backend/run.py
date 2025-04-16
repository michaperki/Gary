import os
import logging
from dotenv import load_dotenv
from api.app import create_app

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Create Flask application
    app = create_app()
    
    # Set up port
    port = int(os.environ.get('PORT', 5000))
    
    # Run application
    logger.info(f"Starting application on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
