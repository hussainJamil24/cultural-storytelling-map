# Cultural Inclusion Storytelling Map

Map-based platform for cultural stories linked to real locations.

Current MVP focus:
- Cyprus
- Greece next
- Europe later

## Current Status

- Backend and frontend run locally
- Story upload works from the UI
- Uploaded stories appear on the map in local demo mode
- Story statuses exist: `pending`, `approved`, `rejected`

## Important Local Note

For local UI testing, new stories are auto-approved in:

- [backend/app/routes/stories.py](backend/app/routes/stories.py)

```python
AUTO_APPROVE_NEW_STORIES = True
```

Turn this off when the real moderation flow is ready.

## Run Locally

### Backend

```powershell
cd "C:\Users\nadio\Documents\02_Projects_&_Code\cultural-storytelling-map\backend"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

- API: `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`

### Database migrations (Alembic)

The database schema is managed by Alembic, not by the app at startup.

```powershell
# apply all migrations (run once after pulling new changes)
.\.venv\Scripts\python.exe -m alembic upgrade head

# after changing a model, generate a new migration
.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "describe change"

# inspect current / available revisions
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic history
```

Always review the generated file under `backend/alembic/versions/` before committing it.

### Frontend

```powershell
cd "C:\Users\nadio\Documents\02_Projects_&_Code\cultural-storytelling-map\frontend"
npm start
```

- App: `http://localhost:3000`
- If busy: `http://localhost:3001`

## Current Story Fields

The frontend and backend currently use:

- `title`
- `content`
- `category`
- `latitude`
- `longitude`
- `status`

Media (images/audio) now lives in a separate `media` table, returned on each
story as a `media` list. The old single `media_url` column has been removed.

Stories also track a submitter via `user_id` (nullable, for logged-out posts)
and an `is_anonymous` flag. Responses expose `author_name` (null when the story
is anonymous) but never the raw `user_id`.

Categories live in a managed `categories` table (slug, label, icon, description,
sort order) seeded with `heritage`, `landmarks`, `oral`, and `customs`. Stories
still reference a category by its slug. The list is served at `GET /categories`,
and new stories are validated against it on submission.

Comments live in a `comments` table linked to a story and its author. They are
always attributed to a logged-in user and shown immediately (no moderation).
Endpoints: `GET /stories/{id}/comments` and `POST /stories/{id}/comments`.

## What Is Done

- Story backend wired with FastAPI + SQLite + SQLAlchemy
- Story upload connected from frontend to backend
- Map pages read backend story data correctly
- API import casing fixed to match `Api.js`
- Local demo flow works end to end

## Team Checklist

### Backend Dev 1

- [x] Database/session setup
- [x] Story model, schema, and routes
- [x] Status update route
- [ ] Backend tests
- [ ] Replace local auto-approve with proper config
- [x] Add submitter support without blocking anonymous posting
- [ ] Plan real media storage

### Developer 2

- [x] Frontend/backend story contract aligned
- [x] Map pages connected to backend
- [x] Upload flow connected to backend
- [ ] Story detail page
- [ ] Loading and error states
- [ ] Re-enable media upload after backend support exists

### Developer 3
- [x] User authentication (register/login)
- [x] Comments model, schema and routes
- [x] Likes & Tags model, schema and routes
- [ ] Define moderation rules
- [ ] Finalize content categories
- [ ] Prepare demo stories
- [ ] Review wording and cultural-sensitivity copy
- [ ] Help define anonymous posting and version history

## Current Limitations

- Media upload is not implemented yet
- No authentication yet
- No moderation dashboard yet
- Comments backend exists (GET/POST `/stories/{id}/comments`); not wired in the UI yet
- No likes/reactions yet
- No story detail page yet
