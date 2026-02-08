"""
Data persistence utilities for recipe dataset management.

This module handles CSV file operations with error handling for
malformed data, including format fixing and type conversion for ingredient lists.
"""

import pandas as pd
import os
import csv
import json
import ast


def fix_csv_format(filename):
    """
    Fix malformed CSV file format.
    
    Args:
        filename (str): Path to CSV file that needs fixing
    """
    with open(filename, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['recipe_title'])
        for line in lines:
            line = line.strip()
            if line and not line.startswith("recipe_title"):
                writer.writerow([line.split(",")[0].strip('"')])


def load_dataset(path):
    """
    Load recipe dataset with error handling and column validation.
    
    Args:
        path (str): Path to CSV file
        
    Returns:
        pd.DataFrame: Recipe dataset with standardized format
    """
    # Create new dataset if file doesn't exist
    if not os.path.exists(path):
        return pd.DataFrame(columns=["recipe_title", "ingredients"])

    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
    except:
        # Fix corrupted CSV format and retry
        fix_csv_format(path)
        df = pd.read_csv(path, encoding="utf-8-sig")

    # Ensure ingredients column exists
    if "ingredients" not in df.columns:
        df["ingredients"] = None

    # Convert ingredients column to proper list format
    df["ingredients"] = df["ingredients"].apply(safe_list)
    return df


def safe_list(x):
    """
    Safely convert various input types to list format.
    
    Args:
        x: Input value to convert
        
    Returns:
        list: Converted value as list
    """
    if isinstance(x, list):
        return x
    if pd.isna(x) or x in ["", "None", "[]"]:
        return []
    try:
        return ast.literal_eval(x)
    except:
        return []


def save_dataset(df, path):
    """
    Save dataset to CSV with JSON serialization for lists.
    
    Args:
        df (pd.DataFrame): Dataset to save
        path (str): Output file path
    """
    df_copy = df.copy()
    # Serialize ingredient lists as JSON strings for CSV storage
    df_copy["ingredients"] = df_copy["ingredients"].apply(
        lambda x: json.dumps(x, ensure_ascii=False)
    )
    df_copy.to_csv(path, index=False, encoding="utf-8-sig")
