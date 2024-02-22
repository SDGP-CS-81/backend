from yt_dlp import YoutubeDL
from PIL import Image
from io import BytesIO
import asyncio
import httpx


class VideoDownloader:
    """
    A class used to download frame and text data for a YouTube video

    ...

    Attributes
    ----------
    YT_URL : str
        a base url string that is used when making requests
    HTTP_CLIENT : httpx.AsyncClient
        a client object for making async requests
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

    Methods
    -------
    get_video_text_info() -> ([str], str)
        gets and returns the YT categories and description text for a video
    get_video_frames() -> [PIL.Image.Image]
        gets and returns the individual frames from a video storyboard,
        or the thumbnails for the video
    """

    YT_URL = "https://www.youtube.com/watch?v="
    # It's better to close this when the server exits or crashes
    HTTP_CLIENT = httpx.AsyncClient()
    FRAME_LIMIT = 50
    DEFAULT_FRAME_SIZE = (1280, 720)

    def __init__(self, video_id):
        """
        Parameters
        ----------
        video_id : str
            a valid YouTube video id
        """

        self.yt = YoutubeDL()
        self.video_id = video_id
        self.video_info = None
        self.video_storyboard_info = None
        self.video_frames = None
        self.is_live = False

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

        await self._initialize_video_info()

        if self.video_info is None:
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

        if self.video_frames is not None:
            return self.video_frames

        # Ensure the required fields are populated
        await self._initialize_video_info()

        # If the video is live we fallback to using thumbnails as our frames
        if self.is_live:
            frames = await self._get_thumbnail_frames()
        else:
            frames = await self._get_storyboard_frames()

        return frames

    async def _get_thumbnail_frames(self):
        if self.video_info is None:
            raise VideoDownloaderError

        thumbnail_urls = [
            thumb_info["url"]
            for thumb_info in self.video_info["thumbnails"]
            # Don't use thumbnails with a very low preference score
            # These thumbnails usually just use a gray placeholder
            # and mess up the detail and diff calculations
            if thumb_info["preference"] > -10
        ]

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

        return resized_frames

    async def _get_storyboard_frames(self):
        if self.video_storyboard_info is None:
            raise VideoDownloaderError

        sb_rows = self.video_storyboard_info["rows"]
        sb_cols = self.video_storyboard_info["columns"]
        num_fragments = len(self.video_storyboard_info["fragments"])
        # Approximately limit the amount of frames downloaded to FRAME_LIMIT
        fragment_step_size = (sb_rows * sb_cols * num_fragments) // self.FRAME_LIMIT

        # Get all storyboard images asynchronously
        storyboard_fragments = (
            result  # Get the other images even if one fails
            for result in await asyncio.gather(
                *(
                    self._get_image_from_url(url)
                    for url in list(
                        map(lambda x: x["url"], self.video_storyboard_info["fragments"])
                    )[::fragment_step_size]
                ),
                return_exceptions=True,  # Don't stop gather if a task fails
            )
            if isinstance(result, Image.Image)  # Filter out exceptions
        )

        sb_width = self.video_storyboard_info["width"]
        sb_height = self.video_storyboard_info["height"]

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
        # and cache the result
        self.video_frames = [frame for frames in storyboard_frames for frame in frames]
        return self.video_frames

    async def _initialize_video_info(self):
        # Skip if the object has already been initialized
        if self.video_info and (self.video_storyboard_info or self.is_live):
            return

        # Asynchronously get the video info with yt_dlp
        # We have to do it another thread because yt_dlp doesn't have
        # async methods for these operations
        self.video_info = await asyncio.to_thread(
            self.yt.extract_info, self.video_id, False
        )

        # Check that we actually managed to download the info
        if self.video_info is None:
            raise VideoDownloaderError

        # Don't attempt to get storyboard info if it's a live video
        if self.video_info["is_live"]:
            self.is_live = True
            return

        # Get only the storyboard streams and sort them by the highest quality
        # storyboard, which is usually sb0
        self.video_storyboard_info = list(
            sorted(
                filter(
                    # Only get the storyboard streams
                    lambda x: "sb" in x["format_id"],
                    self.video_info["formats"],
                ),
                key=lambda x: x["format_id"],
            )
        )[0]

    @staticmethod
    async def _get_image_from_url(url):
        # We have to use BytesIO cause PIL refuses to create an image otherwise
        return Image.open(BytesIO((await VideoDownloader.HTTP_CLIENT.get(url)).content))

    @staticmethod
    def _extract_frames(storyboard, cols, rows, width, height):
        frames = []

        for row in range(rows):
            for col in range(cols):
                frames.append(
                    storyboard.crop(
                        (
                            width * col,  # Left coordinate
                            height * row,  # Upper
                            width * (col + 1),  # Right
                            height * (row + 1),  # Lower
                        )
                    )
                )

        return frames


class VideoDownloaderError(Exception):
    pass
