# Get started with AIVE

## Requirements

- Git and Docker Desktop with Docker Compose v2.
- Node.js and npm for the React interface.
- NVIDIA Container Toolkit support for the GPU reservation in the supplied Compose file.
- Credentials for the hosted processing providers you choose.
- Rust and Windows C++ build tools only if building the Tauri shell.
- Python 3.12 and backend requirements only if running backend tests or services outside Docker.

## Start the browser development interface

```powershell
git clone https://github.com/desanv01/ai-video-editor.git
Set-Location ai-video-editor
Copy-Item .env.example .env
```

Edit `.env` for your chosen providers and environment. The sample contains placeholder credentials; replace them before using the corresponding hosted routes. Keep database credentials consistent with `DATABASE_URL`.

```powershell
docker compose up -d --build
docker compose ps
Invoke-RestMethod http://localhost:8000/health
npm ci --prefix desktop
npm run dev --prefix desktop
```

Open the Vite URL printed in the terminal, normally http://localhost:1420. The API reference is at http://localhost:8000/docs. The backend image provides Python and media tools.

Create a project, import a lecture recording and its course materials, process the sources, and review the proposed edits. Approve the plan before starting the final render.

## Provider settings

The configuration supports hosted, local, and hybrid processing routes. Availability depends on the selected adapter, credentials, model files, and runtime; a local setting alone does not establish a complete offline workflow.

Set `APP_SETTINGS_SECRET_KEY` before storing provider credentials through application settings. Stored credentials are encrypted only when this key is configured. Back up the key securely alongside the database if you need to restore encrypted settings.

Hosted processing may send source content to selected providers. Use materials you have permission to process and review the providers' data policies.

## Run the Tauri shell from source

With Docker running and frontend dependencies installed:

```powershell
Set-Location desktop
npx tauri dev
```

The shell starts the packaged-desktop Compose configuration using launcher-provided storage paths and a loopback API port. Running that Compose file directly requires the same launcher variables. Building the shell requires Rust and the Windows C++ build tools.

For the newer standalone Windows application, see [AIVE Desktop V2](https://github.com/desanv01/ai-video-editor-desktop-v2).

## Ports

| Port | Service |
| --- | --- |
| 1420 | Vite development interface |
| 8000 | Standard Compose API |
| 5432 | Standard Compose PostgreSQL |
| 6333 / 6334 | Qdrant REST / gRPC |
| 6379 | Provisioned Redis service |
| 18000 | Packaged Tauri backend, loopback-bound by default |

The application has no sign-in layer. Use a trusted local machine or network, and do not expose API or database ports to the public internet.

## Storage and backups

- Standard Compose binds `uploads/` into the backend. Generated video storage, PostgreSQL, Qdrant, and Redis use named Docker volumes.
- The packaged-desktop stack receives host storage paths from its launcher and can use separate media and database locations.
- Browser and packaged-desktop modes can therefore show different saved projects.
- Copying the source directory does not copy Docker named volumes. Back up the database, media, and relevant configuration separately.
- Keep `.env`, credentials, recordings, generated media, and database backups out of Git.

[Documentation index](README.md)
