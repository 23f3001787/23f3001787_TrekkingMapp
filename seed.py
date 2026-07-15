from app import app, db, Trek
from datetime import date

def seed_database():
    with app.app_context():
        db.create_all()

        indian_treks = [
            Trek(
                name='Roopkund Mystery Lake',
                location='Uttarakhand, India',
                difficulty='Hard',
                duration_days=8,
                available_slots=20,
                status='Open',
                start_date=date(2026, 9, 15) 
            ),
            Trek(
                name='Hampta Pass Adventure',
                location='Himachal Pradesh, India',
                difficulty='Moderate',
                duration_days=5,
                available_slots=25,
                status='Open',
                start_date=date(2026, 9, 22) 
            ),
            Trek(
                name='Kashmir Great Lakes',
                location='Jammu & Kashmir, India',
                difficulty='Hard',
                duration_days=7,
                available_slots=15,
                status='Open',
                start_date=date(2026, 10, 10)
            ),
            Trek(
                name='Kheerganga Weekend Trek',
                location='Himachal Pradesh, India',
                difficulty='Easy',
                duration_days=3,
                available_slots=40,
                status='Open',
                start_date=date(2026, 11, 5) 
            ),
            Trek(
                name='Sandakphu Phalut',
                location='West Bengal, India',
                difficulty='Moderate',
                duration_days=6,
                available_slots=30,
                status='Open',
                start_date=date(2026, 12, 1)
            )
        ]

        db.session.add_all(indian_treks)
        db.session.commit()
        
        print("seeded")

seed_database()
