import bpy
from bpy.types import Image
import numpy as np
import os


def rendered_image(render_path: str) -> Image:
    # TODO: refactor to avoid saving and loading rendered image. See if https://blender.stackexchange.com/a/248543 can be updated for 4.0 (bgl is deprecated)
    filename = "render.png"
    filepath = os.path.join(render_path, "render.png")
    render_result = next(image for image in bpy.data.images if image.type == "RENDER_RESULT")
    # must save then load render, since render.pixels is empty otherwise
    render_result.save_render(filepath)
    if filename in bpy.data.images:
        bpy.data.images.remove(bpy.data.images[filename])
    return bpy.data.images.load(filepath, check_existing=True)

def image_to_matrix(image: Image) -> np.ndarray:
    pixels = np.array(image.pixels[:])
    return pixels.reshape(image.size[1], image.size[0], 4)


# histogram functions

def histogram(a: np.ndarray) -> np.ndarray:
    resolution = 256
    return np.histogram(a, bins=resolution, range=(0, 1), density=True)[0] / resolution

def red_histogram(image: np.ndarray) -> np.ndarray:
    return histogram(image[:, :, 0])

def green_histogram(image: np.ndarray) -> np.ndarray:
    return histogram(image[:, :, 1])

def blue_histogram(image: np.ndarray) -> np.ndarray:
    return histogram(image[:, :, 2])

def luminance_histogram(image: np.ndarray) -> np.ndarray:
    luminance = 0.2126 * image[:, :, 0] + 0.7152 * image[:, :, 1] + 0.0722 * image[:, :, 2] # TODO: check if this is correct
    return histogram(luminance)

HISTOGRAM_FUNCTIONS_BY_CHANNEL = {
    'RED': {red_histogram},
    'GREEN': {green_histogram},
    'BLUE': {blue_histogram},
    'RGB': {red_histogram, green_histogram, blue_histogram},
    'LUMINANCE': {luminance_histogram}
}


# distance functions

def bhattacharyya_distance(histogram1: np.ndarray, histogram2: np.ndarray) -> float:
    bhattacharyya_coefficient = np.sum(np.sqrt(histogram1 * histogram2))
    return -np.log(bhattacharyya_coefficient) if bhattacharyya_coefficient > 0 else np.inf

def earth_movers_distance(histogram1: np.ndarray, histogram2: np.ndarray) -> float:
    assert len(histogram1) == len(histogram2)
    diff_array = histogram1 - histogram2
    cumulative_sum = np.cumsum(diff_array)
    absolute_cumulative_sum = np.abs(cumulative_sum)
    emd_output = np.sum(absolute_cumulative_sum) / (len(histogram1) - 1)
    return emd_output

DISTANCE_FUNCTIONS_BY_NAME = {
    'BHATTACHARYYA': bhattacharyya_distance,
    'EARTH_MOVERS': earth_movers_distance
}


# comparison function

def compare_images(image1: Image, image2: Image, channel: str, distance: str) -> float:
    """
    Compare two images based on specified channels and distance function.

    Args:
        image1 (Image): The first image to compare.
        image2 (Image): The second image to compare.
        channel (str): The channel to use for comparison.
        distance (str): The distance to use for comparison.

    Returns:
        float: The distance value between the two images.

    """
    matrix1 = image_to_matrix(image1)
    matrix2 = image_to_matrix(image2)

    distance_function = DISTANCE_FUNCTIONS_BY_NAME[distance]

    distance_values = []
    for histogram_function in HISTOGRAM_FUNCTIONS_BY_CHANNEL[channel]:
        histogram1 = histogram_function(matrix1)
        histogram2 = histogram_function(matrix2)

        distance_values.append(distance_function(histogram1, histogram2))

    return np.mean(distance_values)