import pandas as pd
import numpy as np
import re
import os
import glob
import json
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter


class EVAdvertAnalyzer:
    """
    Electric Vehicle Advertisement Analyzer for competitor analysis
    Focuses on Portugal, Germany, and Netherlands markets
    """

    def __init__(self, csv_path: str):
        """Initialize with the path to the CSV data file or directory"""
        self.csv_path = csv_path
        self.df = None
        # Normalize country codes - combine similar references
        self.target_markets = ["Portugal", "PT", "Germany", "DE", "Netherlands", "NL"]
        self.target_vehicles = [
            "Hyundai Ioniq 5",
            "VW ID.4",
            "Renault Megane E-Tech",
            "Audi Q4 e-tron",
            "Tesla Model Y",
        ]
        self.load_data()

    def load_data(self):
        """Load and preprocess the CSV data"""
        try:
            # Check if path is a directory (for split data)
            if os.path.isdir(self.csv_path):
                self._load_from_directory()
            else:
                # Load single file
                self.df = pd.read_csv(self.csv_path)
                print(f"Loaded {len(self.df)} records from {self.csv_path}")

            self._preprocess_data()
        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def _load_from_directory(self):
        """Load data from multiple CSV chunks in a directory"""
        import glob
        import json

        # Initialize empty DataFrame
        self.df = pd.DataFrame()

        # Check for metadata file first
        metadata_path = os.path.join(self.csv_path, "chunks_metadata.json")
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)

                # Load chunks in order
                for chunk_file in metadata["chunk_files"]:
                    chunk_path = os.path.join(self.csv_path, chunk_file)
                    if os.path.exists(chunk_path):
                        chunk_df = pd.read_csv(chunk_path)
                        self.df = pd.concat([self.df, chunk_df], ignore_index=True)
                        print(f"Loaded chunk {chunk_file}: {len(chunk_df)} records")

                print(
                    f"Loaded {len(self.df)} total records from {len(metadata['chunk_files'])} chunks"
                )
                return
            except Exception as e:
                print(f"Error loading from metadata: {e}")
                # Fall back to loading all CSV files

        # Find all CSV files in the directory
        csv_files = glob.glob(os.path.join(self.csv_path, "*.csv"))

        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {self.csv_path}")

        # Load each CSV file and concatenate
        for csv_file in sorted(csv_files):
            # Skip metadata file
            if os.path.basename(csv_file) == "chunks_metadata.json":
                continue

            chunk_df = pd.read_csv(csv_file)
            self.df = pd.concat([self.df, chunk_df], ignore_index=True)
            print(f"Loaded {os.path.basename(csv_file)}: {len(chunk_df)} records")

        print(f"Loaded {len(self.df)} total records from {len(csv_files)} files")

    def _preprocess_data(self):
        """Preprocess the data for analysis"""
        # Convert date columns
        if "start_date" in self.df.columns:
            self.df["start_date"] = pd.to_datetime(
                self.df["start_date"], errors="coerce"
            )
        if "end_date" in self.df.columns:
            self.df["end_date"] = pd.to_datetime(self.df["end_date"], errors="coerce")

        # Use the country column if available, otherwise fall back to targeted_countries_list
        if "country" in self.df.columns:
            self.df["countries_clean"] = self.df["country"].fillna("")
        elif "targeted_countries_list" in self.df.columns:
            self.df["countries_clean"] = self.df["targeted_countries_list"].fillna("")

        # Use matched_cars column if available, otherwise fall back to matched_car_models
        if "matched_cars" in self.df.columns:
            self.df["vehicle_model"] = self.df["matched_cars"].fillna("Unknown")
        elif "matched_car_models" in self.df.columns:
            self.df["vehicle_model"] = self.df["matched_car_models"].fillna("Unknown")
        else:
            self.df["vehicle_model"] = "Unknown"

        # Filter for target markets and vehicles
        self.df_filtered = self._filter_target_data()
        print(
            f"Filtered to {len(self.df_filtered)} records for target markets and vehicles"
        )

    def _filter_target_data(self) -> pd.DataFrame:
        """Filter data for target markets and vehicles"""
        filtered_df = self.df.copy()

        # Filter for target markets - use country column if available
        if "country" in filtered_df.columns:
            # Direct filtering using country column
            market_mask = filtered_df["country"].isin(
                ["Portugal", "Germany", "Netherlands"]
            )
            filtered_df = filtered_df[market_mask]
        elif "targeted_countries_list" in filtered_df.columns:
            # Fallback to targeted_countries_list
            market_mask = filtered_df["targeted_countries_list"].str.contains(
                "|".join(self.target_markets), case=False, na=False
            )
            filtered_df = filtered_df[market_mask]

        # Filter for target vehicles
        if "vehicle_model" in filtered_df.columns:
            vehicle_mask = filtered_df["vehicle_model"].isin(self.target_vehicles)
            filtered_df = filtered_df[vehicle_mask]

        # Filter out low-quality/non-informative content
        summary_column = (
            "openai_analysis"
            if "openai_analysis" in filtered_df.columns
            else "openai_summary"
        )
        if summary_column in filtered_df.columns:
            quality_mask = filtered_df[summary_column].apply(self._is_quality_content)
            filtered_df = filtered_df[quality_mask]

        return filtered_df

    def _normalize_country_name(self, country_text: str) -> str:
        """Normalize country names to standard format"""
        if not country_text:
            return ""

        country_lower = country_text.lower()

        # Normalize to standard names
        if any(x in country_lower for x in ["portugal", "pt"]):
            return "Portugal"
        elif any(x in country_lower for x in ["germany", "de", "deutschland"]):
            return "Germany"
        elif any(x in country_lower for x in ["netherlands", "nl", "nederland"]):
            return "Netherlands"

        return country_text

    def _is_quality_content(self, summary_text: str) -> bool:
        """Filter out low-quality or non-informative content"""
        if pd.isna(summary_text) or not summary_text.strip():
            return False

        summary_lower = str(summary_text).lower()

        # Patterns that indicate low-quality or non-informative content
        low_quality_patterns = [
            "does not include specific details",
        ]

        # Check if content contains low-quality indicators
        for pattern in low_quality_patterns:
            if pattern in summary_lower:
                return False

        # Require minimum content length (exclude very short summaries)
        if len(summary_text.strip()) < 30:  # Reduced from 50 to 30
            return False

        # Require some substantive content (not just metadata) - LESS RESTRICTIVE
        substantive_indicators = [
            "feature",
            "performance",
            "range",
            "interior",
            "exterior",
            "technology",
            "safety",
            "design",
            "comfort",
            "efficiency",
            "battery",
            "charging",
            "driving",
            "experience",
            "capability",
            "innovation",
            "advanced",
            "premium",
            "luxury",
            "spacious",
            "powerful",
            "fast",
            "smooth",
            "quiet",
            "reliable",
            "eco-friendly",
            "sustainable",
            "modern",
            "sleek",
            "stylish",
            "car",
            "vehicle",
            "auto",
            "model",
            "brand",
            "new",
            "latest",
            "available",
            "offer",
            "features",
            "includes",
            "comes",
            "with",
        ]

        # Check if content has at least some substantive indicators - REDUCED REQUIREMENT
        substantive_count = sum(
            1 for indicator in substantive_indicators if indicator in summary_lower
        )
        if substantive_count < 1:  # Reduced from 2 to 1 substantive term
            return False

        return True

    def get_market_summary(self) -> Dict:
        """Get summary statistics by market (normalized)"""
        summary = {}

        # Use country column if available, otherwise fall back to targeted_countries_list
        for market in ["Portugal", "Germany", "Netherlands"]:
            if "country" in self.df_filtered.columns:
                # Direct filtering using country column
                market_data = self.df_filtered[self.df_filtered["country"] == market]
            else:
                # Fallback to targeted_countries_list with variations
                market_variations = []
                if market == "Portugal":
                    market_variations = ["Portugal", "PT"]
                elif market == "Germany":
                    market_variations = ["Germany", "DE"]
                elif market == "Netherlands":
                    market_variations = ["Netherlands", "NL"]

                # Combine data from all variations
                market_data = pd.DataFrame()
                for variation in market_variations:
                    variation_data = self.df_filtered[
                        self.df_filtered["targeted_countries_list"].str.contains(
                            variation, case=False, na=False
                        )
                    ]
                    market_data = pd.concat(
                        [market_data, variation_data]
                    ).drop_duplicates()

            if len(market_data) > 0:
                summary[market] = {
                    "total_ads": len(market_data),
                    "unique_vehicles": market_data["vehicle_model"].nunique(),
                    "unique_advertisers": market_data["page_name"].nunique(),
                    "date_range": {
                        "start": market_data["start_date"].min(),
                        "end": market_data["start_date"].max(),
                    },
                }

        return summary

    def get_vehicle_analysis(self) -> Dict:
        """Analyze advertisements by vehicle model"""
        vehicle_stats = {}

        for vehicle in self.df_filtered["vehicle_model"].unique():
            if pd.isna(vehicle) or vehicle == "Unknown":
                continue

            vehicle_data = self.df_filtered[
                self.df_filtered["vehicle_model"] == vehicle
            ]

            # Get market breakdown
            market_breakdown = {}
            if "country" in vehicle_data.columns:
                # Use country column directly
                for market in ["Portugal", "Germany", "Netherlands"]:
                    market_ads = vehicle_data[vehicle_data["country"] == market]
                    if len(market_ads) > 0:
                        market_breakdown[market] = len(market_ads)
            else:
                # Fallback to targeted_countries_list
                markets = ["Portugal", "Germany", "Netherlands", "PT", "DE", "NL"]
                for market in markets:
                    market_ads = vehicle_data[
                        vehicle_data["targeted_countries_list"].str.contains(
                            market, case=False, na=False
                        )
                    ]
                    if len(market_ads) > 0:
                        market_breakdown[market] = len(market_ads)

            vehicle_stats[vehicle] = {
                "total_ads": len(vehicle_data),
                "market_breakdown": market_breakdown,
                "advertisers": vehicle_data["page_name"].unique().tolist(),
                "avg_spend": (
                    vehicle_data["spend"].mean()
                    if "spend" in vehicle_data.columns
                    else 0
                ),
            }

        return vehicle_stats

    def analyze_features_mentioned(self) -> Dict:
        """Analyze features mentioned using structured sections from OpenAI summaries"""

        feature_analysis = defaultdict(lambda: defaultdict(int))

        for _, row in self.df_filtered.iterrows():
            # Prioritize openai_analysis column if available
            if "openai_analysis" in row and not pd.isna(row["openai_analysis"]):
                summary_text = str(row["openai_analysis"])
            elif "openai_summary" in row and not pd.isna(row["openai_summary"]):
                summary_text = str(row["openai_summary"])
            else:
                continue

            # Get vehicle model - use matched_cars if available
            if "matched_cars" in row and not pd.isna(row["matched_cars"]):
                vehicle = row["matched_cars"]
            else:
                vehicle = row["vehicle_model"]

            # Parse structured sections from the OpenAI analysis
            structured_sections = self._parse_all_structured_sections(summary_text)

            # Count features by category for this vehicle
            for section_name, section_content in structured_sections.items():
                # Skip sections that say "Not specified in the ad"
                if "not specified" in section_content.lower():
                    continue

                feature_category = self._categorize_section(section_name)

                # Only count meaningful feature categories (not "Other")
                if feature_category != "Other":
                    feature_analysis[vehicle][feature_category] += 1

        return dict(feature_analysis)

    def get_feature_mentions_detail(
        self, feature_category: str = None, vehicle_model: str = None
    ) -> List[Dict]:
        """Get detailed mentions using structured **Section:** format from OpenAI analysis"""

        detailed_mentions = []

        # Filter data
        data_to_analyze = self.df_filtered.copy()
        if vehicle_model and vehicle_model != "All":
            data_to_analyze = data_to_analyze[
                data_to_analyze["vehicle_model"] == vehicle_model
            ]

        for _, row in data_to_analyze.iterrows():
            summary_column = (
                "openai_analysis" if "openai_analysis" in row else "openai_summary"
            )
            if pd.isna(row.get(summary_column)):
                continue

            summary_text = str(row[summary_column])

            # Parse all structured sections from the OpenAI analysis
            structured_sections = self._parse_all_structured_sections(summary_text)

            # Filter sections based on feature category if specified
            for section_name, section_content in structured_sections.items():
                # If filtering by specific category, check if section matches
                if feature_category:
                    section_category = self._categorize_section(section_name)
                    if section_category != feature_category:
                        continue

                mention = {
                    "advertiser": row.get("page_name", "Unknown"),
                    "vehicle_model": row.get("vehicle_model", "Unknown"),
                    "matched_keyword": section_name,
                    "feature_category": self._categorize_section(section_name),
                    "relevant_text": section_content,
                    "full_summary": summary_text,
                    "source_platform": row.get("source_platform", "Unknown"),
                }
                detailed_mentions.append(mention)

        return detailed_mentions

    def _parse_all_structured_sections(self, summary: str) -> Dict[str, str]:
        """Parse all **Section:** content from OpenAI analysis using regex"""
        sections = {}

        if pd.isna(summary):
            return sections

        # Pattern to match **Theme:** followed by content until next ** or end
        pattern = r"\*\*([^*]+):\*\*\s*(.*?)(?=\*\*|$)"
        matches = re.findall(pattern, summary, re.DOTALL)

        for theme_name, content in matches:
            theme_name = theme_name.strip()
            content = content.strip()

            # Clean up extra newlines and spaces
            content = re.sub(r"\n+", " ", content)
            content = re.sub(r"\s+", " ", content)

            if theme_name and content:
                sections[theme_name] = content

        return sections

    def _categorize_section(self, section_name: str) -> str:
        """Map exact section names to our feature categories"""
        # Normalize the section name
        section_name = section_name.strip()

        # Direct mapping of exact section names
        section_mapping = {
            # Main sections
            "Brand & Product Focus": "Brand & Product Focus",
            "Brand & Vehicle Focus": "Brand & Product Focus",
            "Key Message/Slogan": "Key Message",
            "Key Message/Value Proposition": "Key Message",
            "Dealership/Advertiser": "Advertiser Info",
            # Feature sections
            "Range and Charging": "Range & Charging",
            "Battery and Range": "Range & Charging",
            "Charging": "Range & Charging",
            "Range": "Range & Charging",
            "Performance": "Performance",
            "Driving Experience": "Performance",
            "Power and Performance": "Performance",
            "Interior and Comfort": "Interior",
            "Interior": "Interior",
            "Comfort": "Interior",
            "Cabin": "Interior",
            "Infotainment & Audio": "Technology",
            "Technology": "Technology",
            "Tech Features": "Technology",
            "Safety & Assistance": "Safety",
            "Safety": "Safety",
            "Driver Assistance": "Safety",
            "Exterior Design": "Design",
            "Design": "Design",
            "Styling": "Design",
            "Appearance": "Design",
            "Eco-Friendly Features": "Eco-Friendly",
            "Environmental Impact": "Eco-Friendly",
            "Sustainability": "Eco-Friendly",
            "Price and Value": "Price",
            "Pricing": "Price",
            "Cost": "Price",
            "Affordability": "Price",
            # Other common sections
            "Connectivity and Digital Experience": "Technology",
            "Overall Theme": "Other",
            "Target Audience": "Other",
            "Visual Elements": "Design",
            "Ad Format": "Other",
        }

        # Return the mapped category or "Other" if not found
        return section_mapping.get(section_name, "Other")

    def _parse_structured_features(self, summary: str) -> Dict[str, str]:
        """Parse features from structured OpenAI summary format **Feature:** content"""
        features = {}

        # First try to extract structured features with ** format
        parts = summary.split("**")

        for i in range(len(parts) - 1):
            if ":" in parts[i]:
                # This might be a feature name
                feature_name = parts[i].strip()
                if feature_name and i + 1 < len(parts):
                    # Get the content after the feature name
                    feature_content = parts[i + 1].strip()
                    # Clean up the feature name (remove trailing colons)
                    clean_feature_name = feature_name.rstrip(":").strip()
                    if clean_feature_name and feature_content:
                        features[clean_feature_name] = feature_content

        # If no structured features found, fall back to keyword matching
        if not features:
            # Define feature keywords for matching
            feature_keywords = {
                "Range & Charging": [
                    "range",
                    "miles",
                    "km",
                    "distance",
                    "battery",
                    "charging",
                    "charge",
                    "charger",
                    "kw",
                    "kilowatt",
                    "fast charging",
                ],
                "Performance": [
                    "performance",
                    "acceleration",
                    "speed",
                    "power",
                    "horsepower",
                    "torque",
                    "handling",
                    "driving",
                    "motor",
                ],
                "Interior": [
                    "interior",
                    "cabin",
                    "seats",
                    "seating",
                    "comfort",
                    "spacious",
                    "space",
                    "room",
                    "luxury",
                    "materials",
                ],
                "Design": [
                    "design",
                    "style",
                    "aesthetic",
                    "appearance",
                    "exterior",
                    "look",
                    "sleek",
                    "beautiful",
                    "elegant",
                    "modern",
                ],
            }

            # Extract relevant sentences for each feature category
            summary_lower = summary.lower()
            sentences = summary.split(".")

            for category, keywords in feature_keywords.items():
                for keyword in keywords:
                    if keyword in summary_lower:
                        # Find sentences containing this keyword
                        relevant_sentences = []
                        for sentence in sentences:
                            if (
                                keyword in sentence.lower()
                                and len(sentence.strip()) > 10
                            ):
                                relevant_sentences.append(sentence.strip())

                        if relevant_sentences:
                            features[category] = ". ".join(relevant_sentences)
                            break  # Only one entry per category

        return features

    def _is_marketing_content(self, sentence_lower: str, keyword: str) -> bool:
        """Filter out metadata and boilerplate text to focus on actual marketing content"""

        # Common metadata and boilerplate patterns to exclude
        exclude_patterns = [
            "dealership/advertiser:",
            "see dealer for details",
            "dealer for details",
            "contact dealer",
            "visit dealer",
            "dealer information",
            "advertiser:",
            "brand & product focus:",
            "key message/slogan:",
            "overall theme:",
            "visual style:",
            "target audience:",
            "call-to-action:",
            "matches dealer pattern:",
            "dealer pattern:",
            "acting as the official",
            "official brand and advertiser",
            "the advertiser",
            "advertisement primarily promotes",
            "advertisement is focused on",
            "advertisement promotes",
            "the ad highlights",
            "the ad features",
            "targeting potential",
            "utm_campaign=",
            "utm_source=",
            "utm_medium=",
            "facebook.com/",
            "instagram.com/",
            "www.",
            "http",
            "learn more",
            "shop now",
            "call now",
            "subscribe",
        ]

        # Check if sentence contains excluded patterns
        for pattern in exclude_patterns:
            if pattern in sentence_lower:
                return False

        # For "deal" keyword, be more specific about what constitutes marketing content
        if keyword == "deal":
            # Only include if it's about actual deals/offers, not dealer references
            deal_marketing_indicators = [
                "special deal",
                "great deal",
                "best deal",
                "deal on",
                "deals available",
                "limited deal",
                "exclusive deal",
                "amazing deal",
                "hot deal",
                "deal of",
                "deal alert",
                "deal expires",
                "deal ends",
                "financing deal",
                "lease deal",
                "trade deal",
                "deal today",
                "deal now",
            ]

            # Check if it's actually about marketing deals
            for indicator in deal_marketing_indicators:
                if indicator in sentence_lower:
                    return True

            # If "deal" appears but no marketing indicators, likely metadata
            return False

        # For other keywords, exclude very short sentences (likely metadata)
        if len(sentence_lower.strip()) < 10:
            return False

        # Include sentence if it passes all filters
        return True

    def analyze_image_themes(self) -> Dict:
        """Analyze image themes from OpenAI summaries"""
        theme_keywords = {
            "City": ["city", "urban", "downtown", "street", "metropolitan"],
            "Country": [
                "country",
                "rural",
                "nature",
                "landscape",
                "outdoor",
                "mountain",
            ],
            "Interior Focus": ["interior", "cabin", "dashboard", "seats", "inside"],
            "Exterior Focus": ["exterior", "outside", "body", "design", "profile"],
            "Lifestyle": ["lifestyle", "family", "adventure", "journey", "experience"],
            "Commute": ["commute", "work", "daily", "traffic", "business"],
            "Luxury": ["luxury", "premium", "elegant", "sophisticated", "high-end"],
            "Sport": ["sport", "sporty", "dynamic", "performance", "athletic"],
        }

        theme_analysis = defaultdict(lambda: defaultdict(int))

        for _, row in self.df_filtered.iterrows():
            if pd.isna(row.get("openai_summary")):
                continue

            summary_text = str(row["openai_summary"]).lower()
            vehicle = row["vehicle_model"]

            for theme_category, keywords in theme_keywords.items():
                for keyword in keywords:
                    if keyword in summary_text:
                        theme_analysis[vehicle][theme_category] += 1
                        break

        return dict(theme_analysis)

    def analyze_tone_and_style(self) -> Dict:
        """Analyze tone and style from OpenAI summaries"""
        tone_keywords = {
            "Modern": ["modern", "contemporary", "current", "latest", "new"],
            "Innovative": [
                "innovative",
                "cutting-edge",
                "advanced",
                "breakthrough",
                "revolutionary",
            ],
            "Elegant": ["elegant", "sophisticated", "refined", "classy", "stylish"],
            "Energetic": ["energetic", "dynamic", "vibrant", "exciting", "powerful"],
            "Minimalist": ["minimalist", "clean", "simple", "sleek", "streamlined"],
            "Professional": ["professional", "business", "corporate", "formal"],
            "Friendly": ["friendly", "approachable", "welcoming", "warm", "inviting"],
        }

        tone_analysis = defaultdict(lambda: defaultdict(int))

        for _, row in self.df_filtered.iterrows():
            if pd.isna(row.get("openai_summary")):
                continue

            summary_text = str(row["openai_summary"]).lower()
            vehicle = row["vehicle_model"]

            for tone_category, keywords in tone_keywords.items():
                for keyword in keywords:
                    if keyword in summary_text:
                        tone_analysis[vehicle][tone_category] += 1
                        break

        return dict(tone_analysis)

    def get_detailed_vehicle_analysis(
        self, vehicle_model: str, market: str = None
    ) -> Dict:
        """Get detailed analysis for a specific vehicle model"""
        vehicle_data = self.df_filtered[
            self.df_filtered["vehicle_model"] == vehicle_model
        ]

        if market:
            if "country" in vehicle_data.columns:
                # Use country column directly
                vehicle_data = vehicle_data[vehicle_data["country"] == market]
            else:
                # Fallback to targeted_countries_list
                vehicle_data = vehicle_data[
                    vehicle_data["targeted_countries_list"].str.contains(
                        market, case=False, na=False
                    )
                ]

        if len(vehicle_data) == 0:
            return {}

        # Extract sample summaries - use openai_analysis if available
        summary_column = (
            "openai_analysis"
            if "openai_analysis" in vehicle_data.columns
            else "openai_summary"
        )
        sample_summaries = vehicle_data[summary_column].dropna().head(5).tolist()

        return {
            "total_ads": len(vehicle_data),
            "advertisers": vehicle_data["page_name"].unique().tolist(),
            "date_range": {
                "start": vehicle_data["start_date"].min(),
                "end": vehicle_data["start_date"].max(),
            },
            "sample_summaries": sample_summaries,
            "avg_spend": (
                vehicle_data["spend"].mean() if "spend" in vehicle_data.columns else 0
            ),
            "total_reach": (
                vehicle_data["reach_estimate"].sum()
                if "reach_estimate" in vehicle_data.columns
                else 0
            ),
        }
