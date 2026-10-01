# AI Video Editor

A thesis prototype for lecturer-supervised editing of educational videos. It turns a lecture recording and course materials into a reviewable edit plan, then renders only after the lecturer approves it.

**Status:** Final Year Project source snapshot and academic prototype. The recorded full source verification is dated 21 June 2026. A separate Docker API health check was recorded on 25 September 2026; it did not rerun the full build or test suite.

[Quick start](#quick-start) · [Workflow](#workflow) · [Architecture](#architecture-and-runtime) · [Data and privacy](#configuration-and-data-locations) · [Project evidence](#verification-and-project-evidence)

## What the application does

- Creates projects and imports lecture videos, audio, and course materials.
- Transcribes recordings through configured hosted, local, or hybrid speech routes.
- Extracts text and page or slide assets from PDF, PPTX, and DOCX materials.
- Uses course context to propose transcript sections, visual matches, layouts, and edit decisions.
- Presents the transcript, evidence, and proposed edits for lecturer review and manual changes.
- Renders approved edits with FFmpeg and exports video, audio, captions, and supporting artifacts.
- Downloads the complete stored original transcript as TXT, timestamped TXT, JSON, or segment CSV before rendering.

The workflow is human-reviewed: processing produces a proposed edit plan; the lecturer approves it before final rendering.

## Workflow

~~~mermaid
flowchart LR
    A[Project, video, and course materials] --> B[Transcription]
    B --> C[Course material extraction and retrieval]
    C --> D[Content and fluency analysis]
    D --> E[Visual and slide planning]
    E --> F[Reviewable edit plan]
    F --> G[Lecturer review and edits]
    G --> H{Approved?}
    H -->|Yes| I[FFmpeg render and exports]
    H -->|Changes needed| F
~~~

## Architecture and runtime

| Layer | Implementation |
|---|---|
| Desktop interface | React 19, TypeScript, Tailwind CSS, and Tauri 2 |
| API | FastAPI with Pydantic request/response models, SQLAlchemy, and Alembic |
| Processing | Direct asynchronous Python orchestration across five workflow stages |
| Relational state | PostgreSQL 16 for projects, transcripts, segments, scenes, plans, assets, and settings |
| Retrieval | Qdrant for course-material and transcript vectors when retrieval is used |
| Media | Filesystem-backed uploads and outputs; FFmpeg/FFprobe native compositor is the default renderer |
| Optional integrations | Hosted provider adapters, local whisper.cpp transcription, hybrid transcription, and optional MCP tools |

Redis is provisioned by the standard Compose file, but the current architecture audit found no active Redis client in the normal application path. Revideo/Puppeteer is disabled by default. LangGraph is present as a dependency but is not connected to the active orchestrator; n8n is deprecated.

### Ports and application modes

| Port | Use |
|---|---|
| 1420 | Vite development UI |
| 8000 | Standard Docker Compose API and browser-development API |
| 5432 | Standard Compose PostgreSQL |
| 6333 / 6334 | Qdrant REST / gRPC |
| 6379 | Standard Compose Redis service |
| 18000 | Packaged Tauri backend, loopback-bound by docker-compose.desktop.yml by default |

The browser development stack and packaged Tauri stack use different Compose configurations. Their databases and media directories can be separate, so opening the browser UI at port 8000 does not prove that the packaged desktop environment at port 18000 is using the same projects.

## Quick start

These commands start the browser-development stack on Windows with PowerShell.

### Requirements

- Git and Docker Desktop with Docker Compose v2
- Node.js and npm to run the desktop UI
- Rust and the Windows C++ build tools when building the Tauri shell
- Python 3.12 and backend requirements only when running backend tests outside Docker
- A working NVIDIA Container Toolkit setup when using the GPU reservation declared by the standard Compose file

### Start the API and browser UI

~~~powershell
git clone https://github.com/desanv01/ai-video-editor.git
Set-Location ai-video-editor

Copy-Item .env.example .env
# Edit .env and set the values needed for your chosen providers and local environment.

docker compose up -d --build
docker compose ps
Invoke-RestMethod http://localhost:8000/health

npm ci --prefix desktop
npm run dev --prefix desktop
~~~

Open the Vite URL printed in the terminal (the development port is 1420). The API documentation is available at http://localhost:8000/docs.

The backend image supplies its Python runtime and media tools. If running the backend directly on the host instead of through Docker, install the dependencies from backend/requirements.txt and provide the required database, vector-store, and storage configuration.

### Run the native Tauri shell

After Docker is running and the desktop dependencies are installed:

~~~powershell
Set-Location desktop
npx tauri dev
~~~

The native shell uses the packaged-desktop Compose configuration and its loopback API port. Rust and the Windows C++ build tools are required to build or run the shell from source.

## Configuration and data locations

- .env.example documents the Compose and provider settings. Copy it to .env for local use; never commit .env or provider keys.
- The standard Compose stack binds the repository's uploads/ directory into the backend and keeps generated video storage, PostgreSQL, Qdrant, and Redis in named Docker volumes.
- The packaged-desktop Compose stack receives host storage paths from the Tauri launcher. It has its own default ports and can use different database and media directories.
- Source-folder copies do not include Docker named volumes. Back up database and media volumes separately before moving or changing a running installation.
- This prototype has no application sign-in layer. Keep its API and database services on a trusted local machine or network; do not expose the Compose ports directly to the public internet.

Provider-backed features need the relevant provider credentials. Stored provider credentials are encrypted only when APP_SETTINGS_SECRET_KEY is configured. Local/manual workflows do not require every hosted provider.

## Original transcript downloads

Open a saved recording in the browser editor and use **Original Transcript** in either **Transcribe** or **Export**. Choose plain TXT, timestamped TXT, structured JSON, or segment CSV. These downloads use the stored original-recording transcript, including speech later removed from the edit; they do not require approval, rendering, or another transcription request. Existing transcribed projects work without reprocessing.

Plain TXT preserves the stored full text. Legacy records without full text fall back to stored segment or word text, identified by `text_source` in JSON. Timestamped TXT uses original segment times and existing speaker labels; missing or invalid times are marked unavailable. CSV contains one row per stored transcript segment, including source times and timing availability. JSON preserves the stored provider words, segments, speakers, language, and provider metadata. Stored upstream timing may itself be approximate; export does not estimate or remap timing. Missing segment data disables the relevant formats while text and JSON remain available.

The **Evidence Bundle (ZIP)** includes the same transcript files and lists them in its evidence index. Files are refreshed when preparing a bundle or completing a video/audio export; standalone downloads are generated directly from the database. Transcript download filenames use the original recording's name.

API: `GET /api/v1/videos/{video_id}/transcript/export?format=txt`, with `txt`, `timestamped_txt`, `json`, or `csv`. The existing `/videos/{video_id}/exports` catalogue reports format availability and unavailable reasons. Missing videos/transcripts return 404; unsupported formats and invalid UUIDs return 422.

To verify against an existing local recording without starting ASR or rendering:

```powershell
.\.venv\Scripts\python.exe scripts\verify_transcript_exports.py <video-id> --bundle
```

The script checks download content, filenames, UTF-8, browser response headers, validation errors, bundle parity, and unchanged stored transcript/status. `--bundle` refreshes the existing evidence artifacts and their metadata. Optionally pass `--missing-transcript-video <video-id>` to check a saved recording that has not been transcribed.

## Verification and project evidence

The repository records a full verification run on 21 June 2026:

| Check | Recorded result |
|---|---|
| Backend unittest suite | 193 tests passed |
| React and TypeScript production build | Passed |
| Tauri/Rust integration check | Passed |
| Docker Compose configuration validation | Passed |

These are historical results for the recorded source snapshot, not a claim that those checks were rerun for every later commit. See [the verification report](docs/reproducibility/VERIFICATION_RESULTS.md). A separate local Docker API check on 25 September 2026 returned a healthy response and the saved project list; it was an operational smoke check, not a rerun of the full test suite.

Useful technical references:

- [System architecture](docs/fyp_context_pack/03_SYSTEM_ARCHITECTURE.md)
- [Database and persistence model](docs/fyp_context_pack/10_DATABASE_AND_PERSISTENCE_MODEL.md)
- [API endpoint inventory](docs/fyp_context_pack/11_API_ENDPOINT_AND_SCHEMA_INVENTORY.md)
- [AI provider configuration](docs/fyp_context_pack/13_AI_PROVIDER_CONFIGURATION.md)
- [Testing and quality status](docs/fyp_context_pack/15_TESTING_BUILD_AND_QUALITY_STATUS.md)
- [Reproducibility guide](docs/reproducibility/REPRODUCIBILITY_GUIDE.md)
- [FYP context pack](docs/fyp_context_pack/00_README.md)

## Repository layout

~~~text
backend/
  app/                  FastAPI routes, agents, providers, database, RAG, and services
  tests/                Backend test suite
  alembic/              Database migrations
desktop/
  src/                  React lecturer interface
  src-tauri/            Tauri shell and desktop backend bootstrap
  revideo/              Optional Revideo scene and render support
docs/
  fyp_context_pack/     Architecture, implementation, and thesis evidence
  reproducibility/      Verification and source-package guidance
fixtures/               Synthetic evaluation fixtures
scripts/                Setup, verification, and source-package utilities
docker-compose.yml      Browser/development services
docker-compose.desktop.yml
                        Packaged desktop services and host storage mounts
~~~

The separate [AI Video Editor Desktop V2 repository](https://github.com/desanv01/ai-video-editor-desktop-v2) contains the later standalone desktop application line. This repository remains the academic FYP source and evidence package.

## Data handling

Lecture recordings, course files, provider credentials, local databases, generated media, and Docker state may contain private information. Keep those materials out of GitHub. Use synthetic fixtures for reproducible checks and follow the repository's .gitignore and source-package guidance when preparing an archive.
