from yt_dlp import YoutubeDL
from PIL import Image
from io import BytesIO
import asyncio
import httpx
from app.logger import setup_logger

logger = setup_logger(
    __name__, log_level="DEBUG", log_file="video-analysis-service.log"
)


class VideoDownloader:
    """
    A class used to download frame and text data for a YouTube video

    ...

    Attributes
    ----------
    HTTP_TIMEOUT : int
        a network timeout that is used when getting frames,
        keep this at a reasonable level to allow for slow sources
        without letting it get too long
    FRAME_LIMIT : int
        a loosely followed upper limit for the amount of frames downloaded
    DEFAULT_FRAME_SIZE : (int, int)
        a default size to normalize uneven shaped frame sequences,
        only used for ensuring thumbnails are similarly sized
    yt : YoutubeDL
        a yt_dlp object that is used for retrieving data from YouTube
    video_id : str
        a valid YouTube video id, this is just the id part and not the url
    video_info : dict
        a dictionary populated with various datapoints about a video
    video_storyboard_info : dict
        a dictionary populated with information and urls for a video storyboard
    video_frames : [PIL.Image.Image]
        a list of frames for a given video
    is_live : boolean
        indicates if the current video is detected as an ongoing livestream
    http_client : httpx.AsyncClient
        a client object for making async requests

    Methods
    -------
    get_video_text_info() -> ([str], str)
        gets and returns the YT categories and description text for a video
    get_video_frames() -> [PIL.Image.Image]
        gets and returns the individual frames from a video storyboard,
        or the thumbnails for the video
    """

    HTTP_TIMEOUT = 20
    FRAME_LIMIT = 50
    DEFAULT_FRAME_SIZE = (1280, 720)

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
        self.video_storyboard_info = None
        self.video_frames = None
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

    async def get_video_frames(self):
        """
        Gets and returns all the frames from a video storyboard or the video thumbnails

        The number of returned images can be loosely clamped with FRAME_LIMIT
        May raise an exception if the information could not be retrieved

        Parameters
        ----------
        None

        Returns
        -------
        [PIL.Image.Image]

        Raises
        ------
        VideoDownloaderError
        """

        logger.info("Retrieving video frames.")

        if self.video_frames is not None:
            logger.debug("Returning cached video frames.")
            return self.video_frames

        # Ensure the required fields are populated
        await self._initialize_video_info()

        # If the video is live we fallback to using thumbnails as our frames
        if self.is_live:
            logger.debug("Video is live, retrieving thumbnail frames.")
            frames = await self._get_thumbnail_frames()
        else:
            logger.debug("Retrieving storyboard frames.")
            frames = await self._get_storyboard_frames()

        return frames

    async def close_http_connections(self):
        logger.debug("Closing HTTP connections.")
        await self.http_client.aclose()

    async def _get_thumbnail_frames(self):
        if self.video_info is None:
            logger.error("Failed to retrieve video information.")
            raise VideoDownloaderError

        thumbnail_urls = (
            thumb_info["url"]
            for thumb_info in self.video_info["thumbnails"]
            # Don't use thumbnails with a very low preference score
            # These thumbnails usually just use a gray placeholder
            # and mess up the detail and diff calculations
            if thumb_info["preference"] > -10
        )

        logger.debug("Downloading thumbnail frames.")
        # Asynchronously get all the thumbnails
        frames = (
            result  # Get the other images even if one fails
            for result in await asyncio.gather(
                *(self._get_image_from_url(url) for url in thumbnail_urls),
                return_exceptions=True,  # Don't cancel the gather op if a task fails
            )
            if isinstance(result, Image.Image)  # Filter out the exception objects
        )

        # Thumbnails could come in different resolutions
        # Resize them so that they are all consistent
        resized_frames = [frame.resize(self.DEFAULT_FRAME_SIZE) for frame in frames]
        logger.info(f"Retrieved {len(resized_frames)} thumbnail frames.")
        return resized_frames

    async def _get_storyboard_frames(self):
        if self.video_storyboard_info is None:
            logger.error("Failed to retrieve video storyboard information.")
            raise VideoDownloaderError

        sb_rows = self.video_storyboard_info["rows"]
        sb_cols = self.video_storyboard_info["columns"]
        num_fragments = len(self.video_storyboard_info["fragments"])
        # Approximately limit the amount of frames downloaded to FRAME_LIMIT
        fragment_step_size = (sb_rows * sb_cols * num_fragments) // self.FRAME_LIMIT

        logger.debug("Downloading storyboard fragments.")
        # Get all storyboard images asynchronously
        storyboard_fragments = (
            result  # Get the other images even if one fails
            for result in await asyncio.gather(
                *(
                    self._get_image_from_url(url)
                    for url in [
                        x["url"] for x in self.video_storyboard_info["fragments"]
                    ][::fragment_step_size]
                ),
                return_exceptions=True,  # Don't stop gather if a task fails
            )
            if isinstance(result, Image.Image)  # Filter out exceptions
        )

        sb_width = self.video_storyboard_info["width"]
        sb_height = self.video_storyboard_info["height"]

        logger.debug("Extracting frames from storyboard fragments.")
        # Extract all the frames from the storyboards asynchronously
        storyboard_frames = await asyncio.gather(
            *(
                asyncio.to_thread(
                    self._extract_frames, sb, sb_cols, sb_rows, sb_width, sb_height
                )
                for sb in storyboard_fragments
            )
        )

        # Flatten the resulting [[Image, ...], ...] array into a [Image, ...] array
        self.video_frames = [frame for frames in storyboard_frames for frame in frames]
        logger.info(f"Retrieved {len(self.video_frames)} storyboard frames.")
        return self.video_frames

    async def _initialize_video_info(self):
        # Skip if the object has already been initialized
        if self.video_info and (self.video_storyboard_info or self.is_live):
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

        logger.debug("Retrieving video storyboard information.")
        # Get only the storyboard streams and sort them by the highest quality
        # storyboard, which is usually sb0
        self.video_storyboard_info = sorted(
            (
                # Only get the storyboard streams
                x
                for x in self.video_info["formats"]
                if "sb" in x["format_id"]
            ),
            key=lambda x: x["format_id"],
        )[0]

    async def _get_image_from_url(self, url):
        logger.debug(f"Downloading image from URL: {url}")
        # We have to use BytesIO cause PIL refuses to create an image otherwise
        return Image.open(BytesIO((await self.http_client.get(url)).content))

    @staticmethod
    def _extract_frames(storyboard, cols, rows, width, height):
        return [
            storyboard.crop(
                (
                    width * col,  # Left
                    height * row,  # Upper
                    width * (col + 1),  # Right
                    height * (row + 1),  # Lower
                )
            )
            for row in range(rows)
            for col in range(cols)
        ]


class VideoDownloaderError(Exception):
    pass
