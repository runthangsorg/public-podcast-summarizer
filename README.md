# Public Podcast Summarizer

A small, deterministic podcast metadata summarizer that parses bounded
publisher RSS or Atom feeds, turns publisher show notes into concise bullets,
and can deliver a responsive HTML digest by SMTP. It uses only the Python
standard library.

The engine deliberately does not download audio, transcribe speech, keep
seen-state, or upload artifacts. This repository contains no personal
subscription list, OPML, recipient, transcript, media, credential, runtime
state or generated report. Feed choices are runtime-only encrypted data.

## Run

    PYTHONPATH=src python -m unittest discover -s tests -v
    PYTHONPATH=src python -m public_podcast_summarizer \
      --feed examples/feed.xml --max-episodes 1

Local XML and public HTTP(S) feed sources are supported. Input is limited to
25 MB, network reads use a timeout, media extensions are rejected, and each
configured feed accepts at most 10 episodes. Output is labelled
`publisher_metadata_only`; it is not a transcript or evidence that audio was
reviewed.

Production passes a strict 1–20 feed list through `PODCAST_CONFIG_JSON` without
committing a subscription list. Configured runs write only structural counts
to Actions logs; feed names, episode titles, report contents and recipient
details are not printed or uploaded. Each feed can include an `expected_title`;
the run rejects a feed whose publisher channel title does not match, preventing
a redirected or mistyped URL from silently delivering the wrong show. Episode
buttons use publisher web pages only—never media enclosure URLs—and are
truthfully labelled as show-page fallbacks when an episode page is unavailable.

## GitHub Actions

`ci.yml` has read-only permissions, pinned actions, a five-minute timeout, no
secrets or artifacts, and runs only for code events/manual checks. The separate
`podcast-digest.yml` production workflow runs once daily on its defined schedule
only when `ENABLE_PODCAST_DIGEST=true`; manual dispatch defaults to dry-run.

Production requires encrypted secrets named `PODCAST_CONFIG_JSON`,
`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, and
`REPORT_RECIPIENT`. Invalid feed JSON or incomplete live SMTP configuration
fails closed instead of silently selecting public defaults or reporting
success.

This service summarizes publisher metadata. Audio transcription and semantic
audio summarization remain a separate, heavier workload and must not be
claimed as completed by this repository.

## License

MIT
