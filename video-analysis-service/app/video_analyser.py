import cv2
import statistics
import asyncio
import numpy
import re
from app.logger import setup_logger
from app.keywords import STATIC_KEYWORDS

logger = setup_logger(
    __name__, log_level="DEBUG", log_file="video-analysis-service.log"
)


class VideoAnalyser:
    """
    A class used to analyze both frame and text data

    ...

    Attributes
    ----------
    DIFF_SCORE_RANGE: (int, int)
        the expected range of scores for image diffing
    DETAIL_SCORE_RANGE: (int, int)
        the expected range of scores for image detail
    video_frames: [PIL.Image.Image]
        a list of frames that are being analysed
    frame_edge_maps: [(cv2.MatLike, int)]
        a list of tuples that contain both an edge map and
        the corresponding detail score (variance)
    frame_diff_maps: [(cv2.MatLike, int)]
        a list of tuples that contain both a diff map and
        the corresponding diff score (sum of absolute diff)
    filtered_frame_data: [((cv2.MatLike, int), (cv2.MatLike, int), PIL.Image.Image)]
        a list that contains the final filtered form of all the data, this list aggregates
        all the appropriate datapoints into one tuple
    video_detail_score: int
        the final detail score for the video
    video_diff_score: int
        the final diff score for the video (approximately the amount of motion)
    selected_frame: PIL.Image.Image
        the image that corresponds to the detail and diff scores

    Methods
    -------
    calculate_text_scores(str, {str: [str]}) -> {str: int}
        takes in the description text for a video and the keyword mappings
        for categories, and returns a map of the category and the scores
    calculate_frame_scores() -> (int, int, PIL.Image.Image)
        returns the detail score, diff score and the selected image as a tuple
    """

    DIFF_SCORE_RANGE = (0, 2_000_000)
    DETAIL_SCORE_RANGE = (0, 2_000)

    def __init__(self, video_frames):
        """
        Parameters
        ----------
        video_frames : [PIL.Image.Image]
            a list of frames to be analysed
        """
        logger.info(f"Initializing VideoAnalyser with {len(video_frames)} frames.")
        self.video_frames = video_frames
        self.frame_edge_maps = []
        self.frame_diff_maps = []
        self.filtered_frame_data = []
        self.video_detail_score = None
        self.video_diff_score = None
        self.selected_frame = None

    async def calculate_frame_scores(self):
        logger.debug("Calculating frame scores...")
        """
        Analyses the given frames and returns the detail and diff scores,
        as well as the selected frames

        Parameters
        ----------
        None

        Returns
        -------
        (int, int, PIL.Image.Image)
        """
        result = await asyncio.to_thread(self._calculate_frame_scores)
        # Uncomment the below lines to dump the analysed data onto disk
        # await asyncio.to_thread(self._save_to_disk)

        return result

    @staticmethod
    def calculate_text_scores(video_text_data, keywords):
        """
        Calculates the text scores when given some text data and
        a map of categories and keywords

        Parameters
        ----------
        video_text_data: str
            the text that will be searched for keywords
        keywords: {str: [str]}
            a map of categories to keywords

        Returns
        -------
        {str: int}
            a map of categories to their keyword occurence scores
        """
        logger.info("Calculating text scores.")
        return {
            key: len(  # Use the number of non-zero keyword hits as the score
                [
                    score
                    for score in (
                        len(  # Get the number of occurences
                            re.findall(
                                # Match each keyword
                                # ensuring it has either space or punctuation
                                # around it
                                re.compile(
                                    f"\\W{value}\\W", re.MULTILINE + re.IGNORECASE
                                ),
                                video_text_data,
                            )
                        )
                        for value in keywords[key]
                    )
                    if score > 0  # Filter out any keywords that didn't have occurences
                ]
            )
            for key in keywords.keys()
        }

    @staticmethod
    def merge_keywords(category_keywords):
        # Merge static and client keywords
        if category_keywords is None:
            merged_keys_dict = STATIC_KEYWORDS
        else:
            merged_keys_dict = category_keywords | STATIC_KEYWORDS
            client_keys = category_keywords.keys()
            static_keys = STATIC_KEYWORDS.keys()

            for key in merged_keys_dict.keys():
                if key in client_keys and key in static_keys:
                    merged_keys_dict[key] = (
                        category_keywords[key] + STATIC_KEYWORDS[key]
                    )
                elif key in client_keys:
                    merged_keys_dict[key] = category_keywords[key]
                elif key in static_keys:
                    merged_keys_dict[key] = STATIC_KEYWORDS[key]

        return merged_keys_dict

    @staticmethod
    def yt_categorization_check(video_category, text_scores):
        # Hack to use YT category to boost score and exit early
        # This should be synchronized with the frontend
        if "music" in video_category[0].lower():
            text_scores["music"] = 1000
            logger.debug("Video category is music. Returning response data early.")
            return True
        elif "gaming" in video_category[0].lower():
            text_scores["gaming"] = 1000
            logger.debug("Video category is gaming. Returning response data early.")
            return True

        return False

    def _save_to_disk(self):
        if self.selected_frame:
            logger.debug("Saving selected frame to disk.")
            self.selected_frame.save("selected_frame.webp")

        for f_idx in range(len(self.filtered_frame_data)):
            logger.debug(f"Saving frame {f_idx} to disk.")
            self.filtered_frame_data[f_idx][2].save(f"outputs/{f_idx}.webp")
            cv2.imwrite(
                f"outputs/{f_idx}_edgemap.webp", self.filtered_frame_data[f_idx][0][0]
            )
            cv2.imwrite(
                f"outputs/{f_idx}_diffmap.webp", self.filtered_frame_data[f_idx][1][0]
            )

    def _calculate_frame_scores(self):
        logger.debug("Calculating frame scores.")
        # Return cached values if available
        if self.video_detail_score and self.video_diff_score and self.selected_frame:
            return (self.video_detail_score, self.video_diff_score, self.selected_frame)

        # These must be called in this order prior to doing anything else
        self._generate_edge_maps()
        self._generate_diff_maps()

        # Get the stdev and mean of the diff scores in order to filter outliers
        diff_sum = [x[1] for x in self.frame_diff_maps]
        diff_stdev = statistics.stdev(diff_sum)
        diff_mean = statistics.mean(diff_sum)

        diff_lower_bound = diff_mean - diff_stdev
        diff_upper_bound = diff_mean + diff_stdev

        self.filtered_frame_data = sorted(
            (
                x
                # Keep the data together before filtering
                for x in zip(
                    self.frame_edge_maps,
                    self.frame_diff_maps,
                    self.video_frames,
                )
                # Filter the outliers
                if x[1][1] <= diff_upper_bound and x[1][1] >= diff_lower_bound
            ),
            key=lambda x: x[1][1],
        )

        # Pick the median
        selected_data = self.filtered_frame_data[len(self.filtered_frame_data) // 2]
        self.video_detail_score = selected_data[0][1]
        self.video_diff_score = selected_data[1][1]
        self.selected_frame = selected_data[2]

        # Normalize frame scores
        self.video_diff_score = self._normalize_value_in_range(
            self.video_diff_score, self.DIFF_SCORE_RANGE
        )

        self.video_detail_score = self._normalize_value_in_range(
            self.video_detail_score, self.DETAIL_SCORE_RANGE
        )

        logger.debug(
            f"Calculated frame scores: detail_score={self.video_detail_score}, diff_score={self.video_diff_score}"
        )
        return (self.video_detail_score, self.video_diff_score, self.selected_frame)

    @staticmethod
    def _normalize_value_in_range(value, value_range):
        clamped_value = min(value_range[1], value)
        clamped_value = max(value_range[0], clamped_value)

        return (clamped_value - value_range[0]) / value_range[1] - value_range[0]

    def _generate_edge_maps(self):
        # Skip if we already have generated edge_maps
        if len(self.frame_edge_maps) > 0:
            logger.debug("Edge maps already generated, skipping generation.")
            return

        logger.debug("Generating edge maps.")
        self.frame_edge_maps = sorted(
            (
                (edge_map, edge_map.var())
                for edge_map in (
                    # Generate edge maps using the laplacian operator
                    cv2.Laplacian(
                        # Load the PIL image as a grayscale opencv matrix
                        cv2.cvtColor(numpy.array(video_frame), cv2.COLOR_RGB2GRAY),
                        cv2.CV_64F,
                    )
                    for video_frame in self.video_frames
                )
            ),
            key=lambda x: x[1],
        )

        # Stuff needed to filter outliers
        edge_var = [x[1] for x in self.frame_edge_maps]
        edge_mean = statistics.mean(edge_var)
        edge_stddev = statistics.stdev(edge_var)

        edge_upper_bound = edge_mean + edge_stddev
        edge_lower_bound = edge_mean - edge_stddev

        self.frame_edge_maps = [
            x
            for x in self.frame_edge_maps
            # Filter outliers
            if x[1] <= edge_upper_bound and x[1] >= edge_lower_bound
        ]
        logger.info(f"Generated {len(self.frame_edge_maps)} edge maps.")

    def _generate_diff_maps(self):
        logger.debug("Generating diff maps.")
        # We need the edge maps to be already generated
        # before we can do the diff maps
        if len(self.frame_edge_maps) <= 0:
            logger.error("Edge maps not generated. Cannot generate diff maps.")
            raise VideoAnalyserError

        # Skip generation if we already have the maps cached
        if len(self.frame_diff_maps) > 0:
            logger.debug("Diff maps already generated, skipping generation.")
            return

        # Use the highest detail edge map
        # The gen edge map function should always return
        # the maps sorted by detail level
        ref_frame = self.frame_edge_maps[0][0]

        self.frame_diff_maps = [
            (diff_map, diff_map.sum())
            for diff_map in (
                # Getting the absolute difference map
                cv2.absdiff(ref_frame, edge_map[0])
                for edge_map in self.frame_edge_maps
            )
        ]
        logger.info(f"Generated {len(self.frame_diff_maps)} diff maps.")


class VideoAnalyserError(Exception):
    pass
