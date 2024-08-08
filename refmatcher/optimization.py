# TODO: think about using scikit-optimize optimizers. Bayesian optimization could be interesting. https://scikit-opt.github.io/scikit-opt/#/en/README

import bpy
from bpy.types import Image, Context
from abc import ABC, abstractmethod
from refmatcher import properties, matching_variables

from refmatcher import dependencies, image_comparison
dependencies_ok = dependencies.check_dependencies()
if not dependencies_ok:
    dependencies.install_dependencies() # TODO: if kept this way, delete the install_dependencies call from operators.py and the HMI code.
import scipy.optimize as opt
import numpy as np

# TODO: real time visualisation. See https://blender.stackexchange.com/q/141121/185343
class Optimizer(ABC):
    def __init__(self, channel: str, distance: str, reference_image: Image, iterations: int, context: Context):
        self.channel = channel
        self.distance = distance
        self.reference_image = reference_image
        self.iterations = iterations
        self.context = context

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
        print(f"x: {x}, result: {result}")
        return result

    @abstractmethod
    def optimize(self) -> opt.OptimizeResult:
        raise NotImplementedError()

class DifferentialEvolutionOptimizer(Optimizer):
    def callback(self, intermediate_result: opt.OptimizeResult):
        print(f"Intermediate result: {intermediate_result}")

    def optimize(self) -> opt.OptimizeResult:
        x0, bounds = self.initial_parameters()
        population_multiplier = 15
        generations = max(self.iterations // (len(bounds) * population_multiplier), 1)
        print(f"Starting differential evolution optimization. Target call to evaluation function: {self.iterations}, with population size {len(bounds) * population_multiplier} and {generations} generations.")
        result = opt.differential_evolution(self.evaluate, bounds, maxiter=generations, popsize=population_multiplier, disp=True, x0=x0, callback=self.callback)
        print(f"Optimization finished.\n{result}")
        return result

class DualAnnealingOptimizer(Optimizer):
    def optimize(self) -> opt.OptimizeResult:
        x0, bounds = self.initial_parameters()
        print(f"Starting dual annealing optimization. Target call to evaluation function: {self.iterations}.")
        result = opt.dual_annealing(self.evaluate, bounds, maxfun=self.iterations, x0=x0)
        print(f"Optimization finished.\n{result}")
        return result


OPTIMIZER_BY_NAME = {
    'DIFFERENTIAL_EVOLUTION': DifferentialEvolutionOptimizer,
    'DUAL_ANNEALING': DualAnnealingOptimizer,
}