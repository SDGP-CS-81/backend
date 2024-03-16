from app.image_classifier import ImageClassifier
from app.logger import setup_logger
from unittest import TestCase
from pathlib import Path
from PIL import Image
import gdown
import shutil
import time

logger = setup_logger(__name__, log_level="DEBUG", log_file=None)


class ImageClassifierTest(TestCase):
    # Time threshold for single image classification
    CLASSIFY_TIME_THRESHOLD_S = 0.5
    # Number of images to test with for batch tests
    BATCH_SIZE = 100
    # Accuracy threshold for BATCH_SIZE number of images
    ACCURACY_THRESHOLD = 0.5

    @classmethod
    def setUpClass(cls):
        logger.info("Set up testing class.")
        logger.info(f"Batch size is {cls.BATCH_SIZE}.")

        dataset_id = "1CEUREAArZWenn7q3FOr9FapwtwaQPvpk"
        dataset_file = Path("dataset.zip")
        cls.dataset_dir = Path("dataset/")

        if not cls.dataset_dir.exists():
            logger.info("Dataset not found on disk.")

            if not (dataset_file.exists() and dataset_file.is_file()):
                logger.info("Dataset archive not found on disk.")
                logger.info("Downloading dataset archive.")

                gdown.download(id=dataset_id, output=str(dataset_file))

            logger.info("Unpacking dataset from archive.")

            shutil.unpack_archive(dataset_file)

        logger.info("Testing class set up completed.")

    def test_classify_image(self):
        """
        Test to see if simple classification gives any output
        """

        logger.info("Starting simple classification test.")

        image = self.dataset_dir.glob("*/*.png").__next__()
        result = ImageClassifier().classify_frame(Image.open(image))

        for category in result:
            self.assertLess(
                0, result[category], "Expected all category weights to be populated!"
            )

        logger.info("Simple classification test passed.")

    def test_classify_speed(self):
        """
        Test to check the speed of a single classification
        """

        logger.info("Starting classification speed test.")

        image = Image.open(self.dataset_dir.glob("*/*.png").__next__())

        start = time.time()
        ImageClassifier().classify_frame(image)
        total_time = time.time() - start

        logger.info(f"Classification time: {total_time}s")

        self.assertGreaterEqual(
            self.CLASSIFY_TIME_THRESHOLD_S, total_time, "Prediction time is too long!"
        )

        logger.info("Classification test passed.")

    def test_classify_speed_batch(self):
        """
        Test to check speed of multiple classifications
        """

        logger.info("Starting batched classification test.")

        total_times = []

        for image in (
            Image.open(image)
            for image in list(self.dataset_dir.glob("*/*.png"))[: self.BATCH_SIZE]
        ):
            start = time.time()
            ImageClassifier().classify_frame(image)
            total_time = time.time() - start
            total_times.append(total_time)

        batch_total_time = sum(total_times)

        logger.info(f"Batch classification time: {batch_total_time}s")

        self.assertGreaterEqual(
            self.CLASSIFY_TIME_THRESHOLD_S * self.BATCH_SIZE,
            batch_total_time,
            "Batch prediction time is too long!",
        )

        logger.info("Batch classification test passed.")

    def test_classify_accuracy_batch(self):
        """
        Test to check the overrall accuracy of the model
        """

        logger.info("Starting batch accuracy test.")

        correct_classifications_count = 0

        category_dirs = list(self.dataset_dir.glob("*/"))

        for category_dir in category_dirs:
            for image in list(category_dir.glob("*.png"))[
                : self.BATCH_SIZE // len(category_dirs)
            ]:
                result = ImageClassifier().classify_frame(Image.open(image))

                highest_score = 0
                highest_category = ""

                for category in result:
                    if result[category] > highest_score:
                        highest_score = result[category]
                        highest_category = category

                if (
                    highest_category.lower()
                    in category_dir.name.replace("_", "").lower()
                ):
                    correct_classifications_count += 1

        total_accuracy = self.BATCH_SIZE / correct_classifications_count

        logger.info(f"Batch classification accuracy: {total_accuracy * 100}%")

        self.assertLessEqual(
            self.ACCURACY_THRESHOLD,
            total_accuracy,
            "Model accuracy is less than expected!",
        )

        logger.info("Batch accuracy test passed.")
