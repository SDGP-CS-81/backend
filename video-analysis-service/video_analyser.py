import cv2
import statistics
import asyncio
import numpy


class VideoAnalyser:
    def __init__(self, video_frames):
        self.video_frames = video_frames
        self.frame_edge_maps = []
        self.frame_diff_maps = []
        self.filtered_frame_data = []
        self.video_detail_score = None
        self.video_diff_score = None
        self.selected_frame = None

    async def calculate_scores(self):
        result = await asyncio.to_thread(self._calculate_scores)
        # await asyncio.to_thread(self._save_to_disk)

        return result

    def _save_to_disk(self):
        for f_idx in range(len(self.filtered_frame_data)):
            self.filtered_frame_data[f_idx][2].save(f"outputs/{f_idx}.webp")
            cv2.imwrite(
                f"outputs/{f_idx}_edgemap.webp", self.filtered_frame_data[f_idx][0][0]
            )
            cv2.imwrite(
                f"outputs/{f_idx}_diffmap.webp", self.filtered_frame_data[f_idx][1][0]
            )

    def _calculate_scores(self):
        if self.video_detail_score and self.video_diff_score and self.selected_frame:
            return (self.video_detail_score, self.video_diff_score, self.selected_frame)

        self._generate_edge_maps()
        self._generate_diff_maps()

        diff_sum = list(map(lambda x: x[1], self.frame_diff_maps))
        diff_stdev = statistics.stdev(diff_sum)
        diff_mean = statistics.mean(diff_sum)

        diff_lower_bound = diff_mean - diff_stdev
        diff_upper_bound = diff_mean + diff_stdev

        self.filtered_frame_data = list(
            filter(
                lambda x: x[1][1] <= diff_upper_bound and x[1][1] >= diff_lower_bound,
                zip(
                    self.frame_edge_maps,
                    self.frame_diff_maps,
                    self.video_frames,
                ),
            )
        )

        self.filtered_frame_data.sort(key=lambda x: x[1][1])
        selected_data = self.filtered_frame_data[len(self.filtered_frame_data) // 2]
        self.video_detail_score = selected_data[0][1]
        self.video_diff_score = selected_data[1][1]
        self.selected_frame = selected_data[2]

        return (self.video_detail_score, self.video_diff_score, self.selected_frame)

    def _generate_edge_maps(self):
        if len(self.frame_edge_maps) > 0:
            return

        for video_frame in self.video_frames:
            edge_map = cv2.Laplacian(
                cv2.cvtColor(numpy.array(video_frame), cv2.COLOR_RGB2GRAY),
                cv2.CV_64F,
            )

            self.frame_edge_maps.append((edge_map, edge_map.var()))

        edge_var = list(map(lambda x: x[1], self.frame_edge_maps))
        edge_mean = statistics.mean(edge_var)
        edge_stddev = statistics.stdev(edge_var)

        edge_upper_bound = edge_mean + edge_stddev
        edge_lower_bound = edge_mean - edge_stddev

        self.frame_edge_maps = list(
            filter(
                lambda x: x[1] <= edge_upper_bound and x[1] >= edge_lower_bound,
                self.frame_edge_maps,
            )
        )

        self.frame_edge_maps.sort(key=lambda x: x[1])

    def _generate_diff_maps(self):
        if len(self.frame_edge_maps) <= 0:
            raise VideoAnalyserError

        if len(self.frame_diff_maps) > 0:
            return

        ref_frame = self.frame_edge_maps[0][0]

        for edge_map in self.frame_edge_maps:
            diff_map = cv2.absdiff(ref_frame, edge_map[0])

            self.frame_diff_maps.append((diff_map, diff_map.sum()))


class VideoAnalyserError(Exception):
    pass
