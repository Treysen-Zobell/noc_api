# Standard Library Imports
import json

# Third Party Imports
import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.routing import APIRoute
from fastapi_utils.tasks import repeat_every

from app.services.exceptions import CmsDeauthenticationFailure
from app.routes.v1 import cms
from app.services.cms import CmsClient

# Local App Imports
from app.services.environment import API_URL, CMS_IP, CMS_USERNAME, CMS_PASSWORD


def custom_generate_unique_id(route: APIRoute) -> str:
    """
    Generate unique id for route using the routes name

    Args:
        route (APIRoute): The route object

    Returns:
        str: Name of the route
    """
    return f"{route.name}"


app = FastAPI(
    generate_unique_id_function=custom_generate_unique_id,
    servers=json.loads(API_URL),
    version="v0.0.0",
    title="Dashboard API",
    # description="Dashboard API Schema",
)  # This is used for code generation

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(cms.router)

# Persistent connections
cms_client = CmsClient(CMS_IP, CMS_USERNAME, CMS_PASSWORD)
app.state.cms = cms_client


@app.on_event("startup")
@repeat_every(seconds=60 * 30)
def reauthenticate_cms() -> None:
    try:
        cms_client.logout()
    except CmsDeauthenticationFailure:
        pass
    cms_client.login()


@app.get("/ping", tags=["ping"])
async def pong():
    """
    Api route to check if api is running

    Returns:
        dict: ping:pong!
    """
    return {"ping": "pong!"}


@app.on_event("shutdown")
async def app_shutdown():
    cms_client.logout()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", port=8003, reload=True, host="0.0.0.0", proxy_headers=True
    )

# poetry shell
# uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
# python -m unittest
