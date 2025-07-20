#!/usr/bin/env python3
"""
Chunk the main CSV file into smaller pieces for GitHub compatibility.
GitHub has a 100MB file size limit, so we need to split large files.
"""

import pandas as pd
import os
from pathlib import Path


def chunk_data():
    """Chunk the main CSV file into GitHub-compatible sizes (under 100MB each)."""

    # Input file
    input_file = "ev_ads_complete_with_images_and_gender_20250720_100525.csv"
    output_dir = Path("Data")

    print(f"📊 Loading data from {input_file}...")

    # Load the main dataset
    try:
        df = pd.read_csv(input_file)
        print(f"✅ Loaded {len(df):,} total records")
    except FileNotFoundError:
        print(f"❌ Error: {input_file} not found!")
        return

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    # Get unique vehicle models
    vehicles = df["primary_vehicle"].value_counts()
    print(f"\n📋 Found {len(vehicles)} unique vehicle models")
    print("Top 10 vehicles by ad count:")
    print(vehicles.head(10))

    # Define our target vehicles for focused analysis
    target_vehicles = [
        "Hyundai Ioniq 5",
        "VW ID.4",
        "Tesla Model Y",
        "Audi Q4 e-tron",
        "BMW iX1",
        "BMW iX3",
    ]

    print(f"\n🎯 Chunking data by vehicle model...")

    # Create chunks for target vehicles
    target_data = []
    for vehicle in target_vehicles:
        vehicle_df = df[df["primary_vehicle"] == vehicle].copy()
        if len(vehicle_df) > 0:
            # Clean filename
            filename = vehicle.replace(" ", "_").replace(".", "").replace("/", "_")
            output_file = output_dir / f"{filename}.csv"

            # Save chunk
            vehicle_df.to_csv(output_file, index=False)
            target_data.append(vehicle_df)

            print(f"  ✅ {vehicle}: {len(vehicle_df):,} ads → {output_file}")
        else:
            print(f"  ⚠️  {vehicle}: No ads found")

    # Create a combined target vehicles file
    if target_data:
        combined_target = pd.concat(target_data, ignore_index=True)
        target_file = output_dir / "target_vehicles_combined.csv"
        combined_target.to_csv(target_file, index=False)
        print(
            f"\n🎯 Combined target vehicles: {len(combined_target):,} ads → {target_file}"
        )

    # Create chunks for other vehicles (group smaller ones together)
    other_vehicles = df[~df["primary_vehicle"].isin(target_vehicles)].copy()
    if len(other_vehicles) > 0:
        # Group by country to create manageable chunks
        countries = other_vehicles["primary_country"].unique()

        print(f"\n🌍 Chunking other vehicles by country...")
        for country in countries:
            country_df = other_vehicles[
                other_vehicles["primary_country"] == country
            ].copy()
            if len(country_df) > 0:
                filename = f"other_vehicles_{country.replace(' ', '_')}.csv"
                output_file = output_dir / filename
                country_df.to_csv(output_file, index=False)
                print(
                    f"  ✅ Other vehicles in {country}: {len(country_df):,} ads → {output_file}"
                )

    # Create a metadata file
    metadata = {
        "total_records": len(df),
        "target_vehicles": len(combined_target) if target_data else 0,
        "other_vehicles": len(other_vehicles),
        "countries": df["primary_country"].unique().tolist(),
        "vehicle_models": df["primary_vehicle"].value_counts().to_dict(),
        "chunk_files": [f.name for f in output_dir.glob("*.csv")],
    }

    metadata_file = output_dir / "metadata.json"
    import json

    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n📋 Created metadata file: {metadata_file}")

    # Summary
    print(f"\n🎉 Data chunking complete!")
    print(f"📁 Output directory: {output_dir}")
    print(f"📊 Total files created: {len(list(output_dir.glob('*.csv')))}")
    print(
        f"💾 Target vehicle ads: {len(combined_target):,}"
        if target_data
        else "💾 No target vehicle data found"
    )

    # Show disk usage
    total_size = sum(f.stat().st_size for f in output_dir.glob("*"))
    print(f"💿 Total size: {total_size / (1024*1024):.1f} MB")


if __name__ == "__main__":
    chunk_data()
