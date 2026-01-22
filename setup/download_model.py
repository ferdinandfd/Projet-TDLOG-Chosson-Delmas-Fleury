#!/usr/bin/env python3
"""
Script to download HuggingFace model for offline usage.
"""

from huggingface_hub import hf_hub_download
import os

def download_model_files():    
    model_name = "antoinechss/ingredient-reco"  # HF model
    cache_dir = "./app/hf_cache"  # Path fetched by the classifier
    
    # Ensure cache directory exists
    os.makedirs(cache_dir, exist_ok=True)
    
    files_to_download = [
        "config.json",
        "preprocessor_config.json", 
        "model.safetensors"
    ]
    
    print(f"Downloading to {cache_dir}")
    
    for filename in files_to_download:
        try:            
            file_path = hf_hub_download(
                repo_id=model_name,
                filename=filename,
                cache_dir=cache_dir,
                resume_download=True
            )
                        
        except Exception as e:
            return False
    
    print("Download Finished")
    return True

if __name__ == "__main__":
    download_model_files()
