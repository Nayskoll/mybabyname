# embedding_preparation.py
# This script enriches baby name data with meanings and generates embeddings using SentenceTransformer.

import pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import ast

# Load previously cleaned names dataset
df = pd.read_csv("prenoms-2023-dpt.csv", sep=";", encoding="utf-8")
df = df.rename(columns={"preusuel": "name", "annais" : "year", "sexe": "gender", "dpt" : "department", "nombre": "popularity"})
df['gender'] = df['gender'].replace({1: 'M', 2: 'F'})
df = df[df["year"]=='2023'].drop(columns="year")
df = df[df["name"]!='_PRENOMS_RARES']
df['total_popularity'] = df.groupby(['gender', 'name'])['popularity'].transform('sum')

# Load the dataset containing name meanings
meaning_df = pd.read_csv("name_with_meaning.csv", sep=",", encoding="utf-8")
meaning_df = meaning_df.drop_duplicates(subset="name", keep="first")

# Filter out low-popularity names and enrich with meanings
df_enriched = df[df.total_popularity > 10].merge(meaning_df, how="left", on="name")

# Select unique name-origin pairs for embedding
df_names_to_embed = df_enriched[["name", "origin"]].drop_duplicates()

# Load the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')
print('--- SentenceTransformer Loaded (1/3)---')

# Generate embeddings for names
df_names_to_embed["embedding"] = df_names_to_embed["name"].apply(lambda x: model.encode(x).tolist())
print('--- Names Embedded (2/3)---')

# Generate embeddings for origins (stored in a separate column)
df_names_to_embed["embedding_origin"] = df_names_to_embed["origin"].apply(lambda x: model.encode(str(x)).tolist())
print('--- Origins Embedded (3/3)---')

# Merge embeddings back to enriched dataframe
df_embedded = df_enriched.merge(df_names_to_embed.drop(columns="origin"), how="left", on="name")

# Ensure list-type columns are hashable for deduplication
df_copy = df_embedded.copy()
for col in df_copy.columns:
    if df_copy[col].apply(lambda x: isinstance(x, list)).any():
        df_copy[col] = df_copy[col].apply(lambda x: tuple(x) if isinstance(x, list) else x)

# Drop duplicates and unnecessary columns
df_deduped = df_copy.drop(columns=["department", "popularity"]).drop_duplicates()

# Save the final dataset with embeddings
df_deduped.to_csv("prenoms_embed_dedup.csv", index=False, encoding='utf-8')
print('--- Done ---')
