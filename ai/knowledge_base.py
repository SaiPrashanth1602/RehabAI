"""
RehabAI Knowledge Base Mock Provider Component
Sprint 2 Component
"""
class ClinicalKnowledgeBase:
    @staticmethod
    def get_clinical_reference():
        return {
            "EX-001": {"target": "100 deg flexion", "doi": "10.1007/s00167-016-4283-3"},
            "EX-002": {"target": "0 deg ext lag", "doi": "10.1136/bjsports-2016-096031"},
            "EX-003": {"target": "0 deg full extension", "doi": "10.1007/s00167-016-4283-3"},
            "EX-004": {"target": "60 deg max depth", "doi": "10.2165/11597940-000000000-00000"},
            "EX-005": {"target": "Symmetric stand up", "doi": "N/A Guidelines"}
        }