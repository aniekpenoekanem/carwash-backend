from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
import csv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, date
import sqlalchemy
from databases import Database
from dotenv import load_dotenv
import uuid
import httpx
import os
import hashlib
import hmac
from fastapi import Request
from typing import Optional

load_dotenv()

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")

if not PAYSTACK_SECRET_KEY:
    raise RuntimeError(
        "PAYSTACK_SECRET_KEY not found."
    )

print("Paystack key loaded:", bool(PAYSTACK_SECRET_KEY))

# ======================
# DATABASE CONFIG
# ======================
BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
   f"sqlite+aiosqlite:///{os.path.join(BASE_DIR, 'carwash.db')}"
)

SYNC_DATABASE_URL = DATABASE_URL.replace(
    "sqlite+aiosqlite:///",
    "sqlite:///"
)

database = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# ======================
# TABLES
# ======================

services = sqlalchemy.Table(
    "services",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("price", sqlalchemy.Float),
)

bookings = sqlalchemy.Table(
    "bookings",
    metadata,
    sqlalchemy.Column("payment_date", sqlalchemy.DateTime),
    sqlalchemy.Column("payment_channel", sqlalchemy.String),
    sqlalchemy.Column("status", sqlalchemy.String, default="service_pending"),
    sqlalchemy.Column("payment_status", sqlalchemy.String, default="unpaid"),
    sqlalchemy.Column("payment_reference", sqlalchemy.String, unique=True),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, default=datetime.utcnow),
    sqlalchemy.Column("phone_number", sqlalchemy.String),
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("service", sqlalchemy.String),
    sqlalchemy.Column("amount", sqlalchemy.Float),
    sqlalchemy.Column("booking_time", sqlalchemy.String),
    sqlalchemy.Column("car_brand", sqlalchemy.String),
    sqlalchemy.Column("car_model", sqlalchemy.String),
    sqlalchemy.Column("email", sqlalchemy.String),
)

print("Tables registered:", list(metadata.tables.keys()))

engine = sqlalchemy.create_engine(SYNC_DATABASE_URL)

print("Creating tables...")
metadata.create_all(engine)
print("Database tables created successfully.")
    
# ======================
# APP INIT
# ======================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# CAR DATA
# ======================

@app.get("/cars")
async def get_cars():
    return {
        "Toyota": ["Corolla", "Camry", "Highlander"],
        "Honda": ["Accord", "Civic", "CR-V"],
        "Lexus": ["RX 350", "ES 350"],
        "Mercedes": ["C300", "E350"]
    }

# ✅ CAR TYPE MAPPING
CAR_TYPE = {
    "Corolla": "Sedan",
    "Camry": "Sedan",
    "Highlander": "SUV",
    "Accord": "Sedan",
    "Civic": "Sedan",
    "CR-V": "SUV",
    "RX 350": "SUV",
    "ES 350": "Sedan",
    "C300": "Sedan",
    "E350": "Sedan",
}

# ======================
# MODELS
# ======================

class BookingCreate(BaseModel):
    customer_name: str
    email: Optional[str] = None
    phone_number: str
    service_id: int
    booking_time: str
    car_brand: str
    car_model: str


class ServiceCreate(BaseModel):
    name: str
    price: float


class ServiceUpdate(BaseModel):
    name: str
    price: float

# ======================
# STARTUP / SHUTDOWN
# ======================

@app.on_event("startup")
async def startup():
    print("Startup event running...")
    await database.connect()

    query = services.select()
    existing = await database.fetch_all(query)

    if not existing:
        default_services = [
            {"name": "Basic Wash", "price": 1000},
            {"name": "Premium Wash", "price": 2000},
            {"name": "Full Service", "price": 3500},
        ]
        for svc in default_services:
            await database.execute(services.insert().values(**svc))


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# ======================
# ROUTES
# ======================

@app.get("/")
async def root():
    return {"message": "Car Wash API is running 🚀",
            "docs": "/docs",
            "status": "online"}



# ======================
# ADMIN LOGIN
# ======================

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
async def login(data: LoginRequest):
    if data.username == ADMIN_USERNAME and data.password == ADMIN_PASSWORD:
        return {"token": "secure_admin_token"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# ======================
# SERVICES
# ======================

@app.get("/services")
async def get_services():
    query = services.select()
    return await database.fetch_all(query)


@app.post("/services")
async def add_service(service: ServiceCreate):
    query = services.insert().values(
        name=service.name,
        price=service.price
    )
    await database.execute(query)
    return {"message": "Service added successfully"}


@app.delete("/services/{service_id}")
async def delete_service(service_id: int):

    query = services.delete().where(
        services.c.id == service_id
    )

    await database.execute(query)

    return {"message": "Service deleted"}

@app.put("/services/{service_id}")
async def update_service(
    service_id: int,
    service: ServiceUpdate
):

    query = services.update().where(
        services.c.id == service_id
    ).values(
        name=service.name,
        price=service.price
    )

    await database.execute(query)

    return {"message": "Service updated"}


# ======================
# PAYMENT INITIALIZATION
# ======================

@app.post("/payments/initialize/{booking_id}")
async def initialize_payment(booking_id: int):

    booking = await database.fetch_one(
        bookings.select().where(
            bookings.c.id == booking_id
        )
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    booking = dict(booking)

    print("BOOKING:", booking)
    print("PAYSTACK EMAIL:", booking.get("email"))

    amount = booking["amount"]

    reference = f"CW_{uuid.uuid4().hex[:12]}"

    await database.execute(
        bookings.update()
        .where(bookings.c.id == booking_id)
        .values(payment_reference=reference)
    )

    payload = {
        "email": booking["email"],
        "amount": int(amount * 100),
        "reference": reference,
        "callback_url": "https://carwash-backend-kv5q.onrender.com/payment-success"
    }
    print("CALLBACK URL:", payload["callback_url"])
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=30) as client:
    print("=" * 60)
    print("PAYLOAD SENT TO PAYSTACK")
    print(payload)
    print("=" * 60)
    response = await client.post(
            "https://api.paystack.co/transaction/initialize",
            json=payload,
            headers=headers
        )

    print("PAYSTACK STATUS:", response.status_code)
    print("PAYSTACK RAW RESPONSE:", response.text)

    data = response.json()

    if response.status_code != 200 or not data.get("status"):
        raise HTTPException(
            status_code=400,
            detail=data.get(
                "message",
                "Payment initialization failed"
            )
        )

    return {
        "payment_url": data["data"]["authorization_url"],
        "reference": reference,
    }

# ======================
# PAYSTACK VERIFICATION
# ======================

async def verify_paystack_payment(reference: str):

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"https://api.paystack.co/transaction/verify/{reference}",
            headers=headers,
        )

    print("VERIFY STATUS:", response.status_code)
    print("VERIFY RESPONSE:", response.text)

    if response.status_code != 200:
        return None

    data = response.json()

    if not data.get("status"):
        return None

    return data["data"]


@app.get("/payments/verify/{reference}")
async def verify_payment(reference: str):

    transaction = await verify_paystack_payment(reference)

    if not transaction:
        raise HTTPException(
            status_code=400,
            detail="Payment verification failed"
        )

    if transaction["status"] != "success":
        raise HTTPException(
            status_code=400,
            detail=f"Payment status: {transaction['status']}"
        )

    booking = await database.fetch_one(
        bookings.select().where(
            bookings.c.payment_reference == reference
        )
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    if booking["payment_status"] == "paid":
        return {
            "message": "Payment already verified",
            "booking_id": booking["id"],
            "reference": reference
        }

    await database.execute(
        bookings.update()
        .where(
            bookings.c.payment_reference == reference
        )
        .values(
            payment_status="paid",
            status="confirmed",
            payment_channel=transaction["channel"],
            payment_date=datetime.utcnow()
        )
    )

    return {
        "message": "Payment verified successfully",
        "booking_id": booking["id"],
        "reference": reference
    }


@app.get("/payment-success", response_class=HTMLResponse)
async def payment_success(
    reference: str | None = None,
    trxref: str | None = None,
):
    print("=" * 60)
    print("PAYMENT CALLBACK HIT")
    print("reference =", reference)
    print("trxref =", trxref)
    print("=" * 60)

    payment_reference = reference or trxref

    if not payment_reference:
        return HTMLResponse(
            content="<h2>Missing payment reference</h2>",
            status_code=400,
        )

    transaction = await verify_paystack_payment(
        payment_reference
    )

    if not transaction:
        return HTMLResponse(
            content="<h2>Payment verification failed</h2>",
            status_code=400,
        )

    booking = await database.fetch_one(
        bookings.select().where(
            bookings.c.payment_reference == payment_reference
        )
    )

    if not booking:
        return HTMLResponse(
            content="<h2>Booking not found</h2>",
            status_code=404,
        )

    if booking["payment_status"] != "paid":

        await database.execute(
            bookings.update()
            .where(
                bookings.c.payment_reference == payment_reference
            )
            .values(
                payment_status="paid",
                status="confirmed",
                payment_channel=transaction["channel"],
                payment_date=datetime.utcnow()
            )
        )

    return f"""
    <html>
        <body style="font-family: Arial; padding: 40px;">
            <h2>Payment verified successfully</h2>
            <p><strong>Reference:</strong> {payment_reference}</p>
            <p><strong>Amount:</strong> ₦{transaction['amount'] / 100:.2f}</p>
            <p><strong>Channel:</strong> {transaction['channel']}</p>
            <p>You may now return to the app.</p>
        </body>
    </html>
    """
    
#Webhook endpoint for Paystack
@app.post("/payments/webhook")
async def paystack_webhook(request: Request):

    payload = await request.body()

    signature = request.headers.get("x-paystack-signature")

    expected_signature = hmac.new(
        PAYSTACK_SECRET_KEY.encode(),
        payload,
        hashlib.sha512
    ).hexdigest()

    if signature != expected_signature:
        raise HTTPException(
            status_code=401,
            detail="Invalid signature"
        )

    event = await request.json()

    print("WEBHOOK EVENT:", event.get("event"))

    if event.get("event") != "charge.success":
        return {"message": "Event ignored"}

    data = event["data"]

    reference = data["reference"]

    booking = await database.fetch_one(
        bookings.select().where(
            bookings.c.payment_reference == reference
        )
    )

    if not booking:
        return {"message": "Booking not found"}

    if booking["payment_status"] == "paid":
        return {"message": "Already processed"}

    await database.execute(
        bookings.update()
        .where(
            bookings.c.payment_reference == reference
        )
        .values(
            payment_status="paid",
            status="confirmed",
            payment_channel=data["channel"],
            payment_date=datetime.utcnow()
        )
    )

    print(f"Booking {booking['id']} marked as paid")

    return {"message": "Webhook processed"}
        

# ======================
# BOOKINGS
# ======================

@app.get("/booked_slots")
async def get_booked_slots(date: str):

    query = bookings.select()

    rows = await database.fetch_all(query)

    booked_slots = []

    for row in rows:
        booking_time = datetime.fromisoformat(
            row["booking_time"]
        )

        if booking_time.date().isoformat() == date:
            booked_slots.append(
                booking_time.isoformat()
            )

    return booked_slots


@app.post("/book")
async def create_booking(booking: BookingCreate):
    print(
    f"Booking received for "
    f"{booking.customer_name}"
)
    try:
         # Check if the selected time has already been booked
        existing_booking = await database.fetch_one(
            bookings.select().where(
                bookings.c.booking_time == booking.booking_time
            )
        )

        if existing_booking:
            raise HTTPException(
                status_code=409,
                detail="This time slot has already been booked."
            )
            
        if booking.email and "@" not in booking.email:
            raise HTTPException(
        status_code=400,
        detail="Invalid email address",
    )
        
        # ✅ Get service from DB
        service_query = services.select().where(
            services.c.id == booking.service_id
        )
        service = await database.fetch_one(service_query)

        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        # ✅ Determine car type
        car_type = CAR_TYPE.get(booking.car_model, "Sedan")

        # ✅ Apply pricing logic
        price = service["price"]
        if car_type == "SUV":
            price += 1000

        query = bookings.insert().values(
            name=booking.customer_name,
            email=booking.email,
            phone_number=booking.phone_number,
            service=service["name"],
            amount=price,
            booking_time=booking.booking_time,
            car_brand=booking.car_brand,
            car_model=booking.car_model,
            status="service_pending",
            payment_status="unpaid",
            created_at=datetime.utcnow()
        )

        booking_id = await database.execute(query)

        return {
            "message": "Booking created successfully",
            "booking_id": booking_id,
        }


    except HTTPException:
        raise

    except Exception as e:
        print(f"BOOKING ERROR: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


# ======================
# ADMIN PANEL (UPDATED)
# ======================

@app.get("/admin/bookings")
async def get_all_bookings(
    token: str,
    brand: str | None = None,
    car_type: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
):
    if token != "secure_admin_token":
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    print(
        f"brand={brand}, "
        f"car_type={car_type}, "
        f"start_date={start_date}, "
        f"end_date={end_date}"
    )

    query = bookings.select()
    data = await database.fetch_all(query)

    filtered = []

    start = start_date
    end = end_date
    
    for b in data:
        model_type = CAR_TYPE.get(b["car_model"], "Sedan")

        if brand and b["car_brand"] != brand:
            continue

        if car_type and model_type != car_type:
            continue

        created_at = b["created_at"]

        if isinstance(created_at, str):
            booking_date = datetime.fromisoformat(
                created_at.replace("Z", "")
            ).date()
        else:
            booking_date = created_at.date()

        if start and booking_date < start:
            continue

        if end and booking_date > end:
            continue

        item = dict(b)
        item["car_type"] = model_type

        filtered.append(item)

    total = len(filtered)

    today = datetime.utcnow().date()

    today_count = sum(
        1
        for b in filtered
        if (
            datetime.fromisoformat(
                str(b["created_at"]).replace("Z", "")
            ).date()
            if isinstance(b["created_at"], str)
            else b["created_at"].date()
        ) == today
    )

    revenue = sum(b["amount"] for b in filtered)

    return {
        "bookings": filtered,
        "total_bookings": total,
        "today_bookings": today_count,
        "total_revenue": revenue,
    }


@app.put("/admin/mark_paid/{booking_id}")
async def mark_paid(booking_id: int, token: str):
    if token != "secure_admin_token":
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    query = bookings.update().where(
        bookings.c.id == booking_id
    ).values(
        payment_status="paid"
    )

    await database.execute(query)

    return {"message": "Payment updated"}

@app.put("/admin/update_status/{booking_id}")
async def update_status(booking_id: int, token: str):
    if token != "secure_admin_token":
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    query = bookings.update().where(
        bookings.c.id == booking_id
    ).values(status="completed")

    await database.execute(query)

    return {"message": "Updated"}

@app.get("/admin/export")
async def export_bookings(token: str):
    if token != "secure_admin_token":
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    filename = "bookings_export.csv"
    rows = await database.fetch_all(bookings.select())

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "Customer",
            "Phone",
            "Service",
            "Amount",
            "Brand",
            "Model",
            "Booking Time",
            "Status",
            "Created At",
        ])

        for row in rows:
            writer.writerow([
                row["name"],
                row["phone_number"],
                row["service"],
                row["amount"],
                row["car_brand"],
                row["car_model"],
                row["booking_time"],
                row["status"],
                row["created_at"],
            ])

    return FileResponse(
        filename,
        media_type="text/csv",
        filename=filename,
    )
    