# Cultural Inclusion Storytelling Map

## Project Summary

This project is an interactive storytelling platform where minority communities can upload narratives linked to geographic locations.

The current MVP is focused on:

- Cyprus first
- Greece second
- Europe later

The platform goal is to improve cultural visibility and respectful engagement, with long-term alignment to SDG 10 and SDG 11.

## Current Stack

- Backend: FastAPI
- Database: SQLite
- ORM: SQLAlchemy
- Frontend: React + React Router + React Leaflet

## What Is Working Right Now

### Backend

- FastAPI app startup is wired in `backend/app/main.py`
- SQLite connection and session management are set up in `backend/app/db/session.py`
- Story model exists in `backend/app/models/story_model.py`
- Story schemas exist in `backend/app/schemas/story_schema.py`
- Story routes exist in `backend/app/routes/stories.py`
- Current story endpoints:
  - `POST /stories`
  - `GET /stories`
  - `GET /stories/{story_id}`
  - `PATCH /stories/{story_id}/status`
- Story status values are controlled:
  - `pending`
  - `approved`
  - `rejected`
- Story validation currently checks:
  - title must not be empty
  - content must not be empty
  - latitude must be between `-90` and `90`
  - longitude must be between `-180` and `180`

### Frontend

- API service is active in `frontend/src/services/Api.js`
- Main routes are active in `frontend/src/App.js`
- Home page uses `MapView`
- Dedicated map page uses `MapPage`
- Upload page submits stories to the backend
- Map rendering now uses the backend story shape correctly:
  - `latitude`
  - `longitude`
  - `content`
  - `media_url`

## Important Local Demo Note

For local UI-only testing, new stories are currently auto-approved in:

- `backend/app/routes/stories.py`

This is controlled by:

```python
AUTO_APPROVE_NEW_STORIES = True
```

That setting was added so the team can:

- upload from the UI
- refresh the map
- immediately see the new story marker

Before production or a real moderation workflow, this should be turned back off.

## What We Finished In This Pass

- fixed frontend/backend story field mismatch
- fixed API import casing to match `Api.js`
- fixed frontend upload flow to send the backend JSON payload
- fixed local frontend start/build reliability in this Windows repo path
- added a moderation status update route on the backend
- added local auto-approve mode so UI-only demo testing works
- added clearer comments to the active backend and frontend story flow files
- cleaned the repo for team work by ignoring local/generated files

## Active Story Data Shape

The frontend should expect stories in this shape:

```json
{
  "id": 1,
  "title": "Story title",
  "content": "Story content",
  "media_url": null,
  "latitude": 35.1856,
  "longitude": 33.3823,
  "status": "approved",
  "created_at": "2026-04-19T14:00:00"
}
```

## Local Run Instructions

### Backend

```powershell
cd "C:\Users\nadio\Documents\02_Projects_&_Code\cultural-storytelling-map\backend"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Backend URLs:

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

### Frontend

```powershell
cd "C:\Users\nadio\Documents\02_Projects_&_Code\cultural-storytelling-map\frontend"
npm start
```

Frontend URL:

- `http://localhost:3000`
- If CRA moves to another port, also try `http://localhost:3001`

## Quick Manual Test Flow

### UI-only flow

1. Start backend
2. Start frontend
3. Open the frontend
4. Go to Upload Story
5. Enter a title
6. Enter a narrative
7. Click a map location
8. Submit
9. Refresh the homepage or `/map`
10. Confirm the new marker appears

### Backend + UI flow

1. Start backend
2. Open Swagger
3. Create a story with `POST /stories`
4. If auto-approve is turned off later, approve it with `PATCH /stories/{story_id}/status`
5. Open the frontend map and confirm the marker appears

## Team Handoff

### Backend Dev 1 Checklist

- [x] Set up SQLite + SQLAlchemy session layer
- [x] Create Story model
- [x] Create Story schemas
- [x] Create Story routes
- [x] Add status update endpoint
- [x] Add validation for title/content/coordinates
- [x] Keep story list approved by default
- [ ] Add a nullable submitter field or user relationship that does not block anonymous posting
- [ ] Add real media storage strategy for image/audio/video
- [ ] Turn local auto-approve back off when moderation flow is ready
- [ ] Add backend tests for story create/list/get/status update
- [ ] Add safer config management for local vs production behavior

### Developer 2 Checklist

- [x] Connect map pages to backend story fetch
- [x] Align map marker rendering with backend story fields
- [x] Align upload page with backend story payload
- [ ] Create a real story detail page instead of the current placeholder button
- [ ] Add loading and empty states for map/story fetching
- [ ] Add error handling UI for failed uploads and failed map fetches
- [ ] Re-enable media upload UI after backend media support exists
- [ ] Clean up duplicate map rendering logic between `MapView.js` and `MapPage.js` only when safe

### Developer 3 Checklist

- [ ] Decide final content categories and how they map to stories
- [ ] Define moderation rules for approved vs rejected stories
- [ ] Create QA checklist for upload, moderation, and map display
- [ ] Prepare seed/demo stories for presentation
- [ ] Review wording, branding, and cultural-sensitivity copy across the UI
- [ ] Help define anonymous posting and future version-history requirements

## Current Limitations

- media upload is still placeholder-only on the frontend
- no authentication yet
- no moderation dashboard yet
- no comments/reactions yet
- no story detail page yet
- duplicate map logic still exists in `MapView.js` and `MapPage.js`
- local auto-approve is enabled for easier demo testing

## End-of-Day Status

The repo is in a working local MVP state:

- backend starts
- frontend starts
- upload works from the UI
- map fetch works
- markers render from backend story data
- local UI-only demo flow works

This is a good stopping point for today and safe to continue from tomorrow.
