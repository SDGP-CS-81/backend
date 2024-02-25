from app.video_downloader import VideoDownloader, VideoDownloaderError
from unittest import IsolatedAsyncioTestCase
import asyncio


class VideoDownloaderTest(IsolatedAsyncioTestCase):
    def setUp(self):
        self.video_ids = ["3qLs27KTYAg", "IOzkOXSz9gE"]

    async def test_text_data_no_exception(self):
        [
            self.assertTrue(not (isinstance(result, VideoDownloaderError)))
            for result in await asyncio.gather(
                *(VideoDownloader(id).get_video_text_info() for id in self.video_ids),
                return_exceptions=True,
            )
        ]

    async def test_frame_data_no_exception(self):
        [
            self.assertTrue(not (isinstance(result, VideoDownloaderError)))
            for result in await asyncio.gather(
                *(VideoDownloader(id).get_video_frames() for id in self.video_ids),
                return_exceptions=True,
            )
        ]

    async def test_text_data_category_not_empty(self):
        [
            self.assertLess(0, len(result[0]))
            for result in await asyncio.gather(
                *(VideoDownloader(id).get_video_text_info() for id in self.video_ids),
            )
        ]

    async def test_text_data_text_not_empty(self):
        [
            self.assertLess(0, len(result[1]))
            for result in await asyncio.gather(
                *(VideoDownloader(id).get_video_text_info() for id in self.video_ids),
            )
        ]

    async def test_frame_data_not_empty(self):
        [
            self.assertLess(0, len(result))
            for result in await asyncio.gather(
                *(VideoDownloader(id).get_video_frames() for id in self.video_ids),
            )
        ]
