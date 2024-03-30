from yt_dlp import YoutubeDL
import asyncio
import httpx
from app.logger import setup_logger

logger = setup_logger(
    __name__, log_level="DEBUG", log_file="video-analysis-service.log"
)


class VideoDownloader:
    """
    A class used to download text data for a YouTube video

    ...

    Attributes
    ----------
    HTTP_TIMEOUT : int
        a network timeout that is used when getting frames,
        keep this at a reasonable level to allow for slow sources
        without letting it get too long
    yt : YoutubeDL
        a yt_dlp object that is used for retrieving data from YouTube
    video_id : str
        a valid YouTube video id, this is just the id part and not the url
    video_info : dict
        a dictionary populated with various datapoints about a video
    is_live : boolean
        indicates if the current video is detected as an ongoing livestream
    http_client : httpx.AsyncClient
        a client object for making async requests

    Methods
    -------
    get_video_text_info() -> ([str], str)
        gets and returns the YT categories and description text for a video
    """

    HTTP_TIMEOUT = 20

    def __init__(self, video_id):
        """
        Parameters
        ----------
        video_id : str
            a valid YouTube video id
        """

        logger.info(f"Initializing VideoDownloader for video ID: {video_id}")

        self.yt = YoutubeDL()
        self.video_id = video_id
        self.video_info = None
        self.is_live = False
        # It's better to close this when the server exits or crashes
        self.http_client = httpx.AsyncClient(timeout=self.HTTP_TIMEOUT)

    async def get_video_text_info(self):
        """
        Gets and returns the YT categories and description text for a video

        May raise an exception if the information could not be retrieved

        Parameters
        ----------
        None

        Returns
        -------
        ([str], str)

        Raises
        ------
        VideoDownloaderError
        """

        logger.info("Retrieving video text information.")
        await self._initialize_video_info()

        if self.video_info is None:
            logger.error("Failed to retrieve video information.")
            raise VideoDownloaderError

        video_categories = self.video_info["categories"]
        video_text_data = (
            self.video_info["title"] + " " + self.video_info["description"]
        )

        return (video_categories, video_text_data)

    async def close_http_connections(self):
        logger.debug("Closing HTTP connections.")
        await self.http_client.aclose()

    async def _initialize_video_info(self):
        # Skip if the object has already been initialized
        if self.video_info and self.is_live:
            logger.debug(
                "Video information already initialized, skipping initialization."
            )
            return

        logger.debug("Initializing video information.")
        # Asynchronously get the video info with yt_dlp
        # We have to do it another thread because yt_dlp doesn't have
        # async methods for these operations
        self.video_info = await asyncio.to_thread(
            self.yt.extract_info, self.video_id, False
        )

        # Check that we actually managed to download the info
        if self.video_info is None:
            logger.error("Failed to retrieve video information.")
            raise VideoDownloaderError

        # Don't attempt to get storyboard info if it's a live video
        if self.video_info["is_live"]:
            logger.info("Video is a live stream.")
            self.is_live = True
            return

        # logger.debug("Retrieving video storyboard information.")
        # # Get only the storyboard streams and sort them by the highest quality
        # # storyboard, which is usually sb0
        # self.video_storyboard_info = sorted(
        #     (
        #         # Only get the storyboard streams
        #         x
        #         for x in self.video_info["formats"]
        #         if "sb" in x["format_id"]
        #     ),
        #     key=lambda x: x["format_id"],
        # )[0]

class VideoDownloaderError(Exception):
    pass
