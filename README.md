#  SpeciesWatch: Monitoring Biodiversity with Data & Visualization


## Overview
SpeciesWatch is a data-driven project designed to monitor biodiversity trends using interactive visualizations and analytical tools. Built as part of the DATA 608 course, this project leverages public datasets to explore species distribution, conservation status, and ecological patterns.

## Repository Structure
- `api-job/`: Backend scripts and API integration for data retrieval.
- `eda-job/`: Exploratory data analysis and preprocessing.
- `specieswatch/`: Final data prep, frontend components and visualization dashboards.

## Web App Demonstration
[![Web App Demo]](https://youtu.be/lOPJfy6CYXo) 


## 1. Introduction

### 1.1 Problem Statement

Information about the global distribution of endangered mammals—whether freshwater, marine, terrestrial, or mixed—is scattered, often locked in static formats, and spread across multiple sources. This makes it hard for researchers, educators, policymakers, and the public to access, explore, and act on the data.

Mammals face increasing threats worldwide. Over **1,100 species** are currently listed as threatened or endangered on the IUCN Red List (nearly 20% of all mammals), due to habitat loss, climate change, poaching, and pollution. They’re ecologically critical, culturally significant, and often serve as “flagship species” for broader conservation efforts.

This project provides a unified, interactive web application for visualizing global endangered mammal data—combining geospatial mapping, conservation status, and representative images.

### 1.2 Key Features

- **Interactive, Filterable World Map**  
  Filter by habitat type (freshwater, marine, terrestrial, or combinations) and see species distributions.
  
- **Species Info Panels**  
  Includes scientific name, conservation status, and representative images.

- **Dynamic Visualizations**  
  - Threatened species by taxonomic order  
  - Distribution by habitat type  
  - Pie charts of conservation status proportions

- **Single, Unified Platform**  
  Consolidates fragmented biodiversity data for public awareness, research, and education.

---

## 2. Data Engineering Lifecycle

### 2.0 Pipeline Overview

**Stages:**
1. **Data Acquisition & Staging**  
   - IUCN shapefiles staged in S3  
   - iNaturalist API for species images

2. **Processing & Storage**  
   - EC2 (Ubuntu 24.04, r5.large) for data cleaning & transformation  
   - Output as GeoJSON (map rendering) and Parquet (analysis)  
   - Stored in PostgreSQL + PostGIS

3. **Consumption & Deployment**  
   - Streamlit app (Dockerized) fetching from PostgreSQL/PostGIS  
   - Interactive maps + analysis dashboards

![Pipeline Diagram](![final (2)](https://github.com/user-attachments/assets/70b6d48c-584b-4a8a-b669-3c2f47696479)
) 
---

### 2.1 Data Sources

1. **IUCN Red List**  
   - ~3.45 GB shapefile dataset of 5,928 mammal species  
   - Attributes: taxonomy, conservation status, habitat presence, geometry  
   - Downloaded: July 17, 2025  

2. **iNaturalist API**  
   - For representative species images  
   - Filtered by taxonomic name, mammals only, photo-supported observations  
   - License: Creative Commons (non-commercial use)

---

### 2.2 Ingestion

- Species list cleaned and deduplicated before API calls
- Batched requests (1,000 species/batch) to respect rate limits
- Logged missing or image-less species
- Final outputs:  
  - `species_not_found.csv`  
  - `species_no_photo.csv`  
  - `species_with_photo.csv`

---

### 2.3 Storage

- **Raw Data**: S3 bucket (`species-conservation-data`, private access)  
- **Processing**: EBS volumes on EC2 (20 GiB OS, 100 GiB shapefiles & outputs)  
- **Processed Data**:  
  - GeoJSON (map rendering)  
  - Parquet (analysis)  
  - PostgreSQL + PostGIS (final serving)

---

### 2.4 Transformation

- Geometry validation, CRS alignment, and duplication removal
- Filtering to threatened species
- Simplification via Douglas–Peucker (1 km tolerance, `preserve_topology=True`)
- Added `habitat` column (combined marine/terrestrial/freshwater flags)
- Joined image URLs from API output
- Standardized taxonomy labels and conservation codes

---

### 2.5 Serving

- **Streamlit Dashboard**  
  - Habitat & species filters  
  - Folium maps with color-coded polygons  
  - Plotly donut charts for conservation status & habitat breakdown
- **Analysis Tools**  
  - Threat ratios per taxonomic order  
  - Distribution by habitat systems  
  - Styled summary tables
- **Dockerized Deployment**  
  - Reproducible local & cloud setup via Docker & Docker Compose

---

## 3. Evaluation

- **Functionality**: All planned features operate without error
- **Performance**: Fast response due to caching and simplified geometries
- **Usability**: Clear UI for both technical and non-technical audiences
- **Data Accuracy**: Cross-verified with IUCN authoritative data
- **Scalability**: Containerized, modular pipeline

---

## 4. Limitations & Next Steps

- Some species lack high-quality images  
- Limited to mammals—future work could expand taxa coverage  
- Potential performance improvements by processing directly from S3 (via Boto3) without EBS transfers

---

## 5. Conclusion

SpeciesWatch integrates global biodiversity data into a single interactive tool, bridging the gap between complex datasets and accessible insights. It demonstrates the potential of combining **data engineering**, **geospatial analysis**, and **ecological expertise** to inform and inspire conservation efforts.

---

## 6. Deployment & Reproducibility

**Requirements**:
- Docker
- Docker Compose

  ## Citation

- IUCN. 2025. *The IUCN Red List of Threatened Species*. Version 3.1. Available at: [https://www.iucnredlist.org](https://www.iucnredlist.org) (accessed July 17, 2025).
- iNaturalist. *iNaturalist API*. Available at: [https://api.inaturalist.org](https://api.inaturalist.org)


