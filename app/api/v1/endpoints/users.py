from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, require_role
from app.models.user import User, KYCDocument
from app.schemas.user_schemas import UserResponse, UserUpdateRequest, KYCDocumentResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(data: UserUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if data.name is not None:
        current_user.name = data.name
    if data.email is not None:
        existing = db.query(User).filter(User.email == data.email, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
        current_user.email = data.email
    if data.location is not None:
        current_user.location = data.location

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/kyc", response_model=KYCDocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_kyc(
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # MVP: store file path locally. S3 upload is a stretch goal.
    import shutil
    import os

    upload_dir = "uploads/kyc"
    os.makedirs(upload_dir, exist_ok=True)

    file_ext = file.filename.split(".")[-1]
    file_name = f"{current_user.id}_{doc_type}.{file_ext}"
    file_path = f"{upload_dir}/{file_name}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc = KYCDocument(
        user_id=current_user.id,
        doc_type=doc_type,
        doc_url=file_path,
    )
    db.add(doc)

    if current_user.kyc_status.value == "none":
        current_user.kyc_status = "pending"

    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user