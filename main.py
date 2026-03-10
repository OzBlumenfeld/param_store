from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.core.database import engine
from app.models.parameter import Base
from app.models.user import User
from app.api.parameters import router as params_router
from app.api.auth import router as auth_router
from app.core.logger import setup_logging

# Initialize global logging and get the root logger
logger = setup_logging()

app = FastAPI(title="OB Company Secure Parameter Store")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# All routes from this router will now start with /params because of its internal prefix
app.include_router(params_router)
app.include_router(auth_router)

if __name__ == "__main__":
    port = 8181
    logger.info("Server is starting", extra={"port": port})
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
