from typing import List, Dict, Any
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL
from app.models.metadata import (
    Usage, PopularityAnalysis, LeastUsedReportsResponse,
    KPI, KPIs, DuplicateKPI, SimilarKPI, KPICluster, KPIIntelligenceResponse
)
import json


class LeastUsedReportsAnalyzer:
    """Analyzer for identifying least-used reports"""
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
    
    async def analyze(self, usage: Usage, reports_info: Dict[str, Any]) -> LeastUsedReportsResponse:
        """
        Analyze report usage and generate popularity scores
        
        Args:
            usage: Usage metadata
            reports_info: Information about reports
        
        Returns:
            LeastUsedReportsResponse with popularity analysis
        """
        analyses = []
        
        for view_stat in usage.view_counts:
            prompt = self._build_prompt(view_stat, reports_info)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Tableau analytics expert. Analyze report usage and provide a JSON response."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            try:
                result = json.loads(response.choices[0].message.content)
                
                analysis = PopularityAnalysis(
                    report_id=view_stat.view_id,
                    report_name=view_stat.view_name,
                    popularity_score=float(result.get("popularity_score", 0)),
                    usage_classification=result.get("usage_classification", "Low")
                )
                analyses.append(analysis)
            except (json.JSONDecodeError, KeyError, ValueError):
                analyses.append(PopularityAnalysis(
                    report_id=view_stat.view_id,
                    report_name=view_stat.view_name,
                    popularity_score=float(view_stat.view_count),
                    usage_classification="Low" if view_stat.view_count < 10 else "Medium" if view_stat.view_count < 50 else "High"
                ))
        
        return LeastUsedReportsResponse(analyses=analyses)
    
    def _build_prompt(self, view_stat, reports_info: Dict[str, Any]) -> str:
        """Build prompt for OpenAI"""
        return f"""
Analyze the following report usage data and classify it:

Report Name: {view_stat.view_name}
View Count: {view_stat.view_count}
Last Viewed: {view_stat.last_viewed}

Based on the view count and activity, provide:
1. A popularity score (0-100)
2. Usage classification (Low, Medium, or High)

Return a JSON object with keys:
- "popularity_score": number between 0 and 100
- "usage_classification": "Low", "Medium", or "High"

Guidelines:
- Low: < 50 views or not viewed in 6 months
- Medium: 50-500 views or regular but not frequent usage
- High: > 500 views or frequent regular usage
"""


class KPIIntelligenceAnalyzer:
    """Analyzer for KPI intelligence and duplicate detection"""
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
    
    async def analyze(self, kpis: KPIs) -> KPIIntelligenceResponse:
        """
        Analyze KPIs for duplicates, similarities, and clusters
        
        Args:
            kpis: KPIs metadata
        
        Returns:
            KPIIntelligenceResponse with intelligence analysis
        """
        if not kpis.kpis:
            return KPIIntelligenceResponse(
                duplicate_kpis=[],
                similar_kpis=[],
                kpi_clusters=[]
            )
        
        prompt = self._build_prompt(kpis)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Tableau KPI expert. Analyze KPIs and identify duplicates, similarities, and clusters. Return JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            
            duplicate_kpis = [
                DuplicateKPI(
                    kpi_ids=dup.get("kpi_ids", []),
                    kpi_names=dup.get("kpi_names", []),
                    similarity_score=float(dup.get("similarity_score", 0.9))
                )
                for dup in result.get("duplicate_kpis", [])
            ]
            
            similar_kpis = [
                SimilarKPI(
                    kpi_ids=sim.get("kpi_ids", []),
                    kpi_names=sim.get("kpi_names", []),
                    similarity_score=float(sim.get("similarity_score", 0.7))
                )
                for sim in result.get("similar_kpis", [])
            ]
            
            kpi_clusters = [
                KPICluster(
                    cluster_id=cluster.get("cluster_id", ""),
                    kpi_ids=cluster.get("kpi_ids", []),
                    cluster_name=cluster.get("cluster_name", ""),
                    common_theme=cluster.get("common_theme", "")
                )
                for cluster in result.get("kpi_clusters", [])
            ]
            
            return KPIIntelligenceResponse(
                duplicate_kpis=duplicate_kpis,
                similar_kpis=similar_kpis,
                kpi_clusters=kpi_clusters
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            return KPIIntelligenceResponse(
                duplicate_kpis=[],
                similar_kpis=[],
                kpi_clusters=[]
            )
    
    def _build_prompt(self, kpis: KPIs) -> str:
        """Build prompt for OpenAI"""
        kpi_list = "\n".join([
            f"- {kpi.name} (ID: {kpi.id}, Formula: {kpi.formula}, Aggregation: {kpi.aggregation})"
            for kpi in kpis.kpis
        ])
        
        return f"""
Analyze the following list of KPIs for duplicates, similarities, and natural groupings:

{kpi_list}

Identify:
1. Exact duplicates (KPIs with the same formula/meaning)
2. Similar KPIs (KPIs that measure similar concepts)
3. KPI clusters (groups of related KPIs)

Return a JSON object with keys:
- "duplicate_kpis": array of objects with "kpi_ids", "kpi_names", "similarity_score"
- "similar_kpis": array of objects with "kpi_ids", "kpi_names", "similarity_score"
- "kpi_clusters": array of objects with "cluster_id", "kpi_ids", "cluster_name", "common_theme"

Only include items with high confidence (similarity_score > 0.7).
"""
