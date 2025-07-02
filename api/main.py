from fastapi import FastAPI
from api.routes import devices, activities, wallets, activity_types

app = FastAPI(title="Silvanus GreenChain API")

app.include_router(devices.router, prefix="/devices", tags=["Devices"])
app.include_router(activities.router, prefix="/activities", tags=["Activities"])
app.include_router(wallets.router, tags=["Wallets"])
app.include_router(activity_types.router, tags=["Activity Types"])

