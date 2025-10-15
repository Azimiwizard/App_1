from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, Dish  # Import db and Dish from models
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Create app instance for this script
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey')
database_url = os.environ.get('DATABASE_URL')
if database_url is None:
    if os.environ.get('PORT'):  # Production environment
        raise RuntimeError(
            "DATABASE_URL environment variable is required for production deployment. Add a PostgreSQL database service in your Railway dashboard.")
    database_url = 'sqlite:///stitch_menu.db'
else:
    database_url = database_url.replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with this app
db.init_app(app)


def seed_database():
    if Dish.query.first():
        print('Dishes already exist. Skipping seeding.')
        return
    dishes = [
        # Breakfast
        Dish(section="Breakfast", name="Classic Breakfast", price=9.99, description="Eggs, toast, and more.",
             image_filename="https://lh3.googleusercontent.com/aida-public/AB6AXuAJh0DPRJwiTIFhPK5fnjUB6w-8C4bztgynoRU20C57Uci8r0D4t0lnIUOz3VeuIsPM90nH9yLw6Y3BewarsxbAKy-zvtrv58kft0RESCu0a_RHCBErw2VSXR48gNE9xp4owZx7fRA1cdX0596gg6bWIiXp1Gc5E40SIOevNTDhzZCvZSdNQ_qMMjlFPy2jeSkAND8Z63oNgtSxCzCJTI8i7t_MRtLeSh4qcUB_YxZ4oe7HGP7TQQmbPiDKhV34dRtzoR9VGnnyFFQ"),
        Dish(section="Breakfast", name="Pancake Stack", price=7.99, description="Fluffy pancakes with syrup.",
             image_filename="https://lh3.googleusercontent.com/aida-public/AB6AXuDmVMyYU2OgWFMbZRd0t2E8r17ANCeb69w8qQDpkWSvCWa7-F8loC0spRcYGLAwK-w2W4UIXmrrHTKHct0gUS6MpetJo22kx-UPzNfdyWE_Q9JNnVG6d3RkmDFevE0k5jJVkocgBOHDpNpSxxJHAQwU3Fay1Mt2mqIIq1sZgbTG6FlC4S0YKzKARJUOH8ve4lko5TiK2cLa8KF-US6wcdh5HGW4uivOteX44TzzKE19x3s0W429ssdKNu1WWATfOoADynIOuchl3pQ"),
        Dish(section="Breakfast", name="Avocado Toast", price=8.50, description="Sourdough with smashed avocado.",
             image_filename="https://lh3.googleusercontent.com/aida-public/AB6AXuAFY5KTEJ7DutOOVYusMnP8LscjlKBf5YPiUitX5Kv-BCb2EWePUPudkfR4pKMJ_f94SiEBNQPH70FpqVFSW5HFTxlMmjgiWaZL5p8ot7c6Any9erxYm0dTCl-au8DEAuz_IkLdg3TdyhNZaCRaHaMEgRnS7tes5695jeRLNEYahJoRSs1jH3EYwMLIv7DdaM-zuzmEqjoLKw_L32H0iJqPHsk5t_Tm__Oi8tmGOsdNn1nOctw4TkxI3WPCVU9vNiRV0XWLL2z8vD0"),
        Dish(section="Breakfast", name="Oatmeal Bowl", price=6.50, description="Healthy oatmeal with fruit.",
             image_filename="https://lh3.googleusercontent.com/aida-public/AB6AXuD89grVa6a6LRLaCfOmZ1eU-TVfHvz7Z12fHkRfHVEE8pydj5NId8IuJXmgyeAdu4DRXeB67NHEFOfhTgQjKonwT6Y6BW-7ZB8WhAN8lgf9HslkpBxBq2SGubTnr1QIkxrrzLLU8dsmmSKrW8gdP8qVzGl9nKOZmQ98IAO7efTJImsIAQqAHcsZLqukeoQOsDhCMy05JWJ4mrJEB_1Jw3GMpnC4b46096UqahzcfUaeZndROeJATEWmjkxBqFO3W66DDVhRXJ9_YMs"),
        # Lunch
        Dish(section="Lunch", name="Chicken Sandwich", price=12.50, description="Grilled chicken sandwich.",
             image_filename="https://lh3.googleusercontent.com/aida-public/AB6AXuA6SPn3c9jwo37E8XnFbDdfBemrnT162S6x6JwEFZBJXoNKLDXA-16blw3vFUSdqsTi5JTYBvFZQ7aK7UgQ913lkE1nIqLaRYEplev_z_AKaHuIzPKRZBAqBzez9ejbJJdbJpJD9fytQd1YOU1Wd2QB07aQsL7Ssl1UjyJG_saq2V6YrCmEOJdyGj7muiupF90x9u0pclksrsp39D2ekorxpFr5aryTlzCorBDYqkiMP9rmdyzUQIRh1vnIivwIz6CbqhTCq5mh1CA"),
        Dish(section="Lunch", name="Burger Deluxe", price=14.75, description="Juicy beef burger.",
             image_filename="https://lh3.googleusercontent.com/aida-public/AB6AXuAnm1viCEuwGWCRwRUn-njhoILHC4NTVwb12MeCPJR77bO5l9p7kBeCPrgWa0ooE2H8IUHzIpqxKzBisgSQoKE6Djh71nBV_74lUtsNLxoeJNplscfpJgXpMXzgWXqc2oQdI21LWq7TNO1ICYQ5jaV3PFYz3dM3KAupplbbUgyiyjG44epHMFR-3u7LCWjmpCImeYNzs5v49RgkPAabO9SIOGXZ1ljAcSnBAN6cEpRLL5p9hdiRYMzdisfPLaVoOJmNrUZWAQMUjps"),
        Dish(section="Lunch", name="Caesar Salad", price=10.00, description="Classic Caesar salad.",
             image_filename="https://lh3.googleusercontent.com/aida-public/AB6AXuCsVW-fvmvEf3CVC8u3mgMRBj8pQRfMyiHH-7eyBVdqN-xwuH83hR-5v1OSJmGO4WzQYr56lHiDew5djsu7gOIjOmZd1kX765aEfrFQZhi6Bjoo0MzUUBMl5PQ_1RpSNVDDuVFB13aMFhcr52Npz1RVkZHNcX_1Ky72LmcQlCGlScf09Fv_OYNd7aNE5f1g9a13RseJBV2v-GqVR87IKfUdMWV8MD-m8W_rEJg4jSYfcVi2K_HpVDk06I0w3ztO3RaNLqBmElGa9L4"),
        Dish(section="Lunch", name="Veggie Wrap", price=11.50, description="Fresh veggie wrap.",
             image_filename="https://lh3.googleusercontent.com/aida-public/AB6AXuANnMQXTQmXdzKhu4NGBm-uRDGFo0P8h3lVViCw49kIJLKIICbDDl8djOgsR-O3jOLTXbTMCi-e2LjaQaZqSPTGCH-L6740aO3vCe-mHfhArHvrWKaBOzKBSZNoIFB74Dh96ZHkeSiiWfO4vgTFbZ3GepYM2I2_LjhCdqFYDkx1PZN7OAnDP9r3mt-7FqPphv9qOz9y-ZJbBmfPC5CdOg3ohYHzxP2uW00sj2tmMV7szJtVt7Qx9sNUFABh2KX3_gRRRlRK4F4ucY"),
        # Dinner
        Dish(section="Dinner", name="Spaghetti & Meatballs", price=16.99, description="Classic spaghetti with meatballs.",
             image_filename="https://lh3.googleusercontent.com/aida-public/AB6AXuAF-Vu9hmDT5IwjoF4OeVw1x01X91EJsQeenM98KLaB4BM7UxR7HqZeO0sLRXrkXzrcurV-ZHVcH05asOGFgGnV9VvIR_TxkgSuq1YoHPFm_fcnvX7DW8eos-Yd0TEIs6cQywpWw-2Jb9esgDX6SLJDPuXmbd2jbcLMlbi3yrdT3Ke4LgmUnt3zZ6fr3y6MENG_QwF1glSgOGm6GbDFMsOTQ05FWJZLIVPoxvVjVM1AbC6C0xNzLqdgqNYl5w0pMh2J0N01t8l3P74"),
        Dish(section="Dinner", name="Grilled Salmon", price=18.50, description="Grilled salmon fillet.",
             image_filename="https://lh3.googleusercontent.com/aida-public/AB6AXuBG41f0rfJLO_eD__LFGCJoIbmo2imGJQVRCVv3SlPN-d_27AE0UmIok7myoVq5201LHPJtz1hEb3EoeVRztn1x3fa30irrT2zaX9GYcnHhf3F-Qq97T45OqIwdO5cP-wfup6CVQL3XqkCm1LpI9hf9GFBlBePHXrc1qwMiF4GZZCN3qiVvayGBj3qEDd40YGQyduHIa74KNgexHaiOsVP9jTIJ49KbmR71gBmgkKRajUGWIjU5cb1k6P2oUpkJVtI9p6pprqI9gfQ"),
        Dish(section="Dinner", name="Ribeye Steak", price=25.00, description="Juicy ribeye steak.",
             image_filename="https://lh3.googleusercontent.com/aida-public/AB6AXuCPSJpmjlLSTRPx6kGAnc21csfda0P8h3lVViCw49kIJLKIICbDDl8djOgsR-O3jOLTXbTMCi-e2LjaQaZqSPTGCH-L6740aO3vCe-mHfhArHvrWKaBOzKBSZNoIFB74Dh96ZHkeSiiWfO4vgTFbZ3GepYM2I2_LjhCdqFYDkx1PZN7OAnDP9r3mt-7FqPphv9qOz9y-ZJbBmfPC5CdOg3ohYHzxP2uW00sj2tmMV7szJtVt7Qx9sNUFABh2KX3_gRRRlRK4F4ucY"),
        Dish(section="Dinner", name="Chicken Parmesan", price=17.50, description="Breaded chicken with cheese.",
             image_filename="https://lh3.googleusercontent.com/aida-public/AB6AXuD8HzoAlTwS2y9F2UwlCc7rDv8E4dzrBQmgpsusR_GOZdcdSodgSajyjU0u6TldoblpaFyJ_FRSn4sIDQWoKnVzsOo3XBYVAAQ5TKDvnTw5cH1tI-x-6JGyTei4g7VsJRb7WhzlsDshO-JECl23cYf2lA3268i_gn0VJocLjl4ddu1xoydT3Ke4LgmUnt3zZ6fr3y6MENG_QwF1glSgOGm6GbDFMsOTQ05FWJZLIVhabz9x8FQz4D2VefNJXRN0g6FIpn_o8JTgKvJo")
    ]
    db.session.bulk_save_objects(dishes)
    db.session.commit()
    print('Seeded dishes!')


def init_db():
    with app.app_context():
        db.create_all()
        seed_database()
        print("Database tables created and seeded successfully.")


if __name__ == "__main__":
    init_db()
