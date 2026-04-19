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
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

- API: `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`

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
- `media_url`
- `latitude`
- `longitude`
- `status`

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
- [ ] Add submitter support without blocking anonymous posting
- [ ] Plan real media storage

### Developer 2

- [x] Frontend/backend story contract aligned
- [x] Map pages connected to backend
- [x] Upload flow connected to backend
- [ ] Story detail page
- [ ] Loading and error states
- [ ] Re-enable media upload after backend support exists

### Developer 3

- [ ] Define moderation rules
- [ ] Finalize content categories
- [ ] Prepare demo stories
- [ ] Review wording and cultural-sensitivity copy
- [ ] Help define anonymous posting and version history

## Current Limitations

- Media upload is not implemented yet
- No authentication yet
- No moderation dashboard yet
- No comments/reactions yet
- No story detail page yet
