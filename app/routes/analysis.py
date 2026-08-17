from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import Optional
from app.services.discovery import DiscoveryService
from app.services.ai_analysis import LeastUsedReportsAnalyzer, KPIIntelligenceAnalyzer
from app.services.advanced_analysis import ComplexityAnalyzer, MigrationStrategyAnalyzer, ImpactAnalyzer
from app.models.metadata import AnalysisResponse
from app.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])


@router.post("/discover-workbooks")
async def discover_workbooks(
    token: str,
    site_id: str,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Discover all workbooks and extract metadata
    
    Args:
        token: Tableau authentication token
        site_id: Tableau site ID
        current_user: Authenticated user
    
    Returns:
        Dictionary with discovery results
    """
    try:
        discovery_service = DiscoveryService(token, site_id)
        workbook_analyses = await discovery_service.discover_all_workbooks()
        
        return {
            "status": "success",
            "count": len(workbook_analyses),
            "workbooks": [wb.dict() for wb in workbook_analyses]
        }
    except Exception as e:
        logger.error(f"Discovery error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-workbook")
async def analyze_workbook(
    token: str,
    site_id: str,
    workbook_id: str,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Complete analysis of a single workbook
    
    Args:
        token: Tableau authentication token
        site_id: Tableau site ID
        workbook_id: ID of workbook to analyze
        current_user: Authenticated user
    
    Returns:
        Analysis response with complete analysis
    """
    try:
        discovery_service = DiscoveryService(token, site_id)
        
        # Discover workbook metadata
        workbooks = await discovery_service.discover_all_workbooks()
        workbook = next((wb for wb in workbooks if wb.workbook_metadata.id == workbook_id), None)
        
        if not workbook:
            raise HTTPException(status_code=404, detail="Workbook not found")
        
        # Analyze usage patterns
        usage_analyzer = LeastUsedReportsAnalyzer()
        usage_analysis = await usage_analyzer.analyze(
            workbook.usage,
            {"reports_info": {}}
        )
        
        # Analyze KPIs
        kpi_analyzer = KPIIntelligenceAnalyzer()
        kpi_analysis = await kpi_analyzer.analyze(workbook.fields)
        
        # Analyze complexity
        complexity_analyzer = ComplexityAnalyzer()
        complexity_analysis = await complexity_analyzer.analyze(
            workbook.components,
            workbook.data_model.dict()
        )
        
        # Generate migration strategy
        strategy_analyzer = MigrationStrategyAnalyzer()
        migration_strategies = await strategy_analyzer.analyze(
            workbook.workbook_metadata.name,
            complexity_analysis.overall_complexity_score,
            workbook.components,
            workbook.data_model.dict(),
            kpi_analysis.dict()
        )
        
        # Assess impact
        impact_analyzer = ImpactAnalyzer()
        impact_assessment = await impact_analyzer.analyze(
            workbook.data_model.dict(),
            workbook.components,
            {}
        )
        
        return {
            "status": "success",
            "workbook_metadata": workbook.workbook_metadata.dict(),
            "reports": workbook.reports.dict(),
            "usage_analysis": usage_analysis.dict(),
            "kpi_intelligence": kpi_analysis.dict(),
            "complexity_analysis": complexity_analysis.dict(),
            "migration_strategies": migration_strategies.dict(),
            "impact_assessment": impact_assessment
        }
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-workbook")
async def upload_workbook(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Upload and analyze a .twb or .twbx file
    
    Args:
        file: Workbook file upload
        current_user: Authenticated user
    
    Returns:
        Dictionary with parsed metadata
    """
    try:
        if not file.filename.endswith(('.twb', '.twbx')):
            raise HTTPException(
                status_code=400,
                detail="Only .twb and .twbx files are supported"
            )
        
        content = await file.read()
        discovery_service = DiscoveryService("", "")
        
        parsed_data = discovery_service.parse_workbook_file(content, file.filename)
        
        return {
            "status": "success",
            "filename": file.filename,
            "parsed_metadata": parsed_data
        }
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/unused-components")
async def get_unused_components(
    token: str,
    site_id: str,
    workbook_id: str,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get unused components in a workbook
    
    Args:
        token: Tableau authentication token
        site_id: Tableau site ID
        workbook_id: ID of workbook
        current_user: Authenticated user
    
    Returns:
        Dictionary with unused components analysis
    """
    try:
        discovery_service = DiscoveryService(token, site_id)
        
        # Get workbook data
        workbooks = await discovery_service.discover_all_workbooks()
        workbook = next((wb for wb in workbooks if wb.workbook_metadata.id == workbook_id), None)
        
        if not workbook:
            raise HTTPException(status_code=404, detail="Workbook not found")
        
        # Analyze unused components
        from app.services.data_model_analyzer import UnusedComponentsAnalyzer
        unused_analyzer = UnusedComponentsAnalyzer()
        
        unused = await unused_analyzer.analyze(
            workbook.data_model,
            workbook.components,
            workbook.usage.dict()
        )
        
        return unused.dict()
    except Exception as e:
        logger.error(f"Unused components error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/shared-data-sources")
async def get_shared_data_sources(
    token: str,
    site_id: str,
    workbook_id: str,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get shared data source analysis
    
    Args:
        token: Tableau authentication token
        site_id: Tableau site ID
        workbook_id: ID of workbook
        current_user: Authenticated user
    
    Returns:
        Dictionary with shared data source analysis
    """
    try:
        discovery_service = DiscoveryService(token, site_id)
        
        # Get workbook data
        workbooks = await discovery_service.discover_all_workbooks()
        workbook = next((wb for wb in workbooks if wb.workbook_metadata.id == workbook_id), None)
        
        if not workbook:
            raise HTTPException(status_code=404, detail="Workbook not found")
        
        # Analyze shared data sources
        from app.services.data_model_analyzer import SharedDataModelAnalyzer
        shared_analyzer = SharedDataModelAnalyzer()
        
        shared_analysis = await shared_analyzer.analyze(
            workbook.data_model,
            workbook.components,
            workbook.mappings.dict()
        )
        
        return shared_analysis.dict()
    except Exception as e:
        logger.error(f"Shared data sources error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint
    
    Returns:
        Status dictionary
    """
    return {
        "status": "healthy",
        "service": "Tableau Pre-Migration Analysis API"
    }
