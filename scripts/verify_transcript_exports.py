"""Verify original transcript downloads against a running local AIVE backend.

Uses existing stored data. Does not start transcription, approve edits, or render.
Pass --bundle to also refresh and verify the existing evidence bundle.
"""

import argparse
import csv
import io
import json
from urllib.error import HTTPError
from urllib.parse import unquote
from urllib.request import Request, urlopen
import uuid
import zipfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video_id", type=uuid.UUID)
    parser.add_argument("--base-url", default="http://localhost:8000/api/v1")
    parser.add_argument("--bundle", action="store_true")
    parser.add_argument("--missing-transcript-video", type=uuid.UUID,
                        help="Also verify a saved video that has not been transcribed.")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    video_url = f"{base}/videos/{args.video_id}"

    def get(url):
        with urlopen(Request(url, headers={"Origin": "http://127.0.0.1:1420"}), timeout=60) as response:
            return response.read(), response.headers

    def expect_status(url, status):
        try:
            get(url)
        except HTTPError as error:
            assert error.code == status, (url, error.code, status)
        else:
            raise AssertionError(f"Expected HTTP {status}: {url}")

    before = json.loads(get(video_url)[0])
    catalog = json.loads(get(f"{video_url}/exports")[0])["exports"]
    downloads = {}
    names = {}
    for kind, artifact in catalog.items():
        if not kind.startswith("original_transcript_") or not artifact["available"]:
            continue
        format_name = artifact["format"]
        content, headers = get(f"{video_url}/transcript/export?format={format_name}")
        assert content, format_name
        assert "attachment;" in headers["Content-Disposition"]
        assert "Content-Disposition" in headers["Access-Control-Expose-Headers"]
        assert headers["Cache-Control"] == "private, no-store"
        content.decode("utf-8")
        downloads[format_name] = content
        names[format_name] = unquote(headers["Content-Disposition"].split("UTF-8''", 1)[1])
    assert "txt" in downloads and "json" in downloads, "An existing text transcript is required."
    data = json.loads(downloads["json"])
    assert data["timeline"] == "original_recording"
    assert data["transcript_variant"] == "original"
    assert downloads["txt"].decode("utf-8") == data["text"]
    if before.get("transcript", {}).get("full_text"):
        assert data["full_text"] == before["transcript"]["full_text"]
        assert downloads["txt"].decode("utf-8") == before["transcript"]["full_text"]
    if "csv" in downloads:
        rows = list(csv.DictReader(io.StringIO(downloads["csv"].decode("utf-8"))))
        assert len(rows) == len(data["segment_rows"])
        assert [row["text"] for row in rows] == [row["text"] for row in data["segment_rows"]]
    expect_status(f"{video_url}/transcript/export?format=pdf", 422)
    expect_status(f"{base}/videos/not-a-uuid/transcript/export", 422)
    expect_status(f"{base}/videos/{uuid.uuid4()}/transcript/export", 404)
    if args.missing_transcript_video:
        missing_url = f"{base}/videos/{args.missing_transcript_video}"
        missing_catalog = json.loads(get(f"{missing_url}/exports")[0])["exports"]
        for kind, artifact in missing_catalog.items():
            if kind.startswith("original_transcript_"):
                assert not artifact["available"] and artifact["reason"]
                expect_status(f"{missing_url}/transcript/export?format={artifact['format']}", 404)
    if args.bundle:
        bundle_content, _ = get(f"{video_url}/evidence/bundle")
        suffixes = {
            "txt": "original_transcript.txt", "timestamped_txt": "original_transcript_timestamped.txt",
            "json": "original_transcript.json", "csv": "original_transcript_segments.csv",
        }
        with zipfile.ZipFile(io.BytesIO(bundle_content)) as bundle:
            for format_name, content in downloads.items():
                assert bundle.read(f"{args.video_id}_{suffixes[format_name]}") == content
            index = json.loads(bundle.read(f"{args.video_id}_generated_evidence_index.json"))
            for kind, artifact in catalog.items():
                if kind.startswith("original_transcript_") and artifact["available"]:
                    assert kind in json.dumps(index)
    after = json.loads(get(video_url)[0])
    assert before["status"] == after["status"], "Download changed processing status."
    assert before.get("transcript") == after.get("transcript"), "Download changed stored transcript."
    print(json.dumps({
        "video_id": str(args.video_id), "status": after["status"], "provider": data["asr_provider"],
        "formats_verified": sorted(downloads), "filenames": names,
        "bundle_verified": args.bundle, "stored_transcript_unchanged": True,
        "validation_and_missing_video_errors_verified": True,
        "missing_transcript_verified": bool(args.missing_transcript_video),
    }, indent=2))


if __name__ == "__main__":
    main()
