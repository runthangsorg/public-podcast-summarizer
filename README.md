# Public Podcast Summarizer

A small, deterministic podcast summarizer that parses bounded publisher RSS or
Atom metadata and turns show notes into concise bullets. It uses only the
Python standard library.

The engine deliberately does not download audio, transcribe speech, send
email, keep seen-state, or upload artifacts. This fresh repository contains no
personal subscription list, OPML, recipient, transcript, media, credential,
runtime state, local path, or history from another repository.

## Run

    PYTHONPATH=src python -m unittest discover -s tests -v
    PYTHONPATH=src python -m public_podcast_summarizer \
      --feed examples/feed.xml --max-episodes 1

Local XML and public HTTP(S) feed sources are supported. Input is limited to
2 MB, network reads use a timeout, media extensions are rejected, and each run
accepts at most 50 episodes. Output is labelled
publisher_metadata_only; it is not a transcript or evidence that the audio
was reviewed.

Private scheduling can pass one approved feed URL at a time without committing
a subscription list. The public workflow intentionally uses only a synthetic
feed.

## GitHub Actions

The workflow has read-only permissions, pinned actions, a five-minute timeout,
no secrets, no artifacts, and one concurrency slot. Its daily schedule is a
bounded health check.

## License

MIT
