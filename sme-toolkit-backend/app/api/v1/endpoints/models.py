"""
Models API Endpoints
Handles model listing, selection, and preferences
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.services.model_management_service import ModelManagementService
from app.auth import get_current_user

router = APIRouter(prefix="/models", tags=["Models"])


class ModelPreferenceUpdate(BaseModel):
    modality: str  # llm, image, video
    model_id: str
    provider_id: str


class ModelPreferenceResponse(BaseModel):
    model_id: Optional[str]
    provider_id: Optional[str]
    modality: str


@router.get("/available/{modality}")
async def get_available_models(
    modality: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get available models for a modality based on user's tier
    
    Modality can be: llm, image, video
    """
    if modality not in ["llm", "image", "video"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid modality: {modality}. Must be llm, image, or video",
        )

    service = ModelManagementService(db)
    models = await service.get_available_models(current_user, modality)
    
    return {
        "modality": modality,
        "providers": models,
        "total_models": sum(len(p["models"]) for p in models),
    }


@router.get("/preference/{modality}")
async def get_model_preference(
    modality: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user's preferred model for a modality
    """
    if modality not in ["llm", "image", "video"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid modality: {modality}",
        )

    service = ModelManagementService(db)
    preference = await service.get_user_model_preference(current_user, modality)
    
    return ModelPreferenceResponse(
        modality=modality,
        **preference,
    )


@router.put("/preference")
async def set_model_preference(
    preference: ModelPreferenceUpdate,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Set user's preferred model for a modality
    """
    if preference.modality not in ["llm", "image", "video"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid modality: {preference.modality}",
        )

    service = ModelManagementService(db)
    
    try:
        await service.set_user_model_preference(
            user_id=current_user,
            modality=preference.modality,
            model_id=preference.model_id,
            provider_id=preference.provider_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    return {
        "success": True,
        "message": f"Model preference updated for {preference.modality}",
        "preference": {
            "modality": preference.modality,
            "model_id": preference.model_id,
            "provider_id": preference.provider_id,
        },
    }


@router.get("/cost/{modality}/{provider_id}/{model_id}")
async def get_model_cost(
    modality: str,
    provider_id: str,
    model_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get cost information for a specific model
    """
    service = ModelManagementService(db)
    cost_info = await service.get_model_cost(modality, model_id, provider_id)
    
    if "error" in cost_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=cost_info["error"],
        )

    return cost_info


@router.get("/all")
async def get_all_models(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all available models across all modalities
    """
    service = ModelManagementService(db)
    
    llm_models = await service.get_available_models(current_user, "llm")
    image_models = await service.get_available_models(current_user, "image")
    video_models = await service.get_available_models(current_user, "video")

    return {
        "llm": {
            "providers": llm_models,
            "total": sum(len(p["models"]) for p in llm_models),
        },
        "image": {
            "providers": image_models,
            "total": sum(len(p["models"]) for p in image_models),
        },
        "video": {
            "providers": video_models,
            "total": sum(len(p["models"]) for p in video_models),
        },
    }
