# Tableau Pre-Migration Analysis API

A comprehensive FastAPI-based solution for analyzing Tableau workbooks and generating actionable insights for migration to Power BI.

## Overview

This application provides deep analysis of Tableau environments to facilitate informed decision-making during migration projects. It leverages AI-powered analysis to identify optimization opportunities, assess complexity, and recommend migration strategies.

## Key Features

### 1. **Workbook Discovery & Metadata Extraction**
- Connects to Tableau Server/Cloud via REST API
- Extracts comprehensive metadata from workbooks
- Analyzes worksheets, dashboards, filters, parameters, and data sources
- Supports direct .twb/.twbx file uploads for offline analysis

### 2. **Usage Pattern Analysis**
- Identifies least-used and unused reports
- Tracks view access patterns and frequencies
- Provides data-driven recommendations for component optimization
- Helps prioritize migration efforts based on actual usage

### 3. **KPI Intelligence**
- Automatic KPI detection and cataloging
- Identifies duplicate and similar KPIs across workbooks
- Recommends KPI consolidation opportunities
- Maps KPIs to metrics and dimensions

### 4. **Complexity Assessment**
- Calculates complexity scores for workbooks and components
- Analyzes dashboard density and worksheet dependencies
- Evaluates filter and parameter complexity
- Provides overall complexity ratings (0-1 scale)

### 5. **Migration Strategy Recommendations**
- Generates multiple migration approaches (Big Bang, Phased, Hybrid)
- Estimates effort and timelines for each strategy
- Assesses risk levels and resource requirements
- Provides detailed step-by-step migration plans

### 6. **Data Model Analysis**
- Identifies shared data sources and consolidation opportunities
- Recommends Power BI semantic models
- Analyzes datasource-to-report mappings
- Prioritizes data reuse opportunities

### 7. **Impact Assessment**
- Evaluates migration risks and dependencies
- Identifies unused components for potential retirement
- Analyzes data refresh overhead
- Provides mitigation recommendations

## API Endpoints

### Discovery
```
POST /api/v1/analysis/discover-workbooks
```
Discover all workbooks in a Tableau environment.

**Parameters:**
- `token`: Tableau authentication token
- `site_id`: Tableau site ID

**Response:**
```json
{
  "status": "success",
  "count": 25,
  "workbooks": [...]
}
```

### Complete Analysis
```
POST /api/v1/analysis/analyze-workbook
```
Perform complete analysis of a single workbook.

**Parameters:**
- `token`: Tableau authentication token
- `site_id`: Tableau site ID
- `workbook_id`: ID of workbook to analyze

**Response:**
```json
{
  "status": "success",
  "workbook_metadata": {...},
  "usage_analysis": {...},
  "kpi_intelligence": {...},
  "complexity_analysis": {...},
  "migration_strategies": {...},
  "impact_assessment": {...}
}
```

### File Upload
```
POST /api/v1/analysis/upload-workbook
```
Upload and analyze a .twb or .twbx file directly.

**Parameters:**
- `file`: Workbook file (.twb or .twbx)

**Response:**
```json
{
  "status": "success",
  "filename": "sales_dashboard.twbx",
  "parsed_metadata": {...}
}
```

### Unused Components
```
GET /api/v1/analysis/unused-components
```
Identify unused components in a workbook.

**Parameters:**
- `token`: Tableau authentication token
- `site_id`: Tableau site ID
- `workbook_id`: Workbook ID

**Response:**
```json
{
  "unused_worksheets": [...],
  "unused_calculated_fields": [...],
  "unused_filters": [...],
  "unused_parameters": [...],
  "unused_datasources": [...]
}
```

### Shared Data Sources
```
GET /api/v1/analysis/shared-data-sources
```
Analyze shared data source opportunities.

**Parameters:**
- `token`: Tableau authentication token
- `site_id`: Tableau site ID
- `workbook_id`: Workbook ID

**Response:**
```json
{
  "shared_datasources": [...],
  "shared_tables": [...],
  "recommended_semantic_models": [...]
}
```

### Health Check
```
GET /api/v1/analysis/health
```
Verify API health status.

## Installation

### Prerequisites
- Python 3.8+
- OpenAI API key (for AI-powered analysis)
- Tableau Server/Cloud access (optional, for live discovery)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/Revanth-Nannaveni/tableau-pre-migration-analysis.git
cd tableau-pre-migration-analysis
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

**Required environment variables:**
```
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4-turbo
TABLEAU_API_URL=https://tableau-server.example.com
DEBUG=false
ALLOWED_ORIGINS=["http://localhost:3000"]
```

5. **Run the application**
```bash
python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Architecture

### Core Services

#### `DiscoveryService`
Handles connection to Tableau and metadata extraction.
- Connects via Tableau REST API
- Parses workbook XML for detailed metadata
- Supports both Server and Cloud environments

#### `LeastUsedReportsAnalyzer`
Analyzes usage patterns using OpenAI.
- Identifies least-used components
- Recommends optimization opportunities
- Provides consolidation suggestions

#### `KPIIntelligenceAnalyzer`
Catalogs and analyzes KPIs across workbooks.
- Detects duplicate KPIs
- Identifies similar metrics
- Recommends consolidation

#### `ComplexityAnalyzer`
Assesses workbook complexity.
- Scores individual components
- Calculates overall complexity
- Identifies complexity drivers

#### `MigrationStrategyAnalyzer`
Generates migration strategies.
- Recommends multiple approaches
- Estimates effort and timelines
- Assesses risk levels

#### `ImpactAnalyzer`
Evaluates migration impact.
- Identifies dependencies
- Assesses risks
- Provides mitigation strategies

#### `SharedDataModelAnalyzer`
Analyzes data model consolidation opportunities.
- Identifies shared datasources
- Recommends semantic models
- Prioritizes reuse opportunities

#### `UnusedComponentsAnalyzer`
Catalogs unused components.
- Identifies retirement candidates
- Estimates cleanup impact
- Provides removal recommendations

## Data Models

### WorkbookMetadata
```python
{
  "id": "string",
  "name": "string",
  "owner": "string",
  "description": "string",
  "created_at": "datetime",
  "modified_at": "datetime",
  "project_id": "string"
}
```

### ComplexityAnalysisResponse
```python
{
  "complexity_scores": [
    {
      "component": "string",
      "score": 0.75,
      "reasoning": "string"
    }
  ],
  "overall_complexity_score": 0.65,
  "complexity_summary": "string"
}
```

### MigrationStrategiesResponse
```python
{
  "strategies": [
    {
      "strategy_name": "string",
      "description": "string",
      "effort_estimate": "string",
      "risk_level": "string",
      "key_steps": ["string"],
      "estimated_timeline": "string",
      "resource_requirements": ["string"]
    }
  ],
  "recommended_strategy": "string",
  "overall_assessment": "string"
}
```

## Usage Examples

### Example 1: Discover Workbooks
```bash
curl -X POST "http://localhost:8000/api/v1/analysis/discover-workbooks" \
  -H "Content-Type: application/json" \
  -d {
    "token": "your_tableau_token",
    "site_id": "your_site_id"
  }
```

### Example 2: Analyze Workbook
```bash
curl -X POST "http://localhost:8000/api/v1/analysis/analyze-workbook" \
  -H "Content-Type: application/json" \
  -d {
    "token": "your_tableau_token",
    "site_id": "your_site_id",
    "workbook_id": "workbook_id"
  }
```

### Example 3: Upload File
```bash
curl -X POST "http://localhost:8000/api/v1/analysis/upload-workbook" \
  -F "file=@sales_dashboard.twbx"
```

## Configuration

### config.py
```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
TABLEAU_API_URL = os.getenv("TABLEAU_API_URL")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ALLOWED_ORIGINS = json.loads(os.getenv("ALLOWED_ORIGINS", '["http://localhost:3000"]'))
```

## Best Practices

1. **Start with Discovery**: Use `discover-workbooks` to get an inventory of your environment
2. **Analyze High-Impact Workbooks First**: Focus on frequently used workbooks with complex logic
3. **Review Migration Strategies**: Consider multiple approaches before deciding on a strategy
4. **Plan Iteratively**: Use phased migration for large environments
5. **Monitor Impact**: Track metrics before and after migration

## Troubleshooting

### Issue: "OpenAI API key not found"
**Solution:** Ensure `OPENAI_API_KEY` is set in `.env` file

### Issue: "Tableau authentication failed"
**Solution:** Verify token validity and site_id are correct

### Issue: "File upload failed"
**Solution:** Ensure file is .twb or .twbx format and not corrupted

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: Revanth.Nannaveni@quadranttechnologies.com

## Version History

### v1.0.0 (Current)
- Initial release
- Complete workbook discovery and analysis
- AI-powered complexity and strategy recommendations
- Data model analysis and consolidation opportunities
- Impact assessment and migration planning

---

**Built with ❤️ for Tableau to Power BI migrations**
