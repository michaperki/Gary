# load_trials.py
import os
import argparse
from minimal_vector_db import MinimalVectorDB

def main():
    parser = argparse.ArgumentParser(description='Load and index clinical trials data')
    parser.add_argument('--data_path', type=str, required=True, help='Path to the data file')
    parser.add_argument('--file_type', type=str, default='json', choices=['json', 'csv'], 
                        help='Type of data file (json or csv)')
    args = parser.parse_args()
    
    # Initialize the vector database
    vector_db = MinimalVectorDB(db_directory="./vector_db")
    
    # Check if the data file exists
    if not os.path.exists(args.data_path):
        print(f"Error: Data file not found at {args.data_path}")
        return
    
    # Load the data
    print(f"Loading data from {args.data_path}...")
    if args.file_type.lower() == 'json':
        trials = vector_db.load_trials_from_json(args.data_path)
    else:
        trials = vector_db.load_trials_from_csv(args.data_path)
    
    print(f"Loaded {len(trials)} trials. Processing and indexing...")
    
    # Process and index the trials
    vector_db.process_and_index_trials(trials)
    
    print("Done! The vector database has been updated.")

if __name__ == "__main__":
    main()
