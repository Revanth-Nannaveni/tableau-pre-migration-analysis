import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
import io


class TWBParser:
    """Parser for Tableau Workbook (.twb) files"""
    
    @staticmethod
    def parse(file_content: bytes) -> Dict[str, Any]:
        """
        Parse a .twb file and extract metadata
        
        Args:
            file_content: Binary content of .twb file
        
        Returns:
            Dictionary containing extracted metadata
        """
        try:
            root = ET.fromstring(file_content)
            return TWBParser._extract_metadata(root)
        except Exception as e:
            return {"error": f"Failed to parse TWB file: {str(e)}"}
    
    @staticmethod
    def _extract_metadata(root: ET.Element) -> Dict[str, Any]:
        """Extract metadata from XML root element"""
        metadata = {
            "calculated_fields": [],
            "lod_expressions": [],
            "table_calculations": [],
            "parameters": [],
            "filters": [],
            "relationships": [],
            "custom_sql": [],
            "dashboards": [],
            "worksheets": []
        }
        
        # Extract calculated fields
        for calc in root.findall(".//column[@caption]"):
            if calc.find("calculation") is not None:
                metadata["calculated_fields"].append({
                    "name": calc.get("caption"),
                    "formula": calc.find("calculation").get("formula")
                })
        
        # Extract LOD expressions
        for lod in root.findall(".//table-calc[@type='LOD']"):
            metadata["lod_expressions"].append({
                "name": lod.get("name"),
                "expression": lod.find("expression").text if lod.find("expression") is not None else None
            })
        
        # Extract table calculations
        for tc in root.findall(".//table-calc[@type='Table']"):
            metadata["table_calculations"].append({
                "name": tc.get("name"),
                "expression": tc.find("expression").text if tc.find("expression") is not None else None
            })
        
        # Extract parameters
        for param in root.findall(".//parameter"):
            metadata["parameters"].append({
                "name": param.get("name"),
                "data_type": param.get("type"),
                "default_value": param.get("value")
            })
        
        # Extract filters
        for filt in root.findall(".//filter"):
            metadata["filters"].append({
                "name": filt.get("name"),
                "field": filt.get("column"),
                "type": filt.get("type")
            })
        
        # Extract relationships
        for rel in root.findall(".//relation"):
            metadata["relationships"].append({
                "name": rel.get("name"),
                "type": rel.get("type"),
                "join_clause": rel.get("join")
            })
        
        # Extract custom SQL
        for sql in root.findall(".//sql"):
            metadata["custom_sql"].append({
                "query": sql.text
            })
        
        # Extract dashboards
        for dash in root.findall(".//dashboard"):
            metadata["dashboards"].append({
                "name": dash.get("name"),
                "size": dash.get("size"),
                "zone_ordering_type": dash.get("zone-ordering-type")
            })
        
        # Extract worksheets
        for ws in root.findall(".//worksheet"):
            metadata["worksheets"].append({
                "name": ws.get("name"),
                "table": ws.get("table")
            })
        
        return metadata


class TWBXParser:
    """Parser for Tableau Workbook Extract (.twbx) files"""
    
    @staticmethod
    def parse(file_content: bytes) -> Dict[str, Any]:
        """
        Parse a .twbx file and extract metadata
        
        Args:
            file_content: Binary content of .twbx file
        
        Returns:
            Dictionary containing extracted metadata
        """
        try:
            with zipfile.ZipFile(io.BytesIO(file_content)) as zip_ref:
                # Find and extract the .twb file
                twb_files = [f for f in zip_ref.namelist() if f.endswith('.twb')]
                
                if not twb_files:
                    return {"error": "No .twb file found in .twbx archive"}
                
                # Extract and parse the main .twb file
                twb_content = zip_ref.read(twb_files[0])
                metadata = TWBParser.parse(twb_content)
                
                # Extract data extracts (.hyper, .tde, .csv)
                metadata["data_extracts"] = TWBXParser._extract_data_extracts(zip_ref)
                
                return metadata
        except Exception as e:
            return {"error": f"Failed to parse TWBX file: {str(e)}"}
    
    @staticmethod
    def _extract_data_extracts(zip_ref: zipfile.ZipFile) -> List[Dict[str, Any]]:
        """Extract information about data extracts in the archive"""
        extracts = []
        
        for file_info in zip_ref.infolist():
            if file_info.filename.endswith(('.hyper', '.tde', '.csv')):
                extracts.append({
                    "filename": file_info.filename,
                    "size_bytes": file_info.file_size,
                    "type": file_info.filename.split('.')[-1]
                })
        
        return extracts
