import httpx
from typing import Optional, Dict, Any
import json
from config import TABLEAU_SERVER, API_VERSION


class TableauMetadataAPI:
    """Tableau Metadata API (GraphQL) client"""
    
    def __init__(self, token: str, site_id: str):
        self.token = token
        self.site_id = site_id
        self.base_url = f"{TABLEAU_SERVER}/api/{API_VERSION}"
        self.graphql_url = f"{TABLEAU_SERVER}/api/metadata/graphql"
    
    async def get_workbooks(self) -> list[Dict[str, Any]]:
        """Fetch all workbooks using GraphQL"""
        query = """
        {
            workbooksConnection {
                edges {
                    node {
                        id
                        name
                        description
                        owner {
                            id
                            username
                        }
                        project {
                            id
                            name
                        }
                        createdAt
                        modifiedAt
                        updatedAt
                    }
                }
            }
        }
        """
        
        return await self._execute_graphql_query(query)
    
    async def get_dashboards(self) -> list[Dict[str, Any]]:
        """Fetch all dashboards using GraphQL"""
        query = """
        {
            dashboardsConnection {
                edges {
                    node {
                        id
                        name
                        description
                        workbook {
                            id
                            name
                        }
                        createdAt
                        modifiedAt
                    }
                }
            }
        }
        """
        
        return await self._execute_graphql_query(query)
    
    async def get_datasources(self) -> list[Dict[str, Any]]:
        """Fetch all data sources using GraphQL"""
        query = """
        {
            datasourcesConnection {
                edges {
                    node {
                        id
                        name
                        description
                        owner {
                            id
                            username
                        }
                        database {
                            id
                            name
                        }
                        createdAt
                        modifiedAt
                    }
                }
            }
        }
        """
        
        return await self._execute_graphql_query(query)
    
    async def get_fields(self, datasource_id: str) -> list[Dict[str, Any]]:
        """Fetch fields for a data source"""
        query = f"""
        {{
            datasource(id: "{datasource_id}") {{
                fields {{
                    id
                    name
                    dataType
                    role
                    aggregation
                }}
            }}
        }}
        """
        
        return await self._execute_graphql_query(query)
    
    async def get_lineage(self, datasource_id: str) -> Dict[str, Any]:
        """Fetch data lineage for a data source"""
        query = f"""
        {{
            datasource(id: "{datasource_id}") {{
                upstreamDatasources {{
                    id
                    name
                }}
                downstreamDatasources {{
                    id
                    name
                }}
                upstreamTables {{
                    id
                    name
                    schema
                    database
                }}
            }}
        }}
        """
        
        return await self._execute_graphql_query(query)
    
    async def _execute_graphql_query(self, query: str) -> Dict[str, Any]:
        """Execute a GraphQL query"""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "query": query
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.graphql_url,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            data = response.json()
            
            if "errors" in data:
                raise Exception(f"GraphQL Error: {data['errors']}")
            
            return data.get("data", {})


class TableauRestAPI:
    """Tableau REST API client"""
    
    def __init__(self, token: str, site_id: str):
        self.token = token
        self.site_id = site_id
        self.base_url = f"{TABLEAU_SERVER}/api/{API_VERSION}/sites/{site_id}"
    
    async def get_workbooks(self) -> list[Dict[str, Any]]:
        """Fetch all workbooks"""
        url = f"{self.base_url}/workbooks"
        
        headers = {
            "X-Tableau-Auth": self.token,
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            
            data = response.json()
            return data.get("pagination", {}).get("_links", [])
    
    async def get_workbook_details(self, workbook_id: str) -> Dict[str, Any]:
        """Fetch workbook details"""
        url = f"{self.base_url}/workbooks/{workbook_id}"
        
        headers = {
            "X-Tableau-Auth": self.token,
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            
            return response.json()
    
    async def get_views(self, workbook_id: str) -> list[Dict[str, Any]]:
        """Fetch views/worksheets for a workbook"""
        url = f"{self.base_url}/workbooks/{workbook_id}/views"
        
        headers = {
            "X-Tableau-Auth": self.token,
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            
            return response.json().get("view", [])
    
    async def get_datasources(self) -> list[Dict[str, Any]]:
        """Fetch all data sources"""
        url = f"{self.base_url}/datasources"
        
        headers = {
            "X-Tableau-Auth": self.token,
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            
            return response.json().get("datasource", [])
    
    async def get_datasource_details(self, datasource_id: str) -> Dict[str, Any]:
        """Fetch data source details"""
        url = f"{self.base_url}/datasources/{datasource_id}"
        
        headers = {
            "X-Tableau-Auth": self.token,
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            
            return response.json()
    
    async def get_view_stats(self, view_id: str) -> Dict[str, Any]:
        """Fetch view statistics"""
        url = f"{self.base_url}/views/{view_id}/usage"
        
        headers = {
            "X-Tableau-Auth": self.token,
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            
            return response.json()
    
    async def get_permissions(self, resource_type: str, resource_id: str) -> list[Dict[str, Any]]:
        """Fetch permissions for a resource"""
        url = f"{self.base_url}/{resource_type}/{resource_id}/permissions"
        
        headers = {
            "X-Tableau-Auth": self.token,
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            
            return response.json().get("granteeCapabilities", [])
