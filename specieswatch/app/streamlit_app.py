import pandas as pd
import streamlit as st
from folium.plugins import Fullscreen
from folium import Map, GeoJson, Popup
import folium
from sqlalchemy import create_engine
import geopandas as gpd
from streamlit_folium import st_folium
from PIL import Image
import requests
from io import BytesIO
import os
import plotly.express as px

# Database connection string
DB_URL = "postgresql://postgres:species123@specieswatch-db:5432/speciesdb"
engine = create_engine(DB_URL)

# Load species_data table
@st.cache_data
def load_species_data():
    query = "SELECT * FROM species_data"
    df = pd.read_sql(query, engine)
    return df

# Load species_geo table as GeoDataFrame
@st.cache_data
def load_species_geo():
    query = "SELECT * FROM species_geo"
    gdf = gpd.read_postgis(query, engine, geom_col="geometry")
    gdf = gdf.dropna(subset=["sci_name", "habitat", "category", "geometry"])
    gdf["sci_name"] = gdf["sci_name"].str.strip()
    gdf["habitat"] = gdf["habitat"].str.strip()
    return gdf

# Load data
df = load_species_data()
gdf = load_species_geo()


# Initialize session_state keys if missing
for key in ["filtered", "loaded_habitat", "loaded_species"]:
    if key not in st.session_state:
        st.session_state[key] = None
if st.session_state["filtered"] is None:
    st.session_state["filtered"] = gdf.iloc[0:0]  # empty

st.set_page_config(page_title="SpeciesWatch", layout="wide")

# Move title up by reducing top margin/padding
st.markdown(
    """
    <style>
    .css-1v3fvcr.e1fqkh3o3 {
        margin-top: 0rem;
        padding-top: 0rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("SpeciesWatch: Mammal Conservation and Habitat Explorer")
st.markdown('<p style="font-size:12px; color:gray;">Data source: IUCN, iNaturalist API</p>', unsafe_allow_html=True)


# --- Dropdowns with empty default selections ---
habitats = sorted(gdf["habitat"].unique())

dropdown_col1, dropdown_col2,col3  = st.columns([2,2,1])
with dropdown_col1:
    selected_habitat = st.selectbox(
        "Select Habitat Type",
        options=[""] + habitats,  # Empty option first
        index=0
    )

with dropdown_col2:
    if selected_habitat:
        species_filtered = gdf[gdf["habitat"] == selected_habitat]
        species_names = sorted(species_filtered["sci_name"].unique())
    else:
        species_names = []

    selected_species = st.selectbox(
        "Select Species Name",
        options=[""] + species_names,
        index=0,
        disabled=(len(species_names) == 0)
    )
with col3:
    st.markdown("<br>", unsafe_allow_html=True) 
    load_clicked = st.button("Load")
# --- Filtering logic ---
if load_clicked:
    if selected_habitat and selected_species:
        if (selected_habitat != st.session_state.get("loaded_habitat") or
            selected_species != st.session_state.get("loaded_species")):
            filtered = gdf[
                (gdf["habitat"] == selected_habitat) &
                (gdf["sci_name"] == selected_species)
            ]

            st.session_state.filtered = filtered
            st.session_state.loaded_habitat = selected_habitat
            st.session_state.loaded_species = selected_species
        else:
            filtered = st.session_state.filtered
        if filtered.empty:
            st.warning("No species found for the selected habitat and name.")
    else:
        st.error("Please select both habitat and species before loading.")
        st.session_state.filtered = gdf.iloc[0:0]


# --- Feedback messages ---
if not selected_habitat:
    st.info("Please select a habitat to begin.")
elif not selected_species:
    st.info("Please select a species.")

filtered = st.session_state.get("filtered", gdf.iloc[0:0])
loaded_habitat = st.session_state.get("loaded_habitat", None)
loaded_species = st.session_state.get("loaded_species", "Unknown Species")

# Render map & info side-by-side with columns
col_map, col_info = st.columns([4,2], gap="small")

with col_map:
    if not filtered.empty:
        bounds = filtered.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=4,
            tiles=None,
            min_zoom=4,
            max_zoom=18,
            max_bounds=True
        )
        folium.TileLayer('CartoDB positron', no_wrap=True).add_to(m)

        # Define category-to-color mapping
        category_colors = {
            'Least Concern': 'green',
            'Near Threatened': '#FFFF00',
            'Vulnerable': '#FFA500',
            'Endangered': "#FF0000D8",
            'Critically Endangered': '#FF0000',  # Bright red
            'Data Deficient': 'gray',
            'Extinct': 'black'
        }

        def style_function(feature):
            category = feature['properties'].get('category', 'Data Deficient')
            color = category_colors.get(category, 'gray')
            return {
                "fillColor": color,
                "color": color,
                "weight": 2,
                "fillOpacity": 0.5
            }

        geojson = GeoJson(data=filtered.__geo_interface__, style_function=style_function)
        popup = Popup(f"{loaded_species}", parse_html=True)
        geojson.add_child(popup)
        geojson.add_to(m)

        m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
        m.options['maxBounds'] = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
        m.options['maxBoundsViscosity'] = 1.0
    else:
        m = folium.Map(
            location=[45.0, -75.0],
            zoom_start=4,
            tiles=None,
            min_zoom=4,
            max_zoom=18,
            max_bounds=True
        )
        folium.TileLayer('CartoDB positron', no_wrap=True).add_to(m)
        folium.Marker(
            location=[45.0, -75.0],
            popup="No data for selected filters",
            icon=folium.Icon(color="gray"),
        ).add_to(m)

    st_folium(m, width=800, height=500)


with col_info:
    if filtered.empty:
        st.warning("Please select both habitat and species before loading.")
    else:
        row = filtered.iloc[0]
        photo_url = row.get('photo_url', None)
        if isinstance(photo_url, str) and photo_url.startswith("http"):
            try:
                response = requests.get(photo_url)
                img = Image.open(BytesIO(response.content))
            except Exception:
                img = None
        elif photo_url and os.path.exists(photo_url):
            img = Image.open(photo_url)
        else:
            img = None  # or skip showing image

        if img:
            st.image(img, caption=f"{row['sci_name']}")
        else:
            st.info("Image not available.")

        st.markdown(f"**Scientific Name:** {row['sci_name']}")
        st.markdown(f"**Conservation Status:** {row['category']}")
        st.markdown("<div style='height:100px'></div>", unsafe_allow_html=True)

# --- Analysis Section ---
st.markdown("---")
st.header("Comprehensive Conservation Analysis")


# --- Analysis Filters (sidebar, separate) ---

category_labels = {
    "CR": "Critically Endangered",
    "EN": "Endangered",
    "EX": "Extinct",
    "LC": "Least Concern",
    "VU": "Vulnerable",
    "NT": "Near Threatened",
    "DD": "Data Deficient",
    "EW": "Extinct in the Wild"
}

# Categories for conservation status filter
categories = sorted(df['category'].dropna().unique())
with st.sidebar:
    st.header("Conservation Filters")

    with st.expander("Filter by Category", expanded=True):
        selected_categories = st.multiselect(
            "Select Conservation Category",
            sorted(df['category'].dropna().unique()),
            default=[]
        )

    with st.expander("Category Legend"):
        for abbr, full in category_labels.items():
            st.markdown(f"- `{abbr}`: {full}")
    st.markdown("---")

filtered_analysis = df[(df['category'].isin(selected_categories))]


if filtered_analysis.empty:
    st.info("Select filters from the sidebar to view detailed analysis.")
else:
    # Clean order_ column and prepare mapping dict
    filtered_analysis['order_'] = filtered_analysis['order_'].str.strip().str.title()
    order_name_map = (
        filtered_analysis[['order_', 'order_name_mapped']]
        .drop_duplicates()
        .set_index('order_')['order_name_mapped']
        .to_dict()
    )

    # Group counts
    species_count = filtered_analysis.groupby('order_')['id_no'].nunique()

    def threatened_species_count(group):
        return group[group['category'].isin(['CR', 'EN', 'VU'])]['id_no'].nunique()

    threatened_count = filtered_analysis.groupby('order_', group_keys=False).apply(threatened_species_count)

    # Create summary table
    taxa_summary = pd.DataFrame({
        'order_': species_count.index,
        'species_count': species_count.values,
        'threatened_count': threatened_count.values
    })

    taxa_summary['threat_ratio'] = taxa_summary['threatened_count'] / taxa_summary['species_count']

    # Map to common names
    taxa_summary['Order Common Name'] = taxa_summary['order_'].map(order_name_map)

    # Rename columns for clarity
    summary = taxa_summary.rename(columns={
        'order_': 'Taxonomic Order',
        'species_count': 'Number of Species',
        'threatened_count': 'Number of Threatened Species',
        'threat_ratio': 'Threat Ratio'
    })

    # Sort by Threat Ratio descending and reset index (drop=True to remove index)
    summary = summary.sort_values(by='Threat Ratio', ascending=False).reset_index(drop=True)

    # Format numeric columns for readability
    summary['Threat Ratio (%)'] = (summary['Threat Ratio'] * 100).round(2)
    summary['Number of Species'] = summary['Number of Species'].apply(lambda x: f"{x:,}")
    summary['Number of Threatened Species'] = summary['Number of Threatened Species'].apply(lambda x: f"{x:,}")

    # Select and reorder columns to show
    final_summary = summary[
        ['Taxonomic Order', 'Order Common Name', 'Number of Species', 'Number of Threatened Species', 'Threat Ratio (%)']
    ]

    # Apply styling to center-align numerical columns
    styled_df = (
        final_summary.style
        .set_properties(
            subset=['Number of Species', 'Number of Threatened Species', 'Threat Ratio (%)'],
            **{'text-align': 'center'}
        )
        .set_table_styles([
            {'selector': 'th.col_heading', 'props': [('text-align', 'center')]}
        ])
    )

    # Display styled DataFrame
    st.subheader("Species and Threatened Species by Taxonomic Order", divider="gray")
    st.dataframe(styled_df, use_container_width=True, hide_index=True)


    #Habitat distribution
    st.subheader("Habitat-Based Species Distribution Overview", divider="gray")
    for col in ['marine', 'terrestria', 'freshwater']:
        filtered_analysis[col] = filtered_analysis[col].astype(str).str.lower().map({'true': True, 'false': False})

    habitat_counts = filtered_analysis[filtered_analysis['presence'] == 1].groupby(['marine', 'terrestria', 'freshwater']).agg(
        species_count=('id_no', 'nunique')
    ).reset_index()

    def habitat_label(row):
        habitats = []
        if row['marine']:
            habitats.append('Marine')
        if row['terrestria']:
            habitats.append('Terrestrial')
        if row['freshwater']:
            habitats.append('Freshwater')
        return ' & '.join(habitats) if habitats else 'Unknown'

    habitat_counts['Habitat Type'] = habitat_counts.apply(habitat_label, axis=1)
    habitat_counts = habitat_counts[['Habitat Type', 'species_count']]
    # Rename and prepare habitat_counts
    habitat_counts = habitat_counts.rename(columns={'species_count': 'Number of Species'})

    # Apply styling to center-align numerical column
    styled_habitat_df = habitat_counts.style.set_properties(
        subset=['Number of Species'],
        **{'text-align': 'center'}
    ).set_table_styles([
        {'selector': 'th', 'props': [('text-align', 'center')]}
    ])
    st.subheader("Species Distribution by Habitat Type")
    st.dataframe(styled_habitat_df, use_container_width=True,hide_index=True)
    # Create two columns
    col1, col2 = st.columns(2)

    # First chart: Red List Categories
    with col1:
        pie_data = filtered_analysis[filtered_analysis['presence'] == 1].groupby('category_full').size().reset_index(name='counts')
        fig2 = px.pie(pie_data, values='counts', names='category_full',
                     hole=0.4)
        st.markdown("Mammals Red List Categories", unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True)

    # Second chart: Habitat Systems
    with col2:
        habitat_counts = habitat_counts[habitat_counts['Habitat Type'] != 'Unknown']
        # Sort for better visuals
        habitat_counts = habitat_counts.sort_values(by='Number of Species', ascending=False)
        # Plot
        fig_donut = px.pie(
            habitat_counts,
            names='Habitat Type',
            values='Number of Species',
            hole=0.4
        )
        fig_donut.update_traces(
            textinfo='label+percent',
            textposition='outside',
            insidetextorientation='radial',
            textfont=dict(size=10)
        )
        fig_donut.update_layout(
            legend_title_text='Habitat Type',
            uniformtext_minsize=10,
            uniformtext_mode='hide',
            margin=dict(t=50, b=50, l=100, r=100),
            height=600,
            width=800,
            showlegend=True
        )
        st.markdown("Habitat Systems", unsafe_allow_html=True)
        st.plotly_chart(fig_donut, use_container_width=True)
