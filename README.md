# Cultural Inclusion Storytelling Map

A map-based platform for collecting and sharing the cultural stories of
**minority communities**, pinned to the real locations they belong to.

Mission focus:
- **Cyprus** first
- **Greece** next
- **Europe** later

---

## Current Status

- Full stack running locally (FastAPI backend + React frontend)
- User registration and login with JWT authentication
- Story submission requires login and goes through admin moderation
- Admin moderation dashboard (approve / reject stories)
- Anonymous posting (author hidden from the public, retained for moderators)
- Comments, likes, and tags supported at the API level
- Map displays approved stories with category-based marker colors
- Demo stories and an admin-promotion script for quick setup

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python) |
| Database | SQLite + SQLAlchemy |
| Auth | JWT (python-jose) + bcrypt password hashing |
| Frontend | React + React Router |
| Map | React-Leaflet (OpenStreetMap tiles) |

---

## Backend Setup (First Time)

The database file (`storymap.db`) is **not** committed to git — each developer
runs their own local copy. The tables are created automatically from the models
on first run, so setting up a fresh database takes a few steps:

### 1. Install dependencies

```bash
cd backend
python -m venv .venv                          # create a virtual environment (first time only)
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Create your environment file

Copy the example file and set a secret key:

```bash
copy .env.example .env
```

Then open `.env` and replace the placeholder with a real key. Generate one with:

```bash
.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

The app will refuse to start if `SECRET_KEY` is missing.

### 3. Run the server

```bash
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

On first run this creates `storymap.db` with all tables (users, stories,
comments, likes, tags).

- API: `http://127.0.0.1:8000`
- Interactive docs: `http://127.0.0.1:8000/docs`

### 4. (Optional) Add demo data

With the server set up, you can seed demo content and create an admin:

```bash
.venv\Scripts\python.exe seed_stories.py              # 6 demo Cyprus stories
.venv\Scripts\python.exe make_admin.py your@email.com # promote a user to admin
```

> **Note:** `make_admin.py` only works after you've registered that email
> through the app first.

---

## Frontend Setup

```bash
cd frontend
npm install        # first time only
npm start
```

- App: `http://localhost:3000`

---

## Database

SQLite + SQLAlchemy. The schema is defined by the models and created
automatically on first run. The `storymap.db` file is local only and gitignored.

| Table | Description |
|-------|-------------|
| `users` | Registered users with bcrypt-hashed passwords and an admin flag |
| `stories` | Submitted stories with coordinates, category, moderation status, and anonymity flag |
| `comments` | User comments on approved stories |
| `likes` | One like per user per story (toggle) |
| `tags` | Admin-managed tags (e.g. festival, music) |
| `story_tags` | Many-to-many join between stories and tags |

---

## Authentication

- Register: `POST /register`
- Login: `POST /login` — returns a JWT token
- The frontend stores the token and sends it as `Authorization: Bearer <token>`
- Admin-only routes return `403` if the user is not an admin

### Promoting a user to admin

```bash
cd backend
.venv\Scripts\python.exe make_admin.py your@email.com           # grant admin
.venv\Scripts\python.exe make_admin.py your@email.com --remove  # revoke admin
```

---

## API Overview

### Stories
| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/stories` | Public (supports `?status=`, `?category=`) |
| GET | `/stories/{id}` | Public |
| POST | `/stories` | Login required |
| PATCH | `/stories/{id}/status` | Admin only |

### Comments
| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/stories/{id}/comments` | Public |
| POST | `/stories/{id}/comments` | Login required |
| DELETE | `/comments/{id}` | Author or admin |

### Likes
| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/stories/{id}/likes` | Public |
| POST | `/stories/{id}/like` | Login required (toggles) |

### Tags
| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/tags` | Public |
| POST | `/tags` | Admin only |
| GET | `/stories/{id}/tags` | Public |
| POST | `/stories/{id}/tags` | Admin only |
| DELETE | `/stories/{id}/tags/{tag_id}` | Admin only |
| GET | `/tags/{id}/stories` | Public |

---

## Story Fields

- `title`
- `content`
- `media_url` (optional)
- `latitude` / `longitude`
- `category` — `heritage`, `landmarks`, `oral`, `customs`
- `status` — `pending`, `approved`, `rejected`
- `user_id` — the submitting user (hidden from public API when anonymous)
- `is_anonymous` — hides the author from the public
- `created_at`

Map marker colors by category: heritage = blue, landmarks = red,
oral = green, customs = yellow.

---

## Team Checklist

### Backend / Database
- [x] Database setup (SQLite + SQLAlchemy)
- [x] Story model, schema, and routes
- [x] User registration and login
- [x] Password hashing (bcrypt)
- [x] JWT authentication + secret key in `.env`
- [x] Admin moderation route
- [x] Anonymous posting
- [x] Comments, likes, tags
- [x] Demo data + admin scripts
- [x] `requirements.txt`
- [ ] Backend tests
- [ ] Media file storage
- [ ] Database migrations (Alembic) — when schema changes must preserve data

### Frontend
- [x] Map page connected to backend
- [x] Upload form connected to backend (login required + anonymous option)
- [x] Login and registration pages
- [x] Admin moderation dashboard
- [ ] Comments UI on story popups
- [ ] Like button on story popups
- [ ] Category legend / labels on the map
- [ ] Story detail page
- [ ] Loading and error states across all pages
- [ ] Re-enable media upload after backend storage exists

### Content & Design
- [ ] Define moderation rules
- [ ] Prepare more demo stories
- [ ] Review cultural-sensitivity copy
- [ ] Define minority community classification (future feature)

---

## Current Limitations

- Media upload is not implemented yet (UI placeholders exist)
- No story detail page yet
- Comments, likes, and tags exist in the backend but are not wired to the frontend UI yet
- No backend tests yet
- Stories are classified only by general category, not yet by minority community
