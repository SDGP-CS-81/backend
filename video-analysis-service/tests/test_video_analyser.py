from app.video_analyser import VideoAnalyser
from app.video_downloader import VideoDownloader
from app.logger import setup_logger
from unittest import IsolatedAsyncioTestCase
from PIL import Image
import asyncio

logger = setup_logger(__name__, log_level="DEBUG", log_file=None)


class VideoAnalyserTest(IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        logger.info("Set up testing class.")

        video_id = "3qLs27KTYAg"
        vid_dl = VideoDownloader(video_id)

        logger.info("Getting test video frames.")

        cls.video_frames = asyncio.get_event_loop().run_until_complete(
            vid_dl.get_video_frames()
        )
        asyncio.get_event_loop().run_until_complete(vid_dl.close_http_connections())
        # Mock category keywords dictionary
        cls.keywords = {
            "music": ["music", "song", "orchestra", "rap", "rock", "classical", "pop"],
            "coding": ["programming", "java", "javascript", "c#", "c++"],
        }

        logger.info("Testing class set up completed.")

    def test_text_scores(self):
        """
        Test to ensure that the keyword scoring algorithm works as expected
        """

        logger.info("Starting keyword scoring test.")

        test_data = "This is a programming video about the java programming language. We will also be looking at it's similarity to C#"
        text_scores = VideoAnalyser.calculate_text_scores(test_data, self.keywords)

        self.assertEqual(0, text_scores["music"], "Expected no matches for music!")
        self.assertEqual(3, text_scores["coding"], "Expected 3 matches for coding!")

        logger.info("Keyword scoring test passed.")

    def test_text_scores_case_insensitive_upper(self):
        """
        Test to ensure that keywords are checked with case insensitivity
        """

        logger.info("Starting keyword scoring case insensitivity test.")

        test_data = "This is a programming video about the java programming language. We will also be looking at it's similarity to C#"
        text_scores = VideoAnalyser.calculate_text_scores(
            test_data.upper(), self.keywords
        )

        self.assertEqual(0, text_scores["music"], "Expected no matches for music!")
        self.assertEqual(3, text_scores["coding"], "Expected 3 matches for coding!")

        logger.info("Keyword scoring case insensitivity test passed.")

    def test_text_scores_case_insensitive_lower(self):
        """
        Test to ensure that keywords are checked with case insensitivity
        """

        logger.info("Starting keyword scoring case insensitivity test.")

        test_data = "This is a programming video about the java programming language. We will also be looking at it's similarity to C#"
        text_scores = VideoAnalyser.calculate_text_scores(
            test_data.lower(), self.keywords
        )

        self.assertEqual(0, text_scores["music"], "Expected no matches for music!")
        self.assertEqual(3, text_scores["coding"], "Expected 3 matches for coding!")

        logger.info("Keyword scoring case insensitivity test passed.")

    async def test_frame_scores(self):
        """
        Test to ensure that the scores are properly populated
        """

        logger.info("Starting frame scoring test.")

        vid_anl = VideoAnalyser(self.video_frames)
        (
            detail_score,
            diff_score,
            selected_frame,
        ) = await vid_anl.calculate_frame_scores()

        logger.info(
            f"Scores: detail_score: {detail_score}, diff_score: {diff_score}, selected_frame: {selected_frame is not None}"
        )

        self.assertLess(0, detail_score, "Expected a valid detail score!")
        self.assertLess(0, diff_score, "Expected a valid diff score!")
        self.assertIsInstance(selected_frame, Image.Image, "Expected a valid image!")

        logger.info("Frame scoring test passed.")

    async def test_frame_scores_non_duplication(self):
        """
        Tests to ensure that frame duplication does not take place within the object

        Frame duplication could happen if incorrect code is written in the
        map generation steps
        """

        logger.info("Starting frame duplication test.")

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

        logger.info("Frame duplication test passed.")
