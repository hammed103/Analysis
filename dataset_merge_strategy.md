# Dataset Merge Strategy Analysis

## Overview
You have two electric vehicle advertising datasets that can be successfully merged:

1. **Google Ads Dataset** (`combined_with_analysis_2025-07-04_09-44-49.csv`)
   - 127,905 rows × 59 columns (349.9 MB)
   - Google Ads Transparency data with OpenAI analysis

2. **Facebook Ads Dataset** (`facebook_ads_electric_vehicles_with_openai_summaries_cached_with_countries_cleaned.csv`)
   - 7,186 rows × 68 columns (18.7 MB)
   - Facebook Ad Library data with OpenAI summaries

## Key Findings

### Common Elements (Good for Merging)
- **Shared columns**: `advertiser_name`, `impressions_lower_bound`, `impressions_upper_bound`
- **Both have OpenAI analysis**: Rich text analysis of ad content
- **Similar data structure**: Ad content, advertiser info, geographic targeting, impressions
- **Complementary platforms**: Google vs Facebook advertising data

### Major Differences
- **Size disparity**: Google dataset is 18x larger than Facebook dataset
- **Column structure**: Only 3 truly identical columns, but many conceptually similar ones
- **Data granularity**: Google has more technical metadata, Facebook has more audience demographics

## Recommended Merge Strategy

### 1. UNION Approach (Recommended)
**Stack datasets vertically** while standardizing column names:

#### Core Standardized Columns:
```
- source_platform: 'google' | 'facebook'
- advertiser_name: Primary advertiser identifier
- ad_title: Standardized ad headline
- ad_description: Main ad text content
- start_date: Campaign start (firstShown → start_date)
- end_date: Campaign end (lastShown → end_date)
- impressions_lower: Lower bound of impressions
- impressions_upper: Upper bound of impressions
- region_info: Geographic targeting (region_name | targeted_countries)
- openai_analysis: AI-generated content analysis
- image_url: Primary ad image
```

#### Column Mapping:
| Concept | Google Dataset | Facebook Dataset |
|---------|----------------|------------------|
| Advertiser | `advertiserName` | `advertiser_name` |
| Ad Title | `shownAd/adTitle` | `ad_title` |
| Ad Text | `shownAd/adDescription` | `ad_text` |
| Start Date | `firstShown` | `start_date` |
| End Date | `lastShown` | `end_date` |
| Geography | `region_name` | `targeted_countries` |
| Analysis | `openai_analysis` | `openai_summary` |
| Image | `archiveImageUrl` | `first_image_url` |

### 2. Columns to Keep

#### Essential Columns:
- **Identity**: `source_platform`, `advertiser_name`, unique IDs
- **Content**: `ad_title`, `ad_description`, `image_url`
- **Timing**: `start_date`, `end_date`
- **Performance**: `impressions_lower`, `impressions_upper`
- **Geography**: `region_info`, `targeted_countries_list`
- **Analysis**: `openai_analysis`, `has_analysis`

#### Platform-Specific Valuable Columns:
**Google-specific:**
- `ocr_text`, `ocr_success` (text extraction from images)
- `advertiserDomain` (website information)
- `platform_code` (Google-specific platform info)

**Facebook-specific:**
- `page_like_count`, `reach_estimate` (social metrics)
- `age_audience_min/max`, `male/female_percentage` (demographics)
- `spend`, `cta_text`, `cta_type` (campaign details)

### 3. Columns to Drop/Minimize

#### Google Dataset - Consider Dropping:
- `variations/0/`, `variations/1/`, `variations/2/`, `variations/3/` columns (redundant)
- `shownAd/` prefix columns (keep content, drop metadata)
- `platform_impressions_*` (redundant with main impression fields)
- Empty analysis fields (`analysis_error`, `ocr_error` if mostly null)

#### Facebook Dataset - Consider Dropping:
- Technical metadata: `gated_type`, `entity_type`, `archive_types`
- Mostly empty fields: `political_countries`, `violation_types`
- Redundant image URLs if `first_image_url` is sufficient

## Implementation Steps

### Step 1: Data Cleaning
```python
# Clean Google dataset
google_clean = google_df[[
    'advertiserName', 'shownAd/adTitle', 'shownAd/adDescription',
    'firstShown', 'lastShown', 'impressions_lower_bound', 'impressions_upper_bound',
    'region_name', 'openai_analysis', 'archiveImageUrl', 'ocr_text', 'advertiserDomain'
]].copy()

# Clean Facebook dataset  
facebook_clean = facebook_df[[
    'advertiser_name', 'ad_title', 'ad_text', 'start_date', 'end_date',
    'impressions_lower_bound', 'impressions_upper_bound', 'targeted_countries',
    'openai_summary', 'first_image_url', 'spend', 'reach_estimate', 'page_like_count'
]].copy()
```

### Step 2: Standardize Column Names
```python
# Rename Google columns
google_clean.columns = [
    'advertiser_name', 'ad_title', 'ad_description', 'start_date', 'end_date',
    'impressions_lower', 'impressions_upper', 'region_info', 'openai_analysis',
    'image_url', 'ocr_text', 'advertiser_domain'
]

# Rename Facebook columns
facebook_clean.columns = [
    'advertiser_name', 'ad_title', 'ad_description', 'start_date', 'end_date',
    'impressions_lower', 'impressions_upper', 'region_info', 'openai_analysis',
    'image_url', 'spend', 'reach_estimate', 'page_like_count'
]
```

### Step 3: Add Source Identifier
```python
google_clean['source_platform'] = 'google'
facebook_clean['source_platform'] = 'facebook'
```

### Step 4: Merge Datasets
```python
# Union the datasets
merged_dataset = pd.concat([google_clean, facebook_clean], ignore_index=True, sort=False)
```

## Expected Outcome

### Final Dataset Characteristics:
- **Size**: ~135,000 rows (127,905 + 7,186)
- **Columns**: ~15-20 core standardized columns + platform-specific columns
- **Coverage**: Both Google and Facebook electric vehicle advertising
- **Analysis**: Rich OpenAI analysis for content insights
- **Geographic**: Global coverage with platform-specific regional data

### Benefits of This Approach:
1. **Preserves all data** while making it analyzable
2. **Maintains platform distinctions** for comparative analysis
3. **Standardizes core fields** for unified analysis
4. **Keeps valuable platform-specific data** for specialized insights
5. **Enables cross-platform advertising analysis**

## Next Steps
1. Implement the cleaning and standardization script
2. Validate data quality after merge
3. Create data dictionary for the merged dataset
4. Consider additional analysis opportunities with the combined data
