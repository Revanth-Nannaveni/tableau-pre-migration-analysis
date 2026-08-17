from typing import Dict, List, Any, Optional
from datetime import datetime
from app.models.metadata import (
    WorkbookAnalysis, WorkbookMetadata, Reports, ReportAsset,
    Usage, ViewStatistic, UserActivity, Subscription, Permission,
    DataModel, DataSource, Database, Schema, Table, Relationship, Join, Connection, CustomSQL,
    Fields, Dimension, Measure, CalculatedField, Formula,
    KPIs, KPI, Dependencies, Components, Dashboard, Worksheet, Filter, Parameter, Action,
    MappingData, MappingMetrics, Mapping
)
from app.services.tableau_api import TableauMetadataAPI, TableauRestAPI
from app.services.workbook_parser import TWBParser, TWBXParser


class DiscoveryService:
    """Service for discovering and extracting Tableau metadata"""
    
    def __init__(self, token: str, site_id: str):
        self.token = token
        self.site_id = site_id
        self.metadata_api = TableauMetadataAPI(token, site_id)
        self.rest_api = TableauRestAPI(token, site_id)
    
    async def discover_all_workbooks(self) -> List[WorkbookAnalysis]:
        """Discover all workbooks and their metadata"""
        try:
            workbooks = await self.metadata_api.get_workbooks()
            analyses = []
            
            for wb_data in workbooks:
                if "node" in wb_data:
                    workbook_node = wb_data["node"]
                    workbook_id = workbook_node.get("id")
                    
                    analysis = await self._analyze_workbook(workbook_node)
                    analyses.append(analysis)
            
            return analyses
        except Exception as e:
            return []
    
    async def _analyze_workbook(self, workbook_node: Dict[str, Any]) -> WorkbookAnalysis:
        """Analyze a single workbook"""
        workbook_id = workbook_node.get("id")
        
        # Extract workbook metadata
        workbook_metadata = WorkbookMetadata(
            id=workbook_id,
            name=workbook_node.get("name", ""),
            owner=workbook_node.get("owner", {}).get("username"),
            project=workbook_node.get("project", {}).get("name"),
            description=workbook_node.get("description"),
            created_at=workbook_node.get("createdAt"),
            updated_at=workbook_node.get("modifiedAt"),
            published_at=workbook_node.get("updatedAt"),
            revisions=[]
        )
        
        # Discover reports
        reports = await self._discover_reports(workbook_id)
        
        # Discover usage
        usage = await self._discover_usage(workbook_id)
        
        # Discover data model
        data_model = await self._discover_data_model(workbook_id)
        
        # Discover fields
        fields = await self._discover_fields(data_model)
        
        # Discover KPIs
        kpis = await self._discover_kpis(fields)
        
        # Discover dependencies
        dependencies = await self._discover_dependencies(workbook_id, data_model)
        
        # Discover components
        components = await self._discover_components(workbook_id)
        
        # Generate mappings
        mappings = await self._generate_mappings(data_model, components)
        
        return WorkbookAnalysis(
            workbook_metadata=workbook_metadata,
            reports=reports,
            usage=usage,
            data_model=data_model,
            fields=fields,
            kpis=kpis,
            dependencies=dependencies,
            components=components,
            mappings=mappings
        )
    
    async def _discover_reports(self, workbook_id: str) -> Reports:
        """Discover reports in a workbook"""
        try:
            dashboards_data = await self.metadata_api.get_dashboards()
            worksheets_data = await self.rest_api.get_views(workbook_id)
            
            dashboards = []
            for dash in dashboards_data:
                if "node" in dash:
                    dash_node = dash["node"]
                    dashboards.append(ReportAsset(
                        id=dash_node.get("id"),
                        name=dash_node.get("name", ""),
                        type="dashboard",
                        description=dash_node.get("description")
                    ))
            
            worksheets = []
            for ws in worksheets_data:
                worksheets.append(ReportAsset(
                    id=ws.get("id"),
                    name=ws.get("name", ""),
                    type="worksheet"
                ))
            
            return Reports(
                workbooks=[ReportAsset(id=workbook_id, name="", type="workbook")],
                dashboards=dashboards,
                worksheets=worksheets
            )
        except Exception:
            return Reports()
    
    async def _discover_usage(self, workbook_id: str) -> Usage:
        """Discover usage statistics"""
        try:
            views_data = await self.rest_api.get_views(workbook_id)
            
            view_counts = []
            for view in views_data:
                view_counts.append(ViewStatistic(
                    view_id=view.get("id"),
                    view_name=view.get("name", ""),
                    view_count=view.get("viewCount", 0),
                    last_viewed=view.get("updatedAt")
                ))
            
            return Usage(
                view_counts=view_counts,
                view_statistics=view_counts
            )
        except Exception:
            return Usage()
    
    async def _discover_data_model(self, workbook_id: str) -> DataModel:
        """Discover data model"""
        try:
            datasources_data = await self.metadata_api.get_datasources()
            
            datasources = []
            connections = []
            
            for ds in datasources_data:
                if "node" in ds:
                    ds_node = ds["node"]
                    datasources.append(DataSource(
                        id=ds_node.get("id"),
                        name=ds_node.get("name", ""),
                        type="published",
                        datasource_type=ds_node.get("database", {}).get("name")
                    ))
                    
                    # Add connection
                    connections.append(Connection(
                        id=ds_node.get("id"),
                        name=ds_node.get("name", ""),
                        server=ds_node.get("database", {}).get("server"),
                        connection_type="database"
                    ))
            
            return DataModel(
                datasources=datasources,
                connections=connections
            )
        except Exception:
            return DataModel()
    
    async def _discover_fields(self, data_model: DataModel) -> Fields:
        """Discover fields from data model"""
        try:
            dimensions = []
            measures = []
            
            for datasource in data_model.datasources:
                fields_data = await self.metadata_api.get_fields(datasource.id)
                
                if "fields" in fields_data:
                    for field in fields_data["fields"]:
                        if field.get("role") == "dimension":
                            dimensions.append(Dimension(
                                id=field.get("id"),
                                name=field.get("name", ""),
                                data_type=field.get("dataType", "string")
                            ))
                        elif field.get("role") == "measure":
                            measures.append(Measure(
                                id=field.get("id"),
                                name=field.get("name", ""),
                                data_type=field.get("dataType", "number")
                            ))
            
            return Fields(
                dimensions=dimensions,
                measures=measures
            )
        except Exception:
            return Fields()
    
    async def _discover_kpis(self, fields: Fields) -> KPIs:
        """Discover KPIs from measures"""
        kpis_list = []
        
        for measure in fields.measures:
            kpis_list.append(KPI(
                id=measure.id,
                name=measure.name,
                formula="",
                aggregation="sum",
                data_type=measure.data_type
            ))
        
        return KPIs(kpis=kpis_list)
    
    async def _discover_dependencies(
        self,
        workbook_id: str,
        data_model: DataModel
    ) -> Dependencies:
        """Discover dependencies"""
        try:
            upstream = []
            downstream = []
            
            for datasource in data_model.datasources:
                lineage = await self.metadata_api.get_lineage(datasource.id)
                
                upstream.extend([
                    ds.get("name", "")
                    for ds in lineage.get("upstreamDatasources", [])
                ])
                
                downstream.extend([
                    ds.get("name", "")
                    for ds in lineage.get("downstreamDatasources", [])
                ])
            
            return Dependencies(
                upstream=upstream,
                downstream=downstream,
                shared_datasources=[ds.name for ds in data_model.datasources]
            )
        except Exception:
            return Dependencies()
    
    async def _discover_components(self, workbook_id: str) -> Components:
        """Discover dashboards, worksheets, filters, and parameters"""
        try:
            views_data = await self.rest_api.get_views(workbook_id)
            
            dashboards = []
            worksheets = []
            
            for view in views_data:
                ws = Worksheet(
                    id=view.get("id"),
                    name=view.get("name", "")
                )
                worksheets.append(ws)
            
            return Components(
                dashboards=dashboards,
                worksheets=worksheets
            )
        except Exception:
            return Components()
    
    async def _generate_mappings(
        self,
        data_model: DataModel,
        components: Components
    ) -> MappingData:
        """Generate data source to report mappings"""
        datasource_to_reports = {}
        dashboard_to_datasources = {}
        
        for ds in data_model.datasources:
            datasource_to_reports[ds.name] = []
        
        for dashboard in components.dashboards:
            dashboard_to_datasources[dashboard.name] = [
                ds.name for ds in data_model.datasources
            ]
        
        # Calculate metrics
        total_reports = len(components.dashboards) + len(components.worksheets)
        total_datasources = len(data_model.datasources)
        
        metrics = MappingMetrics(
            reports_per_datasource=total_reports / total_datasources if total_datasources > 0 else 0,
            datasources_per_dashboard=total_datasources / len(components.dashboards) if len(components.dashboards) > 0 else 0,
            shared_datasources=len(data_model.datasources),
            shared_tables=len(data_model.tables)
        )
        
        return MappingData(
            datasource_to_reports=datasource_to_reports,
            dashboard_to_datasources=dashboard_to_datasources,
            metrics=metrics
        )
    
    async def parse_workbook_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Parse a workbook file (.twb or .twbx)"""
        if filename.endswith('.twbx'):
            return TWBXParser.parse(file_content)
        elif filename.endswith('.twb'):
            return TWBParser.parse(file_content)
        else:
            return {"error": "Unsupported file format"}
