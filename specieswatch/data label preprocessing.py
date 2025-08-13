import pandas as pd

df = pd.read_parquet('historical_species_data.parquet')  # or read_csv/raw data

# Map categories to full names
category_map = {
    'CR': 'Critically Endangered',
    'EX': 'Extinct',
    'EN': 'Endangered',
    'VU': 'Vulnerable',
    'EW': 'Extinct in the Wild',
    'NT': 'Near Threatened',
    'DD': 'Data Deficient',
    'LC': 'Least Concern'
}
df['category_full'] = df['category'].map(category_map)

# Detect category changes over time per species
def detect_change(series):
    prev = series.shift()
    return (series != prev) & prev.notna()

df = df.sort_values(['id_no', 'yrcompiled'])
df['category_change'] = df.groupby('id_no')['category_full'].transform(detect_change)

# Map taxonomic order codes to full names — store in a new column
order_name_map = {
    "SIRENIA": "Sea Cows and Manatees",
    "PROBOSCIDEA": "Elephants",
    "PHOLIDOTA": "Pangolins",
    "PERISSODACTYLA": "Odd-toed Ungulates (e.g., Horses)",
    "PRIMATES": "Primates (Monkeys and Apes)",
    "MONOTREMATA": "Egg-laying Mammals (Platypus, Echidna)",
    "PAUCITUBERCULATA": "Shrew Opossums",
    "PERAMELEMORPHIA": "Bandicoots",
    "ARTIODACTYLA": "Even-toed Ungulates (Deer, Cattle)",
    "DIPROTODONTIA": "Kangaroos and Possums",
    "AFROSORICIDA": "Tenrecs and Golden Moles",
    "CARNIVORA": "Carnivores (Cats, Dogs, Bears)",
    "LAGOMORPHA": "Rabbits and Hares",
    "PILOSA": "Sloths and Anteaters",
    "CHIROPTERA": "Bats",
    "EULIPOTYPHLA": "Shrews, Moles, Hedgehogs",
    "DASYUROMORPHIA": "Australian Carnivores (Tasmanian Devil)",
    "RODENTIA": "Rodents (Mice, Rats, Squirrels)",
    "MACROSCELIDEA": "Elephant Shrews",
    "CINGULATA": "Armadillos",
    "SCANDENTIA": "Tree Shrews",
    "DIDELPHIMORPHIA": "Opossums",
    "HYRACOIDEA": "Hyraxes",
    "DERMOPTERA": "Colugos",
    "NOTORYCTEMORPHIA": "Marsupial Moles",
    "MICROBIOTHERIA": "Monito del Monte",
    "TUBULIDENTATA": "Aardvarks"
}


df['order_name'] = df['order_'].map(order_name_map)

# Save cleaned and enriched data to a new parquet file
df.to_parquet('species_data_clean.parquet', index=False)
