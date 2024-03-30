from app.video_downloader import VideoDownloader, VideoDownloaderError
from app.logger import setup_logger
from unittest import IsolatedAsyncioTestCase
import asyncio

logger = setup_logger(__name__, log_level="DEBUG", log_file=None)


class VideoDownloaderTest(IsolatedAsyncioTestCase):
    def setUp(self):
        logger.info("Set up testing class.")
        self.video_ids = ["_V8eKsto3Ug", "9uhig4A9gf4", "WXV-zB3EfNw"]
        logger.info(f"Testing video IDs: {self.video_ids}")

    async def test_text_data_no_exception(self):
        """
        Test to ensure that no exceptions are thrown with expected usage
        """

        logger.info("Starting text data retrieval test.")

        for result in await asyncio.gather(
            *(VideoDownloader(id).get_video_text_info() for id in self.video_ids),
            return_exceptions=True,
        ):
            self.assertTrue(
                not (isinstance(result, VideoDownloaderError)),
                "Expected text data!",
            )

        logger.info("Text data retrieval test passed.")

    async def test_text_data_category_not_empty(self):
        """
        Test to ensure that the video category is properly populated
        """

        logger.info("Starting category data test.")

        for result in await asyncio.gather(
            *(VideoDownloader(id).get_video_text_info() for id in self.video_ids)
        ):
            self.assertLess(0, len(result[0]), "Expected more than 0 categories!")

        logger.info("Category data test passed.")

    async def test_text_data_text_not_empty(self):
        """
        Test to ensure that text data is properly populated
        """

        logger.info("Starting text data test.")

        for result in await asyncio.gather(
            *(VideoDownloader(id).get_video_text_info() for id in self.video_ids)
        ):
            self.assertLess(
                0,
                len(result[1]),
                # Assuming that at least video titles are not empty
                "Expected more than 0 characters of text!",
            )

        logger.info("Text data test passed.")