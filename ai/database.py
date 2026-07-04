"""
RehabAI Local Relational Persistence Engine
Sprint 8 - v1.2.0 Data Persistence Component

Manages SQLite tables for logging session metrics, raw time-series kinematics vectors,
and automated CSV extractions for clinical analytics reporting.
"""

import sqlite3
import csv
import os
from datetime import datetime
from typing import Dict, Any, List, Tuple

class RehabAIDatabase:
    def __init__(self, db_path: str = "rehab_ai.db"):
        """Initializes the database connection and runs structural schema setups."""
        self.db_path = db_path
        self._initialize_tables()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize_tables(self):
        """Creates normalized relational database tables if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Patients/Profiles Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id TEXT PRIMARY KEY,
                    full_name TEXT NOT NULL,
                    assigned_phase INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL
                )
            """)
            
            # 2. Session Summary Metrics Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    patient_id TEXT,
                    exercise_id TEXT NOT NULL,
                    rehabilitation_phase INTEGER NOT NULL,
                    total_repetitions INTEGER DEFAULT 0,
                    peak_metric_value REAL DEFAULT 0.0,
                    compliance_score REAL DEFAULT 100.0,
                    violation_count INTEGER DEFAULT 0,
                    session_timestamp TEXT NOT NULL,
                    FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
                )
            """)
            
            # 3. High-Frequency Time-Series Telemetry Table (For ML Training & Research)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS telemetry_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    safety_status TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
            """)
            conn.commit()

    def create_patient_profile(self, patient_id: str, name: str, current_phase: int = 1):
        """Inserts or updates a permanent system user profile record."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO patients (patient_id, full_name, assigned_phase, created_at)
                VALUES (?, ?, ?, ?)
            """, (patient_id, name, current_phase, datetime.now().isoformat()))
            conn.commit()

    def log_session_summary(self, session_id: str, patient_id: str, exercise_id: str, 
                            phase: int, reps: int, peak: float, compliance: float, violations: int):
        """Commits aggregate performance metrics to permanent relational history logs."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO sessions (
                    session_id, patient_id, exercise_id, rehabilitation_phase, 
                    total_repetitions, peak_metric_value, compliance_score, violation_count, session_timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (session_id, patient_id, exercise_id, phase, reps, peak, compliance, violations, datetime.now().isoformat()))
            conn.commit()

    def log_telemetry_frame(self, session_id: str, timestamp: float, metric_name: str, metric_value: float, status: str):
        """Logs high-frequency, frame-by-frame tracking variables for deep research evaluations."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO telemetry_logs (session_id, timestamp, metric_name, metric_value, safety_status)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, timestamp, metric_name, metric_value, status))
            conn.commit()

    def export_session_to_csv(self, session_id: str, output_directory: str = "exports") -> str:
        """
        Extracts high-frequency frame telemetry out of the database into a cleanly formatted CSV.
        Ready for immediate statistical modeling inside tools like R, MATLAB, or SPSS.
        """
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            
        file_path = os.path.join(output_directory, f"telemetry_{session_id}.csv")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, metric_name, metric_value, safety_status 
                FROM telemetry_logs 
                WHERE session_id = ? ORDER BY timestamp ASC
            """, (session_id,))
            rows = cursor.fetchall()
            
        with open(file_path, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Timestamp_Offset", "Kinematic_Metric", "Calculated_Value", "Safety_Classification"])
            writer.writerows(rows)
            
        return file_path