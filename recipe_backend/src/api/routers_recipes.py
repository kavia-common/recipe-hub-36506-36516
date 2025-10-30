from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.core.security import oauth2_scheme, decode_token
from src.db.models import Recipe, User
from src.db.schemas import Recipe as RecipeSchema, RecipeCreate, RecipeUpdate
from src.db.session import get_db

router = APIRouter(prefix="/recipes", tags=["Recipes"])


def _get_current_user(db: Session, token: str) -> User:
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=RecipeSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create recipe",
    description="Create a new recipe owned by the authenticated user.",
)
def create_recipe(
    recipe_in: RecipeCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> RecipeSchema:
    """Create a recipe for the current user."""
    user = _get_current_user(db, token)
    recipe = Recipe(
        title=recipe_in.title,
        description=recipe_in.description,
        ingredients=recipe_in.ingredients,
        steps=recipe_in.steps,
        owner_id=user.id,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[RecipeSchema],
    summary="List recipes",
    description="List recipes with optional search over title/description and simple tags support in description. Supports pagination.",
)
def list_recipes(
    q: Optional[str] = Query(None, description="Search query over title/description/tags"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max number of records to return"),
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> List[RecipeSchema]:
    """
    List recipes. If authenticated, returns all recipes (public scope). In a future
    iteration we can add visibility flags. Currently returns all recipes regardless of owner.
    """
    query = db.query(Recipe)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Recipe.title.ilike(like), Recipe.description.ilike(like), Recipe.ingredients.ilike(like)))
    recipes = query.order_by(Recipe.created_at.desc()).offset(skip).limit(limit).all()
    return recipes


# PUBLIC_INTERFACE
@router.get(
    "/{recipe_id}",
    response_model=RecipeSchema,
    summary="Get recipe by ID",
    description="Retrieve a recipe by its identifier.",
)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)) -> RecipeSchema:
    """Get a single recipe."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return recipe


# PUBLIC_INTERFACE
@router.put(
    "/{recipe_id}",
    response_model=RecipeSchema,
    summary="Update recipe",
    description="Update a recipe. Only the owner can update the recipe.",
)
def update_recipe(
    recipe_id: int,
    recipe_in: RecipeUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> RecipeSchema:
    """Update an existing recipe owned by the current user."""
    user = _get_current_user(db, token)
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    if recipe.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this recipe")

    # Apply updates if provided
    if recipe_in.title is not None:
        recipe.title = recipe_in.title
    if recipe_in.description is not None:
        recipe.description = recipe_in.description
    if recipe_in.ingredients is not None:
        recipe.ingredients = recipe_in.ingredients
    if recipe_in.steps is not None:
        recipe.steps = recipe_in.steps

    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


# PUBLIC_INTERFACE
@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete recipe",
    description="Delete a recipe. Only the owner can delete the recipe.",
)
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> None:
    """Delete a recipe owned by the current user."""
    user = _get_current_user(db, token)
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    if recipe.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this recipe")

    db.delete(recipe)
    db.commit()
    return None
