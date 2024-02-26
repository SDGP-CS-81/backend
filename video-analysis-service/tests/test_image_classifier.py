from app.image_classifier import ImageClassifier
from unittest import TestCase
from pathlib import Path
from PIL import Image
import gdown
import shutil
import time


class ImageClassifierTest(TestCase):
    # Time threshold for single image classification
    CLASSIFY_TIME_THRESHOLD_S = 0.5
    # Number of images to test with for batch tests
    BATCH_SIZE = 100
    # Accuracy threshold for BATCH_SIZE number of images
    ACCURACY_THRESHOLD = 0.5

    @classmethod
    def setUpClass(cls):
        dataset_id = "1ne623_uXIf_XEUuHJGHmNMynSP27qd5c"
        dataset_file = Path("dataset.zip")
        cls.dataset_dir = Path("dataset/")

        if not cls.dataset_dir.exists():
            if not (dataset_file.exists() and dataset_file.is_file()):
                gdown.download(id=dataset_id, output=str(dataset_file))

            shutil.unpack_archive(dataset_file)

    def test_classify_image(self):
        """
        Test to see if simple classification gives any output
        """

        image = self.dataset_dir.glob("*/*.png").__next__()
        result = ImageClassifier().classify_frame(Image.open(image))

        for category in result:
            self.assertLess(
                0, result[category], "Expected all category weights to be populated!"
            )

    def test_classify_speed(self):
        """
        Test to check the speed of a single classification
        """

        image = Image.open(self.dataset_dir.glob("*/*.png").__next__())

        start = time.time()
        result = ImageClassifier().classify_frame(image)
        total_time = time.time() - start

        self.assertGreaterEqual(
            self.CLASSIFY_TIME_THRESHOLD_S, total_time, "Prediction time is too long!"
        )

    def test_classify_speed_batch(self):
        """
        Test to check speed of multiple classifications
        """

        total_times = []

        for image in (
            Image.open(image)
            for image in list(self.dataset_dir.glob("*/*.png"))[: self.BATCH_SIZE]
        ):
            start = time.time()
            result = ImageClassifier().classify_frame(image)
            total_time = time.time() - start
            total_times.append(total_time)

        batch_total_time = sum(total_times)

        print(batch_total_time)
        self.assertGreaterEqual(
            self.CLASSIFY_TIME_THRESHOLD_S * self.BATCH_SIZE,
            batch_total_time,
            "Batch prediction time is too long!",
        )

    def test_classify_accuracy_batch(self):
        """
        Test to check the overrall accuracy of the model
        """

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

        print(total_accuracy)
        self.assertLessEqual(
            self.ACCURACY_THRESHOLD,
            total_accuracy,
            "Model accuracy is less than expected!",
        )
