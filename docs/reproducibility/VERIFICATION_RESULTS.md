# Final Thesis Source Verification

Verification date: 21 June 2026 (Asia/Calcutta)

| Check | Command | Result |
|---|---|---|
| Canonical backend suite | `.\.venv\Scripts\python.exe -m unittest discover -s backend\tests -p "test_*.py"` | PASS - 193 tests in 17.277 s |
| React/TypeScript production build | `npm run build --prefix desktop` | PASS - TypeScript and Vite production build completed; 1,598 modules transformed |
| Tauri/Rust integration | `cargo check --manifest-path desktop\src-tauri\Cargo.toml` | PASS - development profile completed |
| Docker Compose validation | `docker compose config --quiet` | PASS - configuration valid |

Observed non-failing warnings:

- SWIG/PyMuPDF deprecation warnings during selected document/rendering tests.
- Expected provider-fallback messages in tests that intentionally simulate unavailable transcription routes.

The source archive and Appendix A must be generated from the tagged final commit after these checks pass.

## Original transcript downloads — 1 October 2026 (Asia/Kuala_Lumpur)

This is a feature verification update to the original browser/Docker FYP workflow, separate from standalone desktop packaging. It does not replace the June thesis snapshot results above.

| Check | Result |
|---|---|
| New transcript export unit tests | PASS — 13 tests: exact stored text/Unicode, original timing, CSV round-trip, JSON provider data, missing/invalid timing, legacy text fallback, availability, safe filenames, bundle parity, refreshed/stale artifacts |
| Full canonical backend suite | 204 of 206 passed in 22.219 s; two existing native compositor timing failures remain |
| Render/export regression suite | PASS — all 38 `test_picture_in_picture_renderer.py` tests, including audio-only export and primary artifact ordering |
| React/TypeScript production build | PASS — `npm run build --prefix desktop`; 1,598 modules transformed |
| Live API, existing unrendered Whisper project | PASS — all four formats; stored text matches database, original timeline declared, CSV rows match JSON, source-based filenames and UTF-8/attachment/CORS headers verified |
| Live evidence bundle | PASS — all four transcript files match the corresponding standalone downloads byte-for-byte and appear in the generated evidence index |
| Live completed Whisper project | PASS — all four formats, without reprocessing |
| Missing transcript and validation | PASS — existing untranscribed recording reports all formats unavailable and returns 404; missing video returns 404; invalid UUID/unsupported format return 422 |
| Browser workflow | PASS — Original Transcript controls visible in both Transcribe and Export before approval/rendering; TXT/JSON clicks reach download-start feedback |
| Download side effects | PASS — stored transcript and video status unchanged; no transcription or rendering request used |
| Whitespace/diff check | PASS — `git diff --check` |

The two full-suite failures also reproduce against the pre-change `HEAD` source extracted into an ignored temporary directory:

- `test_renders_ranged_layouts_with_audio_video_drift_under_50ms`: video duration 3.9 s versus expected 4.0 s (50 ms tolerance).
- `test_thirty_one_scenes_render_without_unbounded_filter_graph`: audio/video duration difference 0.078667 s versus required less than 0.05 s.

No compositor timing code was changed for transcript export. The full suite therefore remains non-green because of these baseline failures. The browser automation did not capture a downloadable-file event for the blob download; actual HTTP attachment content and ZIP parity were verified independently, while the browser check confirms controls and download-start feedback.

Reproduce the live checks with an existing transcribed video ID:

```powershell
.\.venv\Scripts\python.exe scripts\verify_transcript_exports.py <video-id> --bundle --missing-transcript-video <untranscribed-video-id>
```

The Python suite and Vite build require permission to read installed dependencies/start their subprocesses in the restricted desktop environment. Docker services were resumed and the AIVE backend restarted to load the endpoint. The browser frontend was started at `http://127.0.0.1:1420/`. No database migration, ASR call, or existing-video rerender was needed. Bundle verification refreshes the existing evidence artifacts and metadata as the normal bundle endpoint does.
