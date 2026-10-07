# Original transcript downloads

Open a saved recording and select **Original Transcript** in **Transcribe** or **Export**. Download the stored transcript without approving edits, rendering, or sending another transcription request.

These files retain speech from the original recording, including passages removed from the edited video. Existing transcribed projects work without reprocessing.

## Formats

| Format | Contents |
| --- | --- |
| Plain TXT | Stored full text; older records fall back to segment or word text |
| Timestamped TXT | Original segment times and existing speaker labels |
| JSON | Provider words, segments, speakers, language, provider metadata, and text source |
| Segment CSV | One row per stored segment, including source times and timing availability |

Missing or invalid times are marked unavailable. Upstream timing can be approximate; download does not estimate or remap it. Missing segment data disables the relevant formats while plain text and JSON remain available.

The **Evidence Bundle (ZIP)** includes these files and lists them in its index. Bundle preparation and video/audio export refresh stored artifacts; standalone downloads are generated directly from the database. Filenames use the original recording name.

## API

`GET /api/v1/videos/{video_id}/transcript/export?format=txt`

Supported values: `txt`, `timestamped_txt`, `json`, and `csv`. The `/videos/{video_id}/exports` catalogue reports availability and unavailable reasons. Missing videos or transcripts return 404; invalid UUIDs and unsupported formats return 422.

## Verify a saved recording

With the API running and a configured local Python environment:

```powershell
.\.venv\Scripts\python.exe scripts\verify_transcript_exports.py <video-id> --bundle
```

The command checks content, filenames, UTF-8, response headers, validation errors, bundle parity, and unchanged stored transcript/status. `--bundle` refreshes evidence artifacts and metadata. Add `--missing-transcript-video <video-id>` to check a saved recording with no transcript.

[Documentation index](README.md)
