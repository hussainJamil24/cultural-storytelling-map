"""
Seed the database with demo cultural stories for Cyprus.

Run from the backend folder:
    python seed_stories.py

Safe to re-run — it skips stories whose title already exists.
Stories are attributed to the first admin user and set to 'approved'
so they appear on the map immediately.
"""
from datetime import datetime

from app.db.session import SessionLocal
from app.models.story_model import Story, StoryStatus
from app.models.user_model import User

# (title, content, latitude, longitude, category, is_anonymous)
DEMO_STORIES = [
    (
        "The Lacemakers of Lefkara",
        "In the hill village of Lefkara, women have embroidered 'lefkaritika' lace "
        "for over 500 years. Legend says Leonardo da Vinci visited in 1481 and bought "
        "an altar cloth for Milan Cathedral. The craft, passed from mother to daughter, "
        "is now recognised by UNESCO as intangible cultural heritage.",
        34.8667, 33.3000, "heritage", False,
    ),
    (
        "Kyrenia Castle and the Shipwreck Within",
        "Guarding the old harbour of Kyrenia, this castle holds the wreck of a Greek "
        "merchant ship that sank around 300 BC — one of the oldest recovered vessels "
        "in the world. Walking its ramparts, you can still feel the layers of Byzantine, "
        "Lusignan, and Venetian hands that shaped it.",
        35.3414, 33.3192, "landmarks", False,
    ),
    (
        "Commandaria: The Wine of Kings",
        "Around the village of Omodos, families still produce Commandaria, said to be "
        "the world's oldest named wine still in production. Crusader knights drank it, "
        "and King Richard the Lionheart reportedly called it 'the wine of kings and the "
        "king of wines' at his wedding in Cyprus.",
        34.8475, 32.8147, "customs", False,
    ),
    (
        "Hala Sultan Tekke by the Salt Lake",
        "On the shore of Larnaca's salt lake stands one of Islam's most revered shrines, "
        "the resting place of Umm Haram. In winter, flamingos gather on the lake behind it, "
        "and the white mosque mirrored in the still water is one of the island's most "
        "peaceful sights.",
        34.8853, 33.6083, "landmarks", False,
    ),
    (
        "My Grandmother's Bread Oven",
        "My grandmother in Kakopetria kept a clay 'fournos' behind her house. Every Saturday "
        "the whole street smelled of village bread and halloumi pies. She would tell us that "
        "the oven had baked for three generations, and that as long as it was lit, no one in "
        "the family would ever go hungry.",
        34.9889, 32.8997, "oral", True,
    ),
    (
        "The Painted Churches of Troodos",
        "Hidden in the Troodos mountains are small barn-roofed chapels whose interiors blaze "
        "with Byzantine frescoes painted between the 11th and 15th centuries. Ten of them form "
        "a UNESCO World Heritage site. Villagers protected the paintings for centuries, "
        "whitewashing them in times of danger to keep them safe.",
        34.9229, 32.8625, "heritage", False,
    ),
]


def main():
    db = SessionLocal()
    added, skipped = 0, 0
    try:
        admin = db.query(User).filter(User.is_admin == True).first()  # noqa: E712
        author_id = admin.id if admin else None

        for title, content, lat, lng, category, anon in DEMO_STORIES:
            if db.query(Story).filter(Story.title == title).first():
                skipped += 1
                continue
            db.add(Story(
                title=title,
                content=content,
                media_url=None,
                latitude=lat,
                longitude=lng,
                category=category,
                user_id=author_id,
                is_anonymous=anon,
                status=StoryStatus.APPROVED.value,
                created_at=datetime.utcnow(),
            ))
            added += 1
        db.commit()
    finally:
        db.close()

    print(f"Seed complete — {added} added, {skipped} already existed.")


if __name__ == "__main__":
    main()
