import logging

from fastapi import APIRouter

from app.calculator import build_compound_products
from app.rei_data import build_rei_table

logger = logging.getLogger("rei_data")

router = APIRouter()

_REI_TABLE, _MISSING_REI_DATA = build_rei_table()
_COMPOUND_PRODUCTS = build_compound_products()

if _MISSING_REI_DATA:
    logger.warning("data/rei_results.json에 채워지지 않은 조합이 %d건 있습니다:", len(_MISSING_REI_DATA))
    for line in _MISSING_REI_DATA:
        logger.warning("  - %s", line)


@router.get("/api/rei-table")
def get_rei_table():
    return _REI_TABLE


@router.get("/api/compound-products")
def get_compound_products():
    return _COMPOUND_PRODUCTS


@router.get("/api/debug/missing-rei-data")
def get_missing_rei_data():
    return {"count": len(_MISSING_REI_DATA), "missing": _MISSING_REI_DATA}
