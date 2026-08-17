import requests
from config import TABLEAU_SERVER, API_VERSION


def signin_with_credentials(
    username: str,
    password: str,
    site_content_url: str = ""
) -> tuple[str, str]:
    """
    Authenticate with Tableau Server using credentials.
    
    Args:
        username: Tableau username
        password: Tableau password
        site_content_url: Tableau site content URL
    
    Returns:
        Tuple of (token, site_id)
    """
    url = (
        f"{TABLEAU_SERVER}"
        f"/api/{API_VERSION}/auth/signin"
    )

    payload = {
        "credentials": {
            "name": username,
            "password": password,
            "site": {
                "contentUrl": site_content_url
            }
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers
    )

    response.raise_for_status()

    data = response.json()

    return (
        data["credentials"]["token"],
        data["credentials"]["site"]["id"]
    )
