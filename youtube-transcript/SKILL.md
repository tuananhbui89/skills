---
name: youtube-transcript
description: Fetch YouTube video transcripts from YouTube URLs or video IDs, save the transcript in the current workspace directory, and provide a concise content summary. Use when the user gives a YouTube link and asks to get, download, extract, save, summarize, or analyze the video's transcript; supports common YouTube URL formats such as watch, youtu.be, shorts, embed, live, and playlist URLs containing a video parameter.
---

# YouTube Transcript

## Workflow

1. Run `scripts/get_transcript.py` with the user's YouTube URL or video ID.
2. Save output in the current workspace directory unless the user names a different destination.
3. Read the saved `.txt` transcript and summarize the video's content concisely.
4. Report the transcript path, video ID, language used, and any limitations such as unavailable transcripts, private videos, age restrictions, or request blocking.

## Quick Start

Use:

```bash
python3 /path/to/youtube-transcript/scripts/get_transcript.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

Useful options:

```bash
python3 /path/to/youtube-transcript/scripts/get_transcript.py URL --languages en vi --output-dir .
python3 /path/to/youtube-transcript/scripts/get_transcript.py URL --format json --output-dir transcripts
python3 /path/to/youtube-transcript/scripts/get_transcript.py URL --preserve-formatting
python3 /path/to/youtube-transcript/scripts/get_transcript.py URL --no-fallback-any
```

The script prints JSON metadata with `output_path`, `video_id`, `language`, `language_code`, `is_generated`, snippet counts, and any fallback note. Use `output_path` to read the transcript for summarization.

## URL Handling

Accept full URLs or bare IDs. Prefer passing the original user input to the script; it handles:

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/live/VIDEO_ID`
- playlist or timestamp URLs that include `v=VIDEO_ID`

## Dependency

The script requires the `youtube-transcript-api` Python package. If the package is missing, install it in the active environment:

```bash
python3 -m pip install youtube-transcript-api
```

If network access or package installation is blocked, explain that the transcript fetch cannot be completed until the dependency is available.

## Summaries

Keep the final response compact:

- State where the transcript was saved.
- Give a short paragraph or 3-6 bullets covering the main ideas.
- Mention if the transcript was auto-generated, translated, incomplete, or unavailable.
