# TODO: think about using scikit-optimize optimizers. Bayesian optimization could be interesting. https://scikit-opt.github.io/scikit-opt/#/en/README

import bpy
from bpy.types import Image, Context
from abc import ABC, abstractmethod
from refmatcher import properties, matching_variables, server

from refmatcher import dependencies, image_comparison
dependencies_ok = dependencies.check_dependencies()
if not dependencies_ok:
    dependencies.install_dependencies() # TODO: if kept this way, delete the install_dependencies call from operators.py and the HMI code.
import scipy.optimize as opt
import numpy as np
import csv
import os

CSV_PATH = os.path.join(bpy.app.tempdir, "progress.csv")

class Optimizer(ABC):
    def __init__(self, channel: str, distance: str, reference_image: Image, iterations: int, context: Context):
        self.channel = channel
        self.distance = distance
        self.reference_image = reference_image
        self.iterations = iterations
        self.context = context
        self.current_iteration = 0
        self.server = None
        self.scores = []

    def initial_parameters(self) -> tuple[list[float], list[tuple[float, float]]]:
        x0: list[float] = []
        bounds: list[tuple[float, float]] = []
        for matching_property in getattr(self.context.scene, properties.MATCHING_PROPERTIES_PROPNAME):
            datablock, data_path_indexed = matching_property.datablock, matching_property.data_path_indexed
            min, max = matching_property.minimum, matching_property.maximum
            value = matching_variables.get_value(datablock, data_path_indexed)
            x0.append(value)
            bounds.append((min, max))
        return x0, bounds

    def evaluate(self, x: np.ndarray) -> float:
        matching_variables.set_matching_values(self.context, x)
        bpy.ops.render.render(write_still=True)
        rendered_image = image_comparison.rendered_image()
        result = image_comparison.compare_images(self.reference_image, rendered_image, self.channel, self.distance)
        self.current_iteration += 1
        self.scores.append(result)
        self.update_csv_file()
        self.context.window_manager.progress_update(self.current_iteration)
        print(f"x: {x}, result: {result}")
        return result

    def update_csv_file(self):
        # TODO: think about opening the file each time vs opening it once, and closing it after optimize is done
        with open(CSV_PATH, 'w', newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.scores)

    def optimize(self) -> opt.OptimizeResult:
        self.current_iteration = 0
        self.server = server.OptimizeViewServer(8000, CSV_PATH) # TODO: add addon parameter with default port
        self.scores = []
        self.update_csv_file()
        result = self._run_optimize_algorithm()
        self.server.shutdown()
        self.server = None
        return result

    @abstractmethod
    def _run_optimize_algorithm(self) -> opt.OptimizeResult:
        raise NotImplementedError()

class DifferentialEvolutionOptimizer(Optimizer):
    def callback(self, intermediate_result: opt.OptimizeResult):
        print(f"Intermediate result: {intermediate_result}")

    def _run_optimize_algorithm(self) -> opt.OptimizeResult:
        x0, bounds = self.initial_parameters()
        population_multiplier = 15
        generations = max(self.iterations // (len(bounds) * population_multiplier), 1)
        print(f"Starting differential evolution optimization. Target call to evaluation function: {self.iterations}, with population size {len(bounds) * population_multiplier} and {generations} generations.")
        self.context.window_manager.progress_begin(0, len(bounds) * population_multiplier * generations)
        result = opt.differential_evolution(self.evaluate, bounds, maxiter=generations, popsize=population_multiplier, disp=True, x0=x0, callback=self.callback)
        self.context.window_manager.progress_end()
        print(f"Optimization finished.\n{result}")
        return result

class DualAnnealingOptimizer(Optimizer):
    def _run_optimize_algorithm(self) -> opt.OptimizeResult:
        x0, bounds = self.initial_parameters()
        print(f"Starting dual annealing optimization. Target call to evaluation function: {self.iterations}.")
        self.context.window_manager.progress_begin(0, self.iterations)
        result = opt.dual_annealing(self.evaluate, bounds, maxfun=self.iterations, x0=x0)
        self.context.window_manager.progress_end()
        print(f"Optimization finished.\n{result}")
        return result


OPTIMIZER_BY_NAME = {
    'DIFFERENTIAL_EVOLUTION': DifferentialEvolutionOptimizer,
    'DUAL_ANNEALING': DualAnnealingOptimizer,
}