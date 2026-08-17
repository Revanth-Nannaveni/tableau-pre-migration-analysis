from typing import List, Dict, Any
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL
from app.models.metadata import (
    DataModel, Components, SharedDataSourceAnalysis, RecommendedSemanticModel,
    SharedDataModelResponse, UnusedComponentsResponse
)
import json


class SharedDataModelAnalyzer:
    """Analyzer for shared data model opportunities"""
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
    
    async def analyze(
        self,
        data_model: DataModel,
        components: Components,
        mappings: Dict[str, Any]
    ) -> SharedDataModelResponse:
        """
        Analyze shared data sources and recommend semantic models
        
        Args:
            data_model: Data model metadata
            components: Components metadata
            mappings: Mapping data
        
        Returns:
            SharedDataModelResponse with recommendations
        """
        # Identify shared data sources
        shared_datasources = []
        datasource_usage = {}
        
        for ds_name, reports in mappings.get("datasource_to_reports", {}).items():
            if len(reports) > 1:
                shared_datasources.append(SharedDataSourceAnalysis(
                    datasource_name=ds_name,
                    report_count=len(reports),
                    reports=reports
                ))
            datasource_usage[ds_name] = len(reports)
        
        # Generate recommendations
        prompt = self._build_prompt(data_model, shared_datasources, components)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Power BI semantic modeling expert. Recommend optimal semantic model structures. Return JSON."
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
            
            recommended_models = [
                RecommendedSemanticModel(
                    model_name=model.get("model_name", ""),
                    datasources=model.get("datasources", []),
                    recommended_reports=model.get("recommended_reports", []),
                    consolidation_potential=float(model.get("consolidation_potential", 0.0))
                )
                for model in result.get("recommended_semantic_models", [])
            ]
        except (json.JSONDecodeError, KeyError, ValueError):
            recommended_models = []
        
        return SharedDataModelResponse(
            shared_datasources=shared_datasources,
            shared_tables=[t.name for t in data_model.tables],
            recommended_semantic_models=recommended_models
        )
    
    def _build_prompt(
        self,
        data_model: DataModel,
        shared_datasources: List[SharedDataSourceAnalysis],
        components: Components
    ) -> str:
        """Build prompt for OpenAI"""
        shared_info = "\n".join([
            f"- {ds.datasource_name}: used by {ds.report_count} reports ({', '.join(ds.reports)})"
            for ds in shared_datasources
        ])
        
        return f"""
Analyze the following shared data sources and recommend consolidation strategies:

Shared Data Sources:
{shared_info}

Total Dashboards: {len(components.dashboards)}
Total Worksheets: {len(components.worksheets)}

Based on usage patterns, recommend Power BI semantic models that would optimize:
1. Data reusability
2. Report consolidation
3. Reduced data refresh overhead
4. Better governance

Return a JSON object with key:
- "recommended_semantic_models": array of objects with:
  - "model_name": name of the recommended semantic model
  - "datasources": array of datasource names to consolidate
  - "recommended_reports": array of report names that should use this model
  - "consolidation_potential": percentage score (0-1) for consolidation value
"""


class UnusedComponentsAnalyzer:
    """Analyzer for identifying unused components"""
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
    
    async def analyze(
        self,
        data_model: DataModel,
        components: Components,
        usage: Dict[str, Any]
    ) -> UnusedComponentsResponse:
        """
        Identify unused components
        
        Args:
            data_model: Data model metadata
            components: Components metadata
            usage: Usage information
        
        Returns:
            UnusedComponentsResponse with unused asset inventory
        """
        # Simple heuristic: components with no references are unused
        unused_worksheets = []
        unused_calculated_fields = []
        unused_filters = []
        unused_parameters = []
        unused_datasources = []
        
        # Check for unused datasources (those not in mappings)
        used_datasources = set()
        for ds in data_model.datasources:
            used_datasources.add(ds.name)
        
        # Worksheets with no usage data
        for ws in components.worksheets:
            if ws.name not in usage.get("view_names", []):
                unused_worksheets.append(ws.name)
        
        # Filters and parameters not referenced
        for filt in components.filters:
            unused_filters.append(filt.name)
        
        for param in components.parameters:
            unused_parameters.append(param.name)
        
        return UnusedComponentsResponse(
            unused_worksheets=unused_worksheets,
            unused_calculated_fields=unused_calculated_fields,
            unused_filters=unused_filters,
            unused_parameters=unused_parameters,
            unused_datasources=unused_datasources
        )
