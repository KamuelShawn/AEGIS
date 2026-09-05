from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import decisions, environment, google_maps, industry, infrastructure, regions, resources, scenarios, status

app = FastAPI(
    title="SUSTAINA API",
    description="Develop Without Destroying — sustainability intelligence & geospatial decision platform.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(status.router)
app.include_router(regions.router)
app.include_router(environment.router)
app.include_router(resources.router)
app.include_router(infrastructure.router)
app.include_router(industry.router)
app.include_router(decisions.router)
app.include_router(scenarios.router)
app.include_router(google_maps.router)


@app.get("/")
def root():
    return {"name": "SUSTAINA API", "status": "running", "docs": "/docs"}
