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
    Methods
    -------
    calculate_text_scores(str, {str: [str]}) -> {str: int}
        takes in the description text for a video and the keyword mappings
        for categories, and returns a map of the category and the scores
    """

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

class VideoAnalyserError(Exception):
    pass
