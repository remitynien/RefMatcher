# TODO: think about using scikit-optimize optimizers. Bayesian optimization could be interesting. https://scikit-opt.github.io/scikit-opt/#/en/README

import bpy
from bpy.types import Image
from abc import ABC, abstractmethod

from refmatcher import dependencies, image_comparison
exposed_success = dependencies.expose_module("scipy")
if not exposed_success:
    dependencies.install_dependencies() # TODO: if kept this way, delete the install_dependencies call from operators.py and the HMI code.
    dependencies.expose_module("scipy")
import scipy.optimize as opt
import numpy as np

# TODO: real time visualisation. See https://blender.stackexchange.com/q/141121/185343
class Optimizer(ABC):
    def __init__(self, channel: str, distance: str, reference_image: Image, iterations: int):
        self.channel = channel
        self.distance = distance
        self.reference_image = reference_image
        self.iterations = iterations

    def evaluate(self, x: np.ndarray):
        # TODO: update blender properties with x
        bpy.ops.render.render(write_still=True)
        rendered_image = image_comparison.rendered_image()
        result = image_comparison.compare_images(self.reference_image, rendered_image, self.channel, self.distance)
        return result

    @abstractmethod
    def optimize(self):
        pass

class DifferentialEvolutionOptimizer(Optimizer):
    def callback(self, intermediate_result: opt.OptimizeResult):
        print(f"Intermediate result: {intermediate_result}")

    def optimize(self):
        # TODO: proper bounds and x0
        bounds = [(0, 1)] * 4
        population_multiplier = 15
        generations = max(self.iterations // (len(bounds) * population_multiplier), 1)
        print(f"Starting differential evolution optimization. Target call to evaluation function: {self.iterations}, with population size {len(bounds) * population_multiplier} and {generations} generations.")
        result = opt.differential_evolution(self.evaluate, bounds, maxiter=generations, popsize=population_multiplier, disp=True, x0=np.random.rand(4), callback=self.callback)
        print(f"Optimization result: {result}")
        return result

class DualAnnealingOptimizer(Optimizer):
    def optimize(self):
        # TODO: proper bounds and x0
        bounds = [(0, 1)] * 4
        print(f"Starting dual annealing optimization. Target call to evaluation function: {self.iterations}.")
        result = opt.dual_annealing(self.evaluate, bounds, maxfun=self.iterations, x0=np.random.rand(4))
        print(f"Optimization result: {result}")
        return result


OPTIMIZER_BY_NAME = {
    'DIFFERENTIAL_EVOLUTION': DifferentialEvolutionOptimizer,
    'DUAL_ANNEALING': DualAnnealingOptimizer,
}