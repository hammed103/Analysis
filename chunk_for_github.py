#!/usr/bin/env python3
"""
Chunk the main CSV file for GitHub compatibility.
GitHub has a 100MB file size limit, so we split large files into smaller chunks.
"""

import pandas as pd
import os
import json
from pathlib import Path

def chunk_for_github():
    """Split the main CSV file into GitHub-compatible chunks (under 100MB each)."""
    
    # Input file
    input_file = "ev_ads_complete_with_images_and_gender_20250720_100525.csv"
    output_dir = Path("Data")
    
    print(f"📊 Chunking {input_file} for GitHub...")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found!")
        return
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Check file size
    file_size_mb = os.path.getsize(input_file) / (1024 * 1024)
    print(f"📁 Original file size: {file_size_mb:.1f} MB")
    
    # Load the dataset
    print("📖 Loading dataset...")
    df = pd.read_csv(input_file)
    print(f"✅ Loaded {len(df):,} total records")
    
    # GitHub limit is 100MB, let's target 80MB chunks for safety
    target_chunk_size_mb = 80
    
    if file_size_mb <= target_chunk_size_mb:
        print(f"✅ File is under {target_chunk_size_mb}MB, copying to Data/ directory")
        output_file = output_dir / "ev_ads_data.csv"
        df.to_csv(output_file, index=False)
        chunk_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"📄 Copied to: {output_file} ({chunk_size_mb:.1f}MB)")
        
        # Create simple index
        index_data = {
            'total_records': len(df),
            'total_size_mb': chunk_size_mb,
            'chunk_files': ['ev_ads_data.csv'],
            'num_chunks': 1
        }
    else:
        print(f"📦 File is {file_size_mb:.1f}MB, splitting into chunks...")
        
        # Calculate number of chunks needed
        num_chunks = int(file_size_mb / target_chunk_size_mb) + 1
        rows_per_chunk = len(df) // num_chunks
        
        print(f"🔢 Creating {num_chunks} chunks with ~{rows_per_chunk:,} rows each")
        
        chunk_files = []
        
        # Create chunks
        for i in range(num_chunks):
            start_idx = i * rows_per_chunk
            if i == num_chunks - 1:  # Last chunk gets remaining rows
                end_idx = len(df)
            else:
                end_idx = (i + 1) * rows_per_chunk
            
            chunk_df = df.iloc[start_idx:end_idx].copy()
            chunk_file = output_dir / f"ev_ads_data_chunk_{i+1:02d}.csv"
            chunk_df.to_csv(chunk_file, index=False)
            chunk_files.append(chunk_file.name)
            
            # Check chunk size
            chunk_size_mb = os.path.getsize(chunk_file) / (1024 * 1024)
            print(f"  ✅ Chunk {i+1}: {len(chunk_df):,} rows, "
                  f"{chunk_size_mb:.1f}MB → {chunk_file.name}")
        
        # Create index data
        index_data = {
            'total_records': len(df),
            'total_size_mb': file_size_mb,
            'chunk_files': chunk_files,
            'num_chunks': num_chunks
        }
    
    # Add metadata
    index_data.update({
        'columns': df.columns.tolist(),
        'sample_vehicles': df['primary_vehicle'].value_counts().head(10).to_dict(),
        'sample_countries': df['primary_country'].value_counts().head(10).to_dict()
    })
    
    # Save index file
    index_file = output_dir / "data_index.json"
    with open(index_file, 'w') as f:
        json.dump(index_data, f, indent=2)
    
    print(f"\n📋 Created index file: {index_file}")
    
    # Summary
    print(f"\n🎉 Chunking complete!")
    print(f"📁 Output directory: {output_dir}")
    print(f"📊 Total chunks: {index_data['num_chunks']}")
    print(f"💾 Total records: {index_data['total_records']:,}")
    
    # Show disk usage
    total_size = sum(f.stat().st_size for f in output_dir.glob("*.csv"))
    print(f"💿 Total size: {total_size / (1024*1024):.1f} MB")
    
    # GitHub compatibility check
    oversized_files = []
    for csv_file in output_dir.glob("*.csv"):
        size_mb = csv_file.stat().st_size / (1024 * 1024)
        if size_mb > 100:
            oversized_files.append((csv_file.name, size_mb))
    
    if oversized_files:
        print(f"\n⚠️  WARNING: {len(oversized_files)} files exceed 100MB GitHub limit:")
        for filename, size in oversized_files:
            print(f"  - {filename}: {size:.1f}MB")
    else:
        print(f"\n✅ All files are under 100MB - GitHub compatible!")

if __name__ == "__main__":
    chunk_for_github()
