class DeviationAnalysisEngine:
    def analyze_trajectory(self, today_ris, yesterday_ris, expected_ris):
        dev = round(today_ris - expected_ris, 1)
        delta = round(today_ris - yesterday_ris, 1)
        trend = "IMPROVING" if delta > 1.5 else ("REGRESSING" if delta < -1.5 else "PLATEAUED")
        
        if dev <= -7.0:
            rec = "Significant deviation below expected recovery path."
            status = "CRITICAL_LAG"
        elif -7.0 < dev < -2.0:
            rec = "Minor recovery lag identified."
            status = "MODERATE_LAG"
        else:
            rec = "Progress is on track."
            status = "ON_TRACK"
            
        return {"deviation": dev, "trend": trend, "clinical_indicator": status, "recommendation": rec}