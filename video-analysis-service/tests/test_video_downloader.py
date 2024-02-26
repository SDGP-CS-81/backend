from app.video_downloader import VideoDownloader, VideoDownloaderError
from unittest import IsolatedAsyncioTestCase
import asyncio


class VideoDownloaderTest(IsolatedAsyncioTestCase):
    def setUp(self):
        self.video_ids = ["3qLs27KTYAg", "IOzkOXSz9gE"]

    async def test_text_data_no_exception(self):
        """
        Test to ensure that no exceptions are thrown with expected usage
        """
        for result in await asyncio.gather(
            *(VideoDownloader(id).get_video_text_info() for id in self.video_ids),
            return_exceptions=True,
        ):
            self.assertTrue(
                not (isinstance(result, VideoDownloaderError)),
                "Expected text data!",
            )

    async def test_frame_data_no_exception(self):
        """
        Test to ensure that no exceptions are thrown with expected usage
        """
        for result in await asyncio.gather(
            *(VideoDownloader(id).get_video_frames() for id in self.video_ids),
            return_exceptions=True,
        ):
            self.assertTrue(
                not (isinstance(result, VideoDownloaderError)), "Expected image data!"
            )

    async def test_text_data_category_not_empty(self):
        """
        Test to ensure that the video category is properly populated
        """
        for result in await asyncio.gather(
            *(VideoDownloader(id).get_video_text_info() for id in self.video_ids)
        ):
            self.assertLess(0, len(result[0]), "Expected more than 0 categories!")

    async def test_text_data_text_not_empty(self):
        """
        Test to ensure that text data is properly populated
        """
        for result in await asyncio.gather(
            *(VideoDownloader(id).get_video_text_info() for id in self.video_ids)
        ):
            self.assertLess(
                0,
                len(result[1]),
                # Assuming that at least video titles are not empty
                "Expected more than 0 characters of text!",
            )

    async def test_frame_data_not_empty(self):
        """
        Test to ensure that downloader returns at least 2 images

        We check for 2 since diffing requires at least 2 images
        """
        for result in await asyncio.gather(
            *(VideoDownloader(id).get_video_frames() for id in self.video_ids)
        ):
            self.assertLess(1, len(result), "Expected at least 2 images!")
