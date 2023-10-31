
from fastapi import FastAPI
from routers import *


app = FastAPI()


app.include_router(
    account_controller,
    prefix="/api/Account",
    tags=["AccountController"],
)

app.include_router(
    admin_account_controller,
    prefix="/api/Admin/Account",
    tags=["AdminAccountController"],
)

app.include_router(
    payment_controller,
    prefix="/api/Payment",
    tags=["PaymentController"],
)

app.include_router(
    transport_controller,
    prefix="/api/Transport",
    tags=["TransportController"],
)

app.include_router(
    admin_transport_controller,
    prefix="/api/Admin/Transport",
    tags=["AdminTransportController"],
)

app.include_router(
    rent_controller,
    prefix="/api/Rent",
    tags=["RentController"],
)

app.include_router(
    admin_rent_controller,
    prefix="/api/Admin",
    tags=["AdminRentController"],
)


