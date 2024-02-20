from yt_dlp import YoutubeDL
from PIL import Image
from io import BytesIO
import asyncio
import httpx


class VideoDownloader:
    YT_URL = "https://www.youtube.com/watch?v="
    # It's better to close this when the server exits or crashes
    HTTP_CLIENT = httpx.AsyncClient()
    FRAME_LIMIT = 50

    def __init__(self, video_id):
        self.yt = YoutubeDL()
        self.video_id = video_id
        self.video_info = None
        self.video_storyboard_info = None
        self.video_frames = None
        self.initialized = False

    async def get_video_text_info(self):
        await self._initialize_video_info()

        if self.video_info is None:
            raise VideoDownloaderError

        video_categories = self.video_info["categories"]
        video_text_data = (
            self.video_info["title"] + " " + self.video_info["description"]
        )

        return (video_categories, video_text_data)

    async def get_video_frames(self):
        if self.video_frames is not None:
            return self.video_frames

        await self._initialize_video_info()

        if self.video_storyboard_info is None:
            raise VideoDownloaderError

        sb_rows = self.video_storyboard_info["rows"]
        sb_cols = self.video_storyboard_info["columns"]
        num_fragments = len(self.video_storyboard_info["fragments"])
        fragment_step_size = (sb_rows * sb_cols * num_fragments) // self.FRAME_LIMIT

        storyboard_fragments = await asyncio.gather(
            *map(
                self._get_storyboard,
                list(map(lambda x: x["url"], self.video_storyboard_info["fragments"]))[
                    ::fragment_step_size
                ],
            )
        )

        sb_width = self.video_storyboard_info["width"]
        sb_height = self.video_storyboard_info["height"]

        storyboard_frames = await asyncio.gather(
            *[
                asyncio.to_thread(
                    self._extract_frames, sb, sb_cols, sb_rows, sb_width, sb_height
                )
                for sb in storyboard_fragments
            ]
        )

        self.video_frames = [frame for frames in storyboard_frames for frame in frames]
        return self.video_frames

    async def _initialize_video_info(self):
        if self.initialized:
            return

        self.video_info = await asyncio.to_thread(
            self.yt.extract_info, self.video_id, False
        )

        if self.video_info is None:
            raise VideoDownloaderError

        self.video_storyboard_info = list(
            sorted(
                filter(
                    lambda x: "sb" in x["format_id"],
                    self.video_info["formats"],
                ),
                key=lambda x: x["format_id"],
            )
        )[0]

        self.initialized = True

    @staticmethod
    async def _get_storyboard(url):
        return Image.open(BytesIO((await VideoDownloader.HTTP_CLIENT.get(url)).content))

    @staticmethod
    def _extract_frames(storyboard, cols, rows, width, height):
        frames = []

        for row in range(rows):
            for col in range(cols):
                frames.append(
                    storyboard.crop(
                        (
                            width * col,
                            height * row,
                            width * (col + 1),
                            height * (row + 1),
                        )
                    )
                )

        return frames


class VideoDownloaderError(Exception):
    pass
