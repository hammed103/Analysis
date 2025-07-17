#!/usr/bin/env python3
"""
Script to split work.csv into smaller chunks for GitHub deployment
"""

import pandas as pd
import os
import math

def split_csv_file(input_file='work.csv', output_dir='data', chunk_size=5000):
    """
    Split a large CSV file into smaller chunks
    
    Args:
        input_file (str): Path to the input CSV file
        output_dir (str): Directory to save the split files
        chunk_size (int): Number of rows per chunk
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📊 Splitting {input_file} into chunks of {chunk_size} rows...")
    
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)
        total_rows = len(df)
        
        print(f"📈 Total rows in dataset: {total_rows:,}")
        
        # Calculate number of chunks needed
        num_chunks = math.ceil(total_rows / chunk_size)
        print(f"📁 Will create {num_chunks} chunk files")
        
        # Split the dataframe into chunks
        for i in range(num_chunks):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, total_rows)
            
            # Get chunk
            chunk_df = df.iloc[start_idx:end_idx]
            
            # Create filename
            chunk_filename = f"work_chunk_{i+1:03d}.csv"
            chunk_path = os.path.join(output_dir, chunk_filename)
            
            # Save chunk
            chunk_df.to_csv(chunk_path, index=False)
            
            print(f"✅ Created {chunk_filename}: {len(chunk_df):,} rows")
        
        # Create a metadata file with information about the chunks
        metadata = {
            'original_file': input_file,
            'total_rows': total_rows,
            'chunk_size': chunk_size,
            'num_chunks': num_chunks,
            'chunk_files': [f"work_chunk_{i+1:03d}.csv" for i in range(num_chunks)]
        }
        
        metadata_path = os.path.join(output_dir, 'chunks_metadata.json')
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"📋 Created metadata file: {metadata_path}")
        print(f"🎉 Successfully split {input_file} into {num_chunks} chunks in {output_dir}/")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Error: {input_file} not found")
        return False
    except Exception as e:
        print(f"❌ Error splitting file: {e}")
        return False

def combine_chunks(data_dir='data', output_file='combined_work.csv'):
    """
    Combine split CSV chunks back into a single file
    
    Args:
        data_dir (str): Directory containing the chunk files
        output_file (str): Path for the combined output file
    """
    
    print(f"🔄 Combining chunks from {data_dir}/...")
    
    try:
        # Look for chunk files
        chunk_files = []
        for filename in os.listdir(data_dir):
            if filename.startswith('work_chunk_') and filename.endswith('.csv'):
                chunk_files.append(filename)
        
        if not chunk_files:
            print(f"❌ No chunk files found in {data_dir}/")
            return False
        
        # Sort chunk files to ensure correct order
        chunk_files.sort()
        print(f"📁 Found {len(chunk_files)} chunk files")
        
        # Read and combine chunks
        combined_df = pd.DataFrame()
        
        for chunk_file in chunk_files:
            chunk_path = os.path.join(data_dir, chunk_file)
            chunk_df = pd.read_csv(chunk_path)
            combined_df = pd.concat([combined_df, chunk_df], ignore_index=True)
            print(f"✅ Added {chunk_file}: {len(chunk_df):,} rows")
        
        # Save combined file
        combined_df.to_csv(output_file, index=False)
        
        print(f"🎉 Successfully combined {len(chunk_files)} chunks into {output_file}")
        print(f"📊 Total rows in combined file: {len(combined_df):,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error combining chunks: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "combine":
        # Combine mode
        combine_chunks()
    else:
        # Split mode (default)
        if os.path.exists('work.csv'):
            split_csv_file()
        else:
            print("❌ work.csv not found. Please ensure the file exists in the current directory.")
