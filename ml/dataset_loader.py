"""
RehabAI V1 - Dynamic Dataset Loader
"""
import os
import gzip
import re
import numpy as np
import pandas as pd
from ml.config import DATASET_ROOT, TARGET_MOVEMENTS

class UIPRMDLoader:
    def __init__(self, root_path=DATASET_ROOT):
        self.root_path = root_path
        # Defensive regex tracking both standard filenames and your folder's nested files
        self.file_pattern = re.compile(r'(m\d{2})_s(\d{2})_e(\d{2})_angles(?:_inc)?\.txt(?:\.gz)?')

    def scan_and_parse(self):
        """Recursively parses metadata and maps data streams directly."""
        records = []
        
        if not os.path.exists(self.root_path):
            raise FileNotFoundError(f"Dataset target layout absent at: {os.path.abspath(self.root_path)}")

        print(f"🔍 Beginning scanning loop inside: {self.root_path}")
        for root, _, files in os.walk(self.root_path):
            # Scan folders containing movement files
            if "Angles" in root:
                # Isolate target metrics based on sub-folder structure
                if "Incorrect Segmented Movements" in root or "Incorrect" in root:
                    quality_label = 0
                elif "Segmented Movements" in root or "Correct" in root or "data" in root:
                    # Default backup if explicitly nested under structural parent trees
                    quality_label = 0 if "inc" in root.lower() else 1
                else:
                    quality_label = 1

                for file in files:
                    match = self.file_pattern.match(file)
                    if match:
                        movement_id, subject_id, rep_id = match.groups()
                        
                        # Fallback parsing fix if the filename has an explicit indicator suffix
                        if "inc" in file.lower():
                            quality_label = 0
                        
                        if movement_id in TARGET_MOVEMENTS:
                            records.append({
                                "exercise_id": movement_id,
                                "exercise_name": TARGET_MOVEMENTS[movement_id],
                                "subject_id": int(subject_id),
                                "repetition_id": int(rep_id),
                                "label": quality_label,
                                "file_path": os.path.join(root, file)
                            })
                            
        return pd.DataFrame(records)

    def load_matrix(self, file_path):
        """Decompresses and extracts angular columns safely."""
        if file_path.endswith('.gz'):
            with gzip.open(file_path, 'rt') as f:
                matrix = np.loadtxt(f, delimiter=',')
        else:
            matrix = np.loadtxt(file_path, delimiter=',')
            
        if matrix.ndim == 1:
            matrix = matrix.reshape(-1, matrix.shape[0])
        return matrix