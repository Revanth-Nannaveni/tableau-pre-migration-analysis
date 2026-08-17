from typing import List, Dict, Any
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL
from app.models.metadata import (
    Components, ComplexityScore, ComplexityAnalysisResponse,
    MigrationStrategy, MigrationStrategiesResponse
)
import json


class ComplexityAnalyzer:
    """Analyzer for workbook complexity assessment"""
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
    
    async def analyze(self, components: Components, data_model: Dict[str, Any]) -> ComplexityAnalysisResponse:
        """
        Analyze workbook complexity
        
        Args:
            components: Components metadata
            data_model: Data model metadata
        
        Returns:
            ComplexityAnalysisResponse with complexity scores
        """
        prompt = self._build_prompt(components, data_model)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Tableau complexity assessment expert. Analyze workbook complexity. Return JSON."
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
            
            complexity_scores = [
                ComplexityScore(
                    component=score.get("component", ""),
                    score=float(score.get("score", 0.5)),
                    reasoning=score.get("reasoning", "")
                )
                for score in result.get("complexity_scores", [])
            ]
            
            overall_score = float(result.get("overall_complexity_score", 0.5))
            
            return ComplexityAnalysisResponse(
                complexity_scores=complexity_scores,
                overall_complexity_score=overall_score,
                complexity_summary=result.get("summary", "")
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return ComplexityAnalysisResponse(
                complexity_scores=[],
                overall_complexity_score=0.5,
                complexity_summary="Analysis incomplete"
            )
    
    def _build_prompt(self, components: Components, data_model: Dict[str, Any]) -> str:
        """Build prompt for OpenAI"""
        return f"""
Analyze the complexity of a Tableau workbook with the following characteristics:

Dashboards: {len(components.dashboards)}
Worksheets: {len(components.worksheets)}
Filters: {len(components.filters)}
Parameters: {len(components.parameters)}
Actions: {len(components.actions)}
Datasources: {len(data_model.get('datasources', []))}
Relationships: {len(data_model.get('relationships', []))}

Provide:
1. Complexity scores for each major component (0-1 scale)
2. Overall complexity score (0-1 scale)
3. Summary explanation

Return a JSON object with keys:
- "complexity_scores": array of objects with "component", "score", "reasoning"
- "overall_complexity_score": number between 0 and 1
- "summary": brief explanation of complexity factors
"""


class MigrationStrategyAnalyzer:
    """Analyzer for recommending migration strategies"""
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
    
    async def analyze(
        self,
        workbook_name: str,
        complexity_score: float,
        components: Components,
        data_model: Dict[str, Any],
        kpi_analysis: Dict[str, Any]
    ) -> MigrationStrategiesResponse:
        """
        Recommend migration strategies
        
        Args:
            workbook_name: Name of workbook
            complexity_score: Complexity score (0-1)
            components: Components metadata
            data_model: Data model metadata
            kpi_analysis: KPI analysis results
        
        Returns:
            MigrationStrategiesResponse with recommended strategies
        """
        prompt = self._build_prompt(
            workbook_name,
            complexity_score,
            components,
            data_model,
            kpi_analysis
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Tableau to Power BI migration expert. Recommend optimal migration strategies. Return JSON."
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
            
            strategies = [
                MigrationStrategy(
                    strategy_name=strat.get("strategy_name", ""),
                    description=strat.get("description", ""),
                    effort_estimate=strat.get("effort_estimate", ""),
                    risk_level=strat.get("risk_level", ""),
                    key_steps=strat.get("key_steps", []),
                    estimated_timeline=strat.get("estimated_timeline", ""),
                    resource_requirements=strat.get("resource_requirements", [])
                )
                for strat in result.get("migration_strategies", [])
            ]
            
            return MigrationStrategiesResponse(
                strategies=strategies,
                recommended_strategy=result.get("recommended_strategy", ""),
                overall_assessment=result.get("overall_assessment", "")
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return MigrationStrategiesResponse(
                strategies=[],
                recommended_strategy="",
                overall_assessment="Analysis incomplete"
            )
    
    def _build_prompt(
        self,
        workbook_name: str,
        complexity_score: float,
        components: Components,
        data_model: Dict[str, Any],
        kpi_analysis: Dict[str, Any]
    ) -> str:
        """Build prompt for OpenAI"""
        complexity_level = "High" if complexity_score > 0.7 else "Medium" if complexity_score > 0.4 else "Low"
        
        return f"""
Recommend migration strategies for a Tableau to Power BI migration:

Workbook: {workbook_name}
Complexity Level: {complexity_level} (score: {complexity_score:.2f})
Dashboards: {len(components.dashboards)}
Worksheets: {len(components.worksheets)}
Filters: {len(components.filters)}
Parameters: {len(components.parameters)}
Datasources: {len(data_model.get('datasources', []))}
Duplicate KPIs: {len(kpi_analysis.get('duplicate_kpis', []))}
Similar KPIs: {len(kpi_analysis.get('similar_kpis', []))}

Based on these characteristics, recommend:
1. Multiple migration approaches (e.g., Big Bang, Phased, Hybrid)
2. For each approach: description, effort estimate, risk level, key steps, timeline, resources needed
3. Overall recommendation

Return a JSON object with keys:
- "migration_strategies": array of strategy objects
- "recommended_strategy": name of recommended approach
- "overall_assessment": brief assessment and rationale
"""


class ImpactAnalyzer:
    """Analyzer for migration impact assessment"""
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
    
    async def analyze(
        self,
        data_model: Dict[str, Any],
        components: Components,
        unused_components: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess migration impact
        
        Args:
            data_model: Data model metadata
            components: Components metadata
            unused_components: Unused components analysis
        
        Returns:
            Dict with impact assessment
        """
        prompt = self._build_prompt(data_model, components, unused_components)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Tableau to Power BI migration impact assessment expert. Provide detailed impact analysis. Return JSON."
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
            return result
        except (json.JSONDecodeError, ValueError):
            return {
                "impact_areas": [],
                "risk_assessment": {},
                "recommendations": []
            }
    
    def _build_prompt(
        self,
        data_model: Dict[str, Any],
        components: Components,
        unused_components: Dict[str, Any]
    ) -> str:
        """Build prompt for OpenAI"""
        return f"""
Assess the migration impact for a Tableau to Power BI migration:

Data Model:
- Datasources: {len(data_model.get('datasources', []))}
- Connections: {len(data_model.get('connections', []))}
- Relationships: {len(data_model.get('relationships', []))}

Components:
- Dashboards: {len(components.dashboards)}
- Worksheets: {len(components.worksheets)}
- Filters: {len(components.filters)}
- Parameters: {len(components.parameters)}

Unused Components (candidates for retirement):
- Unused Worksheets: {len(unused_components.get('unused_worksheets', []))}
- Unused Filters: {len(unused_components.get('unused_filters', []))}
- Unused Parameters: {len(unused_components.get('unused_parameters', []))}

Provide:
1. Key impact areas
2. Risk assessment with scores
3. Recommendations for minimizing impact

Return a JSON object with:
- "impact_areas": array of impact descriptions
- "risk_assessment": object with risk categories and scores
- "recommendations": array of mitigation recommendations
"""
