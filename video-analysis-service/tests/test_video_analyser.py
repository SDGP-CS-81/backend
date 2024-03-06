from app.video_analyser import VideoAnalyser
from app.video_downloader import VideoDownloader
from unittest import IsolatedAsyncioTestCase
from PIL import Image
import asyncio


class VideoAnalyserTest(IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        video_id = "3qLs27KTYAg"
        vid_dl = VideoDownloader(video_id)
        cls.video_frames = asyncio.run(vid_dl.get_video_frames())
        # Mock category keywords dictionary
        cls.keywords = {
            "music": ["music", "song", "orchestra", "rap", "rock", "classical", "pop"],
            "coding": ["programming", "java", "javascript", "c#", "c++"],
        }

    def test_text_scores(self):
        """
        Test to ensure that the keyword scoring algorithm works as expected
        """
        test_data = "This is a programming video about the java programming language. We will also be looking at it's similarity to C#"
        text_scores = VideoAnalyser.calculate_text_scores(test_data, self.keywords)

        self.assertEqual(0, text_scores["music"], "Expected no matches for music!")
        self.assertEqual(3, text_scores["coding"], "Expected 3 matches for coding!")

    def test_text_scores_case_insensitive_upper(self):
        """
        Test to ensure that keywords are checked with case insensitivity
        """
        test_data = "This is a programming video about the java programming language. We will also be looking at it's similarity to C#"
        text_scores = VideoAnalyser.calculate_text_scores(
            test_data.upper(), self.keywords
        )

        self.assertEqual(0, text_scores["music"], "Expected no matches for music!")
        self.assertEqual(3, text_scores["coding"], "Expected 3 matches for coding!")

    def test_text_scores_case_insensitive_lower(self):
        """
        Test to ensure that keywords are checked with case insensitivity
        """
        test_data = "This is a programming video about the java programming language. We will also be looking at it's similarity to C#"
        text_scores = VideoAnalyser.calculate_text_scores(
            test_data.lower(), self.keywords
        )

        self.assertEqual(0, text_scores["music"], "Expected no matches for music!")
        self.assertEqual(3, text_scores["coding"], "Expected 3 matches for coding!")

    async def test_frame_scores(self):
        """
        Test to ensure that the scores are properly populated
        """
        vid_anl = VideoAnalyser(self.video_frames)
        (
            detail_score,
            diff_score,
            selected_frame,
        ) = await vid_anl.calculate_frame_scores()

        self.assertLess(0, detail_score, "Expected a valid detail score!")
        self.assertLess(0, diff_score, "Expected a valid diff score!")
        self.assertIsInstance(selected_frame, Image.Image, "Expected a valid image!")

    async def test_frame_scores_non_duplication(self):
        """
        Tests to ensure that frame duplication does not take place within the object

        Frame duplication could happen if incorrect code is written in the
        map generation steps
        """
        vid_anl = VideoAnalyser(self.video_frames)
        # Generate the filtered frame data
        
        await vid_anl.calculate_frame_scores()

        # Check internal structures to make sure frame duplication has not occured
        self.assertGreaterEqual(
            len(self.video_frames),
            len(vid_anl.filtered_frame_data),
            "Expected less or equal amount of filtered frames!",
        )
        self.assertGreaterEqual(
            len(self.video_frames),
            len(vid_anl.frame_edge_maps),
            "Expected less or equal amount of edge maps to video frames!",
        )
        self.assertGreaterEqual(
            len(self.video_frames),
            len(vid_anl.frame_diff_maps),
            "Expected less or equal amount of diff maps to video frames!",
        )
