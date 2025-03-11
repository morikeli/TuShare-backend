import asyncio
import random
import uuid
from datetime import datetime, timedelta, timezone
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from utils import get_password_hash
from .database import AsyncSessionLocal, init_db
from models import Message, User, Ride, Booking


fake = Faker()

async def seed_users(db: AsyncSession):
    """Create fake users."""
    users = []

    for index, _ in enumerate(range(100)):
        gender = random.choice(['Male', 'Female'])

        if gender == "Male":
            first_name = fake.first_name_male().lower()     # generate first name for male users
        else:
            first_name = fake.first_name_female().lower()
        
        last_name = fake.last_name().lower()
        # first_name = fake.first_name().lower()
        # last_name = fake.last_name().lower()
        
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
            gender=gender,
            email=fake.email(),
            mobile_number=fake.phone_number(),
            password=hashed_password,
            role=random.choice(["driver", "passenger"]),
            bio=random.choice([fake.sentence(), fake.paragraph(nb_sentences=5)]),   # some users will have a short bio while for other its a paragraph
            home_address=fake.address(),  # Fake home address
            work_address=random.choice([fake.address(), None]),  # Some users may not have work addresses
            twitter_handle=twitter_username,
            facebook_handle=username,
            instagram_handle=f'thee.{username}',
        )
        users.append(user)
        print(f'Generating info for user {index}')

    db.add_all(users)
    await db.commit()
    print('🧑‍🦱👩‍🦱 User accounts created successfully! ')
    return users


async def seed_rides(db: AsyncSession, users):
    """Create fake ride records."""
    destinations_list = [
        # Nairobi  
        "National Library, Upperhill, Nairobi",
        "Kenyatta Market, Ngumo, Nairobi",
        "The Hub, Karen, Nairobi",
        "Prestige Plaza, Ngong Road, Nairobi",
        "Yaya Centre, Kilimani, Nairobi",
        "Two Rivers Mall, Runda, Nairobi",
        "Village Market, Gigiri, Nairobi",
        "Garden City Mall, Thika Road, Nairobi",
        "Uhuru Park, CBD, Nairobi",
        "Karura Forest, Muthaiga, Nairobi",
        "Galleria Mall, Lang’ata, Nairobi",
        "Sarit Centre, Westlands, Nairobi",
        "The Junction, Ngong Road, Nairobi",
        "City Market, CBD, Nairobi",
        "JKIA, Embakasi, Nairobi",

        # Nakuru  
        "Lake Nakuru Lodge, Nakuru Town, Nakuru",
        "Westside Mall, Milimani, Nakuru",
        "Menengai Crater, Bahati, Nakuru",
        "Rift Valley Sports Club, CBD, Nakuru",
        "Afraha Stadium, Kiamunyi, Nakuru",
        "Kabarak University, Kabarak, Nakuru",
        "Hyrax Hill Museum, Free Area, Nakuru",
        "Nakuru War Cemetery, Lanet, Nakuru",
        "Njoro Country Club, Njoro, Nakuru",
        "Flamingo Business Park, Shabaab, Nakuru",
        "Subukia Shrine, Subukia, Nakuru",
        "Pipeline Resort, Pipeline, Nakuru",
        "Free Area Market, Free Area, Nakuru",
        "Maili Sita Trading Centre, Bahati, Nakuru",
        "Londiani Junction, Londiani, Nakuru",

        # Machakos
        "Maanzoni Lodge, Athi River, Machakos",
        "Kenyatta Stadium, CBD, Machakos",
        "People’s Park, Kathiani, Machakos",
        "Tala Market, Tala, Machakos",
        "Mulleys Supermarket, Mlolongo, Machakos",
        "Machakos University, Machakos Town, Machakos",
        "Konza Technopolis, Konza, Machakos",
        "Wamunyu Handicrafts, Wamunyu, Machakos",
        "Athi River Mining, Athi River, Machakos",
        "Kangundo Shopping Centre, Kangundo, Machakos",
        "Masinga Dam, Masinga, Machakos",
        "Syokimau Railway Station, Syokimau, Machakos",
        "Joska Trading Centre, Joska, Machakos",
        "Kitengela Hot Glass, Kitengela, Machakos",
        "Mwala Market, Mwala, Machakos",

        # Mombasa  
        "Fort Jesus, Old Town, Mombasa",
        "Nyali Beach, Nyali, Mombasa",
        "Haller Park, Bamburi, Mombasa",
        "Mama Ngina Waterfront, CBD, Mombasa",
        "Likoni Ferry, Likoni, Mombasa",
        "Tudor Creek, Tudor, Mombasa",
        "Bombolulu Workshops, Bombolulu, Mombasa",
        "Mombasa Marine Park, Shanzu, Mombasa",
        "City Mall, Nyali, Mombasa",
        "Moi International Airport, Port Reitz, Mombasa",
        "Pirates Beach, Bamburi, Mombasa",
        "Kongowea Market, Kongowea, Mombasa",
        "Jomo Kenyatta Public Beach, Bamburi, Mombasa",
        "Makadara Grounds, Makadara, Mombasa",
        "Kenya Ferry Terminal, Likoni, Mombasa",

        # Kiambu
        "Two Rivers Mall, Ruaka, Kiambu",
        "Banana Hill Art Gallery, Banana, Kiambu",
        "Windsor Golf Club, Ridgeways, Kiambu",
        "Kahawa Wendani Market, Kahawa Wendani, Kiambu",
        "Thika Road Mall (TRM), Roysambu, Kiambu",
        "Kikuyu Hospital, Kikuyu, Kiambu",
        "Kenyatta University, Ruiru, Kiambu",
        "Juja City Mall, Juja, Kiambu",
        "Limuru Country Club, Limuru, Kiambu",
        "Kentmere Club, Tigoni, Kiambu",
        "Ndumberi Dairy Farmers, Ndumberi, Kiambu",
        "Zambezi Shopping Centre, Zambezi, Kiambu",
        "Kamakis Bypass, Ruiru, Kiambu",
        "Sigona Golf Club, Sigona, Kiambu",
        "Karura Forest Entrance, Kiambu Road, Kiambu",

        # Kisumu
        "Kisumu International Airport, Kisumu Town, Kisumu",
        "Dunga Beach, Dunga, Kisumu",
        "Impala Sanctuary, Milimani, Kisumu",
        "Westend Mall, CBD, Kisumu",
        "Mega City Mall, Kondele, Kisumu",
        "Kisumu Museum, CBD, Kisumu",
        "Hippo Point, Dunga, Kisumu",
        "Maseno University, Maseno, Kisumu",
        "Kibuye Market, Kibuye, Kisumu",
        "Winam Gulf, Winam, Kisumu",
        "Kibos Sugar Factory, Kibos, Kisumu",
        "Tilapia Beach, Oginga Odinga Road, Kisumu",
        "Kisumu Yacht Club, Milimani, Kisumu",
        "United Mall, Kondele, Kisumu",
        "Kanyakwar Hills, Mamboleo, Kisumu",

        # Rongo  
        "Rongo University, Rongo Town, Rongo",
        "Kamagambo Market, Kamagambo, Rongo",
        "Rongo Catholic Church, CBD, Rongo",
        "Nyarach Primary School, Nyarach, Rongo",
        "Rongo Police Station, CBD, Rongo",
        "Sony Sugar Factory, Awendo, Rongo",
        "Rongo Bus Park, Rongo Town, Rongo",
        "Kitere Hills, Kitere, Rongo",
        "Cham Gi Wadu Trading Centre, Cham Gi Wadu, Rongo",
        " Riosiri Shopping Centre, Riosiri, Rongo",

    ]

    vehicle_model = [
        # sedan & hatchbacks
        "Toyota Corolla",
        "Toyota Premio",
        "Toyota Allion",
        "Toyota Axio",
        "Toyota Belta",
        "Toyota Vitz",
        "Toyota Passo",
        "Toyota Auris",
        "Nissan Sylphy",
        "Nissan Tiida",
        "Nissan Bluebird",
        "Honda Fit",
        "Honda Civic",
        "Honda Accord",
        "Mazda Demio",
        "Mazda Axela",
        "Subaru Impreza",
        "Subaru Legacy B4",
        "Volkswagen Golf",
        "Volkswagen Passat",
        "Suzuki Alto",
        "Suzuki Swift",
        "Mitsubishi Lancer",
        "Ford Focus",
        "Peugeot 508",

        # SUVs & crossovers
        "Toyota RAV4",
        "Toyota Harrier",
        "Toyota Prado",
        "Toyota Land Cruiser V8",
        "Toyota Land Cruiser 70 Series",
        "Toyota Rush",
        "Nissan X-Trail",
        "Nissan Juke",
        "Nissan Patrol",
        "Honda CR-V",
        "Honda Vezel",
        "Mazda CX-5",
        "Mazda CX-3",
        "Subaru Forester",
        "Subaru Outback",
        "Mitsubishi Outlander",
        "Mitsubishi Pajero",
        "Volkswagen Touareg",
        "Ford Escape",
        "Ford Edge",
        "BMW X3",
        "BMW X5",
        "Mercedes-Benz GLC",
        "Mercedes-Benz GLE",
        "Hyundai Tucson",
        "Kia Sportage",

        # pickups & vans
        "Toyota Hilux",
        "Toyota TownAce",
        "Toyota HiAce",
        "Nissan Navara",
        "Nissan Hardbody",
        "Mazda BT-50",
        "Mitsubishi L200",
        "Isuzu D-Max",
        "Isuzu ELF",
        "Ford Ranger",
        "Volkswagen Amarok",
        "Suzuki Every",

    ]
    
    rides = []

    for index, _ in enumerate(range(80)):
        ride = Ride(
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
        rides.append(ride)
        print(f'Generating info for ride {index}')

    db.add_all(rides)
    await db.commit()
    print('🚗 Ride requests created and saved succesfully!')
    return rides


async def seed_bookings(db: AsyncSession, users, rides):
    """Create fake bookings."""
    bookings = []
    
    for index, _ in enumerate(range(75)):
        booking = Booking(
            id=str(uuid.uuid4().hex),
            ride_id=fake.random_element(rides).id,
            passenger_id=fake.random_element(users).id,
            seats_booked=1,
            total_price=fake.random_int(min=10, max=2000),
            status=fake.random_element(["pending", "confirmed", "completed"]),
        )
        bookings.append(booking)
        print(f'Generating info for booking {index}')


    db.add_all(bookings)
    await db.commit()
    print('Booking created and saved successfully!')


async def seed_messages(db: AsyncSession, users, rides):
    """Create fake messages between users."""
    messages = []

    for index in range(200):    # Generate 200 messages
        sender = random.choice(users)
        receiver = random.choice([user for user in users if user.id != sender.id])      # Ensure sender != receiver

        message = Message(
            id=str(uuid.uuid4().hex),
            sender_id=sender.id,
            receiver_id=receiver.id,
            ride_id=fake.random_element(rides).id,
            content=fake.sentence(),
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=random.randint(1, 1000)),
        )
        messages.append(message)
        print(f'Generating message {index}')

    db.add_all(messages)
    await db.commit()
    print('💬 Messages generated successfully!')


async def main():
    """Run all seeding functions."""
    async with AsyncSessionLocal() as db:
        await init_db()  # Ensure database tables are created
        users = await seed_users(db)
        rides = await seed_rides(db, users)
        await seed_bookings(db, users, rides)
        await seed_messages(db, users, rides)
        print("✅ Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(main())
