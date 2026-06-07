"""Approval Center: the human-in-the-loop queue across all agents."""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.approval import Approval
from app.models.creative import CreativeAsset
from app.models.tenant import User
from app.models.trip import Trip
from app.schemas.trip import ApprovalDecision, ApprovalOut

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("", response_model=list[ApprovalOut])
async def list_approvals(
    status: str = "pending",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Approval]:
    result = await db.execute(
        select(Approval).where(Approval.status == status).order_by(Approval.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("/{approval_id}/decide", response_model=ApprovalOut)
async def decide_approval(
    approval_id: uuid.UUID,
    payload: ApprovalDecision,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Approval:
    approval = await db.get(Approval, approval_id)
    if approval is None:
        raise HTTPException(status_code=404, detail="Approval not found")

    approval.status = payload.decision
    approval.decided_by = user.id
    approval.decided_at = datetime.now(timezone.utc)

    # Propagate the decision to the underlying entity.
    if approval.entity_type == "trip":
        trip = await db.get(Trip, approval.entity_id)
        if trip is not None and payload.decision == "approved":
            trip.status = "approved"
    elif approval.entity_type == "creative_asset":
        asset = await db.get(CreativeAsset, approval.entity_id)
        if asset is not None:
            asset.status = payload.decision

    return approval
