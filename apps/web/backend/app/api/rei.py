from fastapi import APIRouter

from app.calculator import build_compound_products, build_rei_table

router = APIRouter()

_REI_TABLE = build_rei_table()
_COMPOUND_PRODUCTS = build_compound_products()


@router.get("/api/rei-table")
def get_rei_table():
    return _REI_TABLE


@router.get("/api/compound-products")
def get_compound_products():
    return _COMPOUND_PRODUCTS
