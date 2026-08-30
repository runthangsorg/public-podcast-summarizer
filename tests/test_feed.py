import unittest

from public_podcast_summarizer.feed import parse_feed


SAMPLE_FEED = b"""<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <title>Example Engineering Podcast</title>
    <item>
      <guid>episode-2</guid>
      <title>Reliable queues</title>
      <pubDate>Tue, 02 Jan 2030 08:00:00 GMT</pubDate>
      <description><![CDATA[<p>How bounded queues prevent overload.</p>]]></description>
      <link>https://example.test/episodes/2?tracking=public</link>
      <enclosure url="https://media.example.test/private-audio.mp3" type="audio/mpeg"/>
    </item>
    <item>
      <guid>episode-1</guid>
      <title>Old episode</title>
      <description>Older notes.</description>
      <link>https://example.test/episodes/1</link>
    </item>
  </channel>
</rss>
"""


class FeedTests(unittest.TestCase):
    def test_parses_only_bounded_metadata_and_never_returns_audio_urls(self):
        episodes = parse_feed(SAMPLE_FEED, max_episodes=1)

        self.assertEqual(len(episodes), 1)
        self.assertEqual(episodes[0].podcast, "Example Engineering Podcast")
        self.assertEqual(episodes[0].title, "Reliable queues")
        self.assertEqual(episodes[0].notes, "How bounded queues prevent overload.")
        self.assertEqual(episodes[0].link_kind, "episode_page")
        self.assertNotIn("audio", episodes[0].to_public_dict())
        self.assertNotIn("media.example", str(episodes[0].to_public_dict()))

    def test_rejects_unbounded_episode_limits(self):
        with self.assertRaises(ValueError):
            parse_feed(SAMPLE_FEED, max_episodes=51)

    def test_missing_episode_page_falls_back_to_publisher_show_page(self):
        payload = b"""<rss><channel>
        <title>Example Show</title>
        <link>https://example.test/show</link>
        <item><title>Episode without page</title><description>Notes.</description>
        <enclosure url="https://media.example.test/private-audio.mp3" type="audio/mpeg"/>
        </item></channel></rss>"""

        episode = parse_feed(payload, max_episodes=1)[0]

        self.assertEqual(episode.link, "https://example.test/show")
        self.assertEqual(episode.link_kind, "show_page")
        self.assertNotIn("media.example", str(episode.to_public_dict()))


if __name__ == "__main__":
    unittest.main()
