import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from utils import get_password_hash
from .database import AsyncSessionLocal, init_db
from models import User, Ride, Booking
import random

fake = Faker()

async def seed_users(db: AsyncSession):
    """Create fake users."""
    users = []

    for index, _ in enumerate(range(100)):
        first_name = fake.first_name().lower()
        last_name = fake.last_name().lower()
        
        # Randomly choose between dot (.) or underscore (_)
        separator = random.choice([".", "_"])
        
        username = f"{first_name}{separator}{last_name}"
        twitter_username = f'{separator}{username}'
        raw_password = "defaultpassword"
        hashed_password = get_password_hash(raw_password)
        
        # create a user account
        user = User(
            id=str(uuid.uuid4().hex),
            first_name=first_name.capitalize(),
            last_name=last_name.capitalize(),
            username=username,
            gender=random.choice(["Male", "Female"]),
            email=fake.email(),
            password=hashed_password,
            role=random.choice(["driver", "passenger"])
        )
        users.append(user)

    db.add_all(users)
    await db.commit()
    return users


async def seed_rides(db: AsyncSession, users):
    """Create fake ride records."""
    destinations_list = [
        "Donholm",
        "GPO - Nairobi", 
        "Kayole",
        "Kayole junction",
        "Kisumu", 
        "Kitere - Rongo",
        "Machakos", 
        "Mombasa", 
        "Pipeline",
        "Rongo town",
        "Rongo University - Kitere",
        "Umoja 1",
        "Umoja 2",
        "Umoja 3",
        "Umoja Innercore",
        "Upperhill - National Library",
        "Upperhill - 2nd Ngong Avenue", 
        "Upperhill - Community stage",
    ]

    vehicle_model = [
        'BMW M3',
        'BMW M5',
        'Nissan AD',
        'Nissan Sylphy',
        'Porsche 911 Turbo S',
        'Subaru Legacy B4',
        'Subaru Impreza',
        'Suzuki Alto',
        'Toyota Corolla',
        'Toyota Premio',
        'Toyota Rav4',
        'Toyota Rush',
        'Volkswagen Golf',
        'Volkswagen Passat',
        'Volkswagen Polo',
    ]
    
    rides = [
        Ride(
            id=str(uuid.uuid4().hex),
            driver_id=fake.random_element(users).id,
            vehicle_type=fake.random_element(["Sedan", "SUV", "Bike"]),
            vehicle_model=fake.random_element(vehicle_model),
            vehicle_plate=fake.license_plate(),
            available_seats=fake.random_int(min=1, max=4),
            departure_location=fake.city(),
            destination=fake.random_element(destinations_list),
            departure_time=datetime.now(timezone.utc) + timedelta(days=fake.random_int(min=1, max=5)),
            price_per_seat=fake.random_int(min=2, max=8),
            is_available=True
        )
        for _ in range(70)
    ]
    db.add_all(rides)
    await db.commit()
    return rides


async def seed_bookings(db: AsyncSession, users, rides):
    """Create fake bookings."""
    bookings = [
        Booking(
            id=str(uuid.uuid4().hex),
            ride_id=fake.random_element(rides).id,
            passenger_id=fake.random_element(users).id,
            seats_booked=1,
            total_price=fake.random_int(min=10, max=2000),
            status=fake.random_element(["pending", "confirmed", "completed"]),
        )
        for _ in range(40)
    ]
    db.add_all(bookings)
    await db.commit()


async def main():
    """Run all seeding functions."""
    async with AsyncSessionLocal() as db:
        await init_db()  # Ensure database tables are created
        users = await seed_users(db)
        rides = await seed_rides(db, users)
        await seed_bookings(db, users, rides)
        print("✅ Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(main())
