from fastapi import APIRouter, Depends, HTTPException, Query, status

from login import crud, schemas
from login.deps import get_session

router = APIRouter(tags=["hospitals"])


@router.get("/hospitals", response_model=schemas.HospitalList)
async def list_hospitals(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    session=Depends(get_session),
):
    items, total = await crud.list_hospitals(session, q, page, size)
    return schemas.HospitalList(
        items=[
            schemas.HospitalPublic(
                id=i.id,
                name=i.name,
                is_open=i.is_open,
                distance_km=i.distance_km,
                address=i.address,
                er_beds=i.er_beds,
                operating_rooms=i.operating_rooms,
            )
            for i in items
        ],
        page=page,
        size=size,
        total=total,
    )


@router.get("/hospitals/{hospital_id}", response_model=schemas.HospitalPublic)
async def get_hospital(hospital_id: int, session=Depends(get_session)):
    hospital = await crud.get_hospital_by_id(session, hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="hospital not found")
    return schemas.HospitalPublic(
        id=hospital.id,
        name=hospital.name,
        is_open=hospital.is_open,
        distance_km=hospital.distance_km,
        address=hospital.address,
        er_beds=hospital.er_beds,
        operating_rooms=hospital.operating_rooms,
    )


@router.api_route("/hospitals", methods=["POST", "PUT", "PATCH", "DELETE"])
@router.api_route("/hospitals/{hospital_id}", methods=["POST", "PUT", "PATCH", "DELETE"])
async def hospitals_method_not_allowed(*_args, **_kwargs):
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="hospitals are read-only resources",
    )
