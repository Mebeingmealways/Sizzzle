"""Bootstrap database data for local development, demos, and tests."""
""" includes demo db for customer, cook, manager and admin"""
from datetime import date, datetime, timedelta, timezone
import random
import secrets
import string

from app import create_app, db
from models import (
    Booking,
    BookingDish,
    Complaint,
    CookAvailability,
    CookDish,
    CookProfile,
    Dish,
    DishIngredient,
    Ingredient,
    PlatformPolicy,
    TasteProfile,
    User,
)


def generate_booking_code():
    chars = string.ascii_uppercase + string.digits
    return "BK-" + "".join(secrets.choice(chars) for _ in range(6))


def utc_now_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def seed(app=None, reset=True):
    if app is None:
        app = create_app()
    rng = random.Random(106)

    with app.app_context():
        if reset:
            db.drop_all()
        db.create_all()

        # Users
        admin = User(
            name="Admin User",
            email="admin@sizzzle.com",
            phone="+91 90000 00001",
            role="admin",
            is_email_verified=True,
            address="Mumbai",
            latitude=19.076,
            longitude=72.8777,
        )
        admin.set_password("admin123")

        manager = User(
            name="Arjun Mehta",
            email="manager@sizzzle.com",
            phone="+91 90000 00002",
            role="manager",
            is_email_verified=True,
            address="Mumbai",
            latitude=19.082,
            longitude=72.881,
        )
        manager.set_password("manager123")

        customer = User(
            name="Priya Sharma",
            email="customer@sizzzle.com",
            phone="+91 90000 00003",
            role="customer",
            is_email_verified=True,
            address="Bandra West, Mumbai",
            latitude=19.0596,
            longitude=72.8295,
        )
        customer.set_password("customer123")

        customer2 = User(
            name="Rohit Patel",
            email="rohit@sizzzle.com",
            phone="+91 90000 00010",
            role="customer",
            is_email_verified=True,
            address="Juhu, Mumbai",
            latitude=19.1075,
            longitude=72.8263,
        )
        customer2.set_password("customer123")

        cook_user = User(
            name="Chef Kavitha",
            email="cook@sizzzle.com",
            phone="+91 90000 00004",
            role="cook",
            is_email_verified=True,
            address="Andheri East, Mumbai",
            latitude=19.1136,
            longitude=72.8697,
        )
        cook_user.set_password("cook123")

        cook_user2 = User(
            name="Chef Raman",
            email="raman@sizzzle.com",
            phone="+91 90000 00005",
            role="cook",
            is_email_verified=True,
            address="Dadar, Mumbai",
            latitude=19.0178,
            longitude=72.8478,
        )
        cook_user2.set_password("cook123")

        cook_user3 = User(
            name="Meena Iyer",
            email="meena@sizzzle.com",
            phone="+91 90000 00006",
            role="cook",
            is_email_verified=True,
            address="Powai, Mumbai",
            latitude=19.1176,
            longitude=72.9060,
        )
        cook_user3.set_password("cook123")

        db.session.add_all([admin, manager, customer, customer2, cook_user, cook_user2, cook_user3])
        db.session.flush()

        # Cook profiles
        cook_profile = CookProfile(
            user_id=cook_user.id,
            specialization="South Indian",
            experience_type="Professional Chef",
            years_experience=8,
            aadhar_number="XXXX-XXXX-4321",
            fssai_license="FSSAI-2026-4488",
            rating=4.8,
            total_jobs=142,
            total_earnings=142500,
            verification_status="approved",
            travel_radius_km=10,
            bank_account="XXXX6789",
            ifsc_code="SBIN0001234",
            pan_number="ABCPK1234F",
            upi_id="kavitha@upi",
            latitude=19.1136,
            longitude=72.8697,
            location_accuracy_m=8,
            location_updated_at=utc_now_naive(),
        )
        cook_profile2 = CookProfile(
            user_id=cook_user2.id,
            specialization="North Indian",
            experience_type="Home Cook",
            years_experience=5,
            aadhar_number="XXXX-XXXX-5678",
            fssai_license="FSSAI-2026-5512",
            rating=4.5,
            total_jobs=87,
            total_earnings=89000,
            verification_status="approved",
            travel_radius_km=8,
            bank_account="XXXX1234",
            ifsc_code="HDFC0002345",
            pan_number="DEFPK5678G",
            upi_id="raman@upi",
            latitude=19.0178,
            longitude=72.8478,
            location_accuracy_m=12,
            location_updated_at=utc_now_naive(),
        )
        cook_profile3 = CookProfile(
            user_id=cook_user3.id,
            specialization="Chinese & Continental",
            experience_type="Catering Expert",
            years_experience=3,
            aadhar_number="XXXX-XXXX-9012",
            fssai_license=None,
            rating=4.2,
            total_jobs=45,
            total_earnings=52000,
            verification_status="pending",
            travel_radius_km=12,
            bank_account="XXXX5678",
            ifsc_code="ICIC0003456",
            pan_number="GHIPK9012H",
            upi_id="meena@upi",
            latitude=19.1176,
            longitude=72.9060,
            location_accuracy_m=18,
        )
        db.session.add_all([cook_profile, cook_profile2, cook_profile3])
        db.session.flush()

        # Availability for approved cooks
        for cook in [cook_profile, cook_profile2]:
            for day in range(7):
                for slot in ["Morning", "Afternoon", "Evening"]:
                    db.session.add(
                        CookAvailability(
                            cook_id=cook.id,
                            day_of_week=day,
                            slot=slot,
                            is_available=(day < 6),
                        )
                    )

        # Taste profiles
        db.session.add_all(
            [
                TasteProfile(
                    user_id=customer.id,
                    dietary_preferences=["Vegetarian"],
                    allergies=["Peanuts"],
                    spice_level=3,
                    kitchen_equipment=["Gas Stove", "Microwave", "Blender", "Pressure Cooker"],
                ),
                TasteProfile(
                    user_id=customer2.id,
                    dietary_preferences=["Non-Vegetarian", "Keto"],
                    allergies=[],
                    spice_level=4,
                    kitchen_equipment=["Gas Stove", "Oven", "Mixer", "Air Fryer"],
                ),
            ]
        )

        # Ingredients
        ingredient_rows = [
            ("Paneer", "grams", True),
            ("Butter", "grams", True),
            ("Cream", "ml", True),
            ("Tomato", "pieces", True),
            ("Onion", "pieces", True),
            ("Garlic", "cloves", True),
            ("Ginger", "inches", True),
            ("Rice", "cups", True),
            ("Basmati Rice", "cups", True),
            ("Chicken", "grams", True),
            ("Fish", "grams", True),
            ("Yogurt", "cups", True),
            ("Dosa Batter", "cups", True),
            ("Sambar Powder", "tsp", True),
            ("Oil", "tbsp", True),
            ("Salt", "tsp", True),
        ]

        ingredients = {}
        for name, unit, mandatory in ingredient_rows:
            ing = Ingredient(name=name, unit=unit, is_mandatory=mandatory)
            db.session.add(ing)
            ingredients[name] = ing
        db.session.flush()

        # Dishes
        dishes_data = [
            ("Paneer Butter Masala", "Mains", "North Indian", "veg", 30, "Rich paneer in butter tomato gravy"),
            ("Dal Makhani", "Mains", "North Indian", "veg", 40, "Slow-cooked black lentils"),
            ("Butter Naan", "Breads", "North Indian", "veg", 15, "Soft tandoori flatbread"),
            ("Jeera Rice", "Rice", "North Indian", "veg", 20, "Cumin-tempered basmati rice"),
            ("Masala Dosa", "Mains", "South Indian", "veg", 25, "Crispy dosa with masala filling"),
            ("Idli Sambar", "Starters", "South Indian", "veg", 20, "Steamed idli with sambar"),
            ("Chicken Biryani", "Rice", "Mughlai", "nonveg", 45, "Aromatic rice with chicken"),
            ("Fish Curry", "Mains", "Bengali", "nonveg", 35, "Mustard style fish curry"),
            ("Mango Lassi", "Beverages", "North Indian", "veg", 10, "Chilled yogurt mango drink"),
            ("Aloo Gobi", "Mains", "North Indian", "veg", 25, "Potato cauliflower stir fry"),
            ("Palak Paneer", "Mains", "North Indian", "veg", 30, "Paneer in spinach gravy"),
            ("Veg Fried Rice", "Rice", "Chinese", "veg", 20, "Stir-fried rice with vegetables"),
        ]

        dish_models = []
        for name, category, cuisine, veg_nonveg, prep, description in dishes_data:
            dish = Dish(
                name=name,
                category=category,
                cuisine=cuisine,
                veg_nonveg=veg_nonveg,
                prep_time_minutes=prep,
                description=description,
            )
            db.session.add(dish)
            dish_models.append(dish)
        db.session.flush()

        dish_lookup = {d.name: d for d in dish_models}

        # Minimal ingredient mapping for common dishes
        mappings = {
            "Paneer Butter Masala": ["Paneer", "Butter", "Cream", "Tomato", "Onion", "Salt"],
            "Dal Makhani": ["Butter", "Tomato", "Onion", "Garlic", "Salt"],
            "Masala Dosa": ["Dosa Batter", "Onion", "Oil", "Salt"],
            "Idli Sambar": ["Dosa Batter", "Sambar Powder", "Tomato", "Salt"],
            "Chicken Biryani": ["Chicken", "Basmati Rice", "Onion", "Yogurt", "Oil", "Salt"],
            "Fish Curry": ["Fish", "Onion", "Tomato", "Oil", "Salt"],
        }
        for dish_name, ing_names in mappings.items():
            dish = dish_lookup.get(dish_name)
            if not dish:
                continue
            for ing_name in ing_names:
                ing = ingredients.get(ing_name)
                if ing:
                    db.session.add(DishIngredient(dish_id=dish.id, ingredient_id=ing.id, quantity="As needed"))

        # Cook dish assignments
        for dish in dish_models[:8]:
            db.session.add(CookDish(cook_id=cook_profile.id, dish_id=dish.id))
        for dish in dish_models[:10]:
            db.session.add(CookDish(cook_id=cook_profile2.id, dish_id=dish.id))

        # Booking helper
        city_cycle = [
            ("Bandra West, Mumbai", 19.0596, 72.8295, customer.id),
            ("Juhu, Mumbai", 19.1075, 72.8263, customer2.id),
            ("Indiranagar, Bengaluru", 12.9784, 77.6408, customer.id),
            ("Koramangala, Bengaluru", 12.9352, 77.6245, customer2.id),
            ("Banjara Hills, Hyderabad", 17.4126, 78.4482, customer.id),
            ("Adyar, Chennai", 13.0012, 80.2565, customer2.id),
        ]
        dish_bundles = [
            ["Paneer Butter Masala", "Dal Makhani", "Butter Naan"],
            ["Masala Dosa", "Idli Sambar"],
            ["Chicken Biryani", "Jeera Rice"],
            ["Fish Curry", "Jeera Rice"],
            ["Veg Fried Rice", "Aloo Gobi"],
            ["Palak Paneer", "Mango Lassi"],
        ]

        created_bookings = []

        def add_booking(d, time_slot, people, tier, status, amount, customer_id, cook_id, address, lat, lng, dish_names):
            fee_rate = 0.12 if tier == "premium" else 0.15
            platform_fee = round(amount * fee_rate, 2)
            cook_earnings = round(amount - platform_fee - (amount * 0.05), 2)

            b = Booking(
                booking_code=generate_booking_code(),
                customer_id=customer_id,
                cook_id=cook_id,
                date=d,
                time_slot=time_slot,
                num_people=people,
                tier=tier,
                status=status,
                otp_code="".join(secrets.choice(string.digits) for _ in range(6)),
                total_amount=amount,
                platform_fee=platform_fee,
                cook_earnings=cook_earnings,
                address=address,
                latitude=lat,
                longitude=lng,
            )
            if status == "completed":
                b.service_started_at = datetime.combine(d, datetime.strptime("10:00", "%H:%M").time())
                b.service_ended_at = datetime.combine(d, datetime.strptime("12:00", "%H:%M").time())
            if status == "cancelled":
                b.cancelled_at = datetime.combine(d, datetime.strptime("09:00", "%H:%M").time())
                b.cancellation_charge = round(amount * 0.5, 2)

            db.session.add(b)
            db.session.flush()
            created_bookings.append(b)

            for name in dish_names:
                dish = dish_lookup.get(name)
                if dish:
                    db.session.add(BookingDish(booking_id=b.id, dish_id=dish.id))

        today = date.today()

        # Keep first seeded bookings deterministic for tests (IDs 1,2,3)
        add_booking(today + timedelta(days=2), "12:00", 6, "premium", "accepted", 3200, customer.id, cook_profile.id,
                    "Bandra West, Mumbai", 19.0596, 72.8295, ["Paneer Butter Masala", "Dal Makhani", "Butter Naan"])
        add_booking(today + timedelta(days=5), "19:30", 4, "standard", "pending", 1800, customer.id, cook_profile2.id,
                    "Juhu, Mumbai", 19.1075, 72.8263, ["Masala Dosa", "Idli Sambar"])
        add_booking(today - timedelta(days=3), "13:00", 8, "premium", "completed", 4500, customer.id, cook_profile.id,
                    "Bandra West, Mumbai", 19.0596, 72.8295, ["Chicken Biryani", "Jeera Rice"])

        add_booking(today - timedelta(days=1), "11:00", 3, "standard", "completed", 1200, customer2.id, cook_profile.id,
                    "Juhu, Mumbai", 19.1075, 72.8263, ["Palak Paneer", "Butter Naan"])
        add_booking(today + timedelta(days=3), "18:00", 5, "standard", "pending", 2200, customer2.id, cook_profile2.id,
                    "Juhu, Mumbai", 19.1075, 72.8263, ["Fish Curry", "Jeera Rice"])

        # Historical and upcoming bookings for richer analytics
        for i in range(55):
            if i < 45:
                booking_date = today - timedelta(days=(160 - i * 3))
                status = "cancelled" if i % 10 == 0 else "completed"
            else:
                booking_date = today + timedelta(days=i - 44)
                status = "accepted" if i % 2 == 0 else "pending"

            tier = "premium" if i % 4 == 0 else "standard"
            amount = 1400 + (i % 7) * 260 + (500 if tier == "premium" else 0)
            address, lat, lng, cust_id = city_cycle[i % len(city_cycle)]
            cook_id = cook_profile.id if i % 2 == 0 else cook_profile2.id
            dishes = dish_bundles[i % len(dish_bundles)]

            add_booking(
                booking_date,
                ["09:00", "12:30", "16:30", "19:30"][i % 4],
                2 + (i % 5),
                tier,
                status,
                amount,
                cust_id,
                cook_id,
                address,
                lat,
                lng,
                dishes,
            )

        # Complaints with different lifecycle states
        complaint_specs = [
            ("Late arrival", "Cook arrived 35 minutes late for a scheduled slot.", "Medium", "Open", None),
            ("Ingredient mismatch", "Requested no onion/garlic but meal included both.", "High", "Investigating", manager.id),
            ("Unprofessional behavior", "Customer reported rude communication during service.", "High", "Escalated", manager.id),
            ("Billing dispute", "Customer requested itemized split for add-on grocery cost.", "Low", "Resolved", manager.id),
        ]
        completed_or_cancelled = [b for b in created_bookings if b.status in ("completed", "cancelled")]
        for i, (subject, description, priority, status, manager_id) in enumerate(complaint_specs):
            src = completed_or_cancelled[i % len(completed_or_cancelled)]
            db.session.add(
                Complaint(
                    booking_id=src.id,
                    customer_id=src.customer_id,
                    cook_id=src.cook_id,
                    subject=subject,
                    description=description,
                    priority=priority,
                    status=status,
                    manager_id=manager_id,
                    resolution_notes="Closed after review" if status == "Resolved" else None,
                )
            )

        # Platform policies
        policies = [
            ("cancellation_free_window", "12", "Hours before service for free cancellation"),
            ("cancellation_half_charge", "6", "Hours threshold for 50% charge"),
            ("cancellation_late_fee", "80", "Late cancellation fee (%)"),
            ("commission_standard", "15", "Platform fee for standard tier (%)"),
            ("commission_premium", "12", "Platform fee for premium tier (%)"),
            ("gst_rate", "5", "GST rate (%)"),
            ("payout_cycle", "weekly", "Default payout cycle"),
            ("min_payout", "500", "Minimum payout amount (INR)"),
            ("min_advance_hours", "24", "Minimum advance booking hours"),
        ]
        for key, value, description in policies:
            db.session.add(PlatformPolicy(key=key, value=value, description=description))

        db.session.commit()

        print("Database bootstrap complete.")
        print("Demo accounts:")
        print("  Admin:    admin@sizzzle.com / admin123")
        print("  Manager:  manager@sizzzle.com / manager123")
        print("  Customer: customer@sizzzle.com / customer123")
        print("  Customer: rohit@sizzzle.com / customer123")
        print("  Cook:     cook@sizzzle.com / cook123")
        print("  Cook:     raman@sizzzle.com / cook123")
        print("  Cook:     meena@sizzzle.com / cook123 (pending verification)")


if __name__ == "__main__":
    seed()
