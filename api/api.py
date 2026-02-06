from fastapi import APIRouter

from api.routers import auth, users, assets, datasets, models, training, predictions, feedback, simulation

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(training.router, prefix="/train", tags=["training"])
api_router.include_router(predictions.router, prefix="/predict", tags=["predictions"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(simulation.router, prefix="/simulation", tags=["simulation"])
