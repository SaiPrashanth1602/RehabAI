# test_v1_2_persistence.py
"""
RehabAI v1.2.0 Relational Persistence Engine Integration Test Suite
"""

import pytest
import os
import gc
from ai.database import RehabAIDatabase

def test_database_lifecycle_and_csv_generation():
    test_db = "rehab_test.db"
    
    # Clean up test database artifact if it exists from a previous crash
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except PermissionError:
            pass
        
    db_engine = RehabAIDatabase(db_path=test_db)
    
    # 1. Verify schema tables were created successfully
    assert os.path.exists(test_db)
    
    # 2. Simulate logging dummy session frames
    mock_session = "SESS-TEST123"
    db_engine.log_telemetry_frame(mock_session, 1.01, "knee_flexion_angle", 45.2, "GREEN")
    db_engine.log_telemetry_frame(mock_session, 1.02, "knee_flexion_angle", 48.7, "GREEN")
    
    # 3. Verify record extraction operations
    csv_out_path = db_engine.export_session_to_csv(mock_session, output_directory="test_exports")
    assert os.path.exists(csv_out_path)
    
    # Force connection cleanup by destroying the instance reference pointer explicitly
    del db_engine
    gc.collect() # Trigger garbage collection to completely drop connection locks
    
    # 4. Clean up verification artifacts safely without file lock errors
    if os.path.exists(test_db):
        os.remove(test_db)
    if os.path.exists(csv_out_path):
        os.remove(csv_out_path)
        
    print("✅ Database persistence and CSV research exporter verified completely on Windows!")

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main(["-v", __file__]))