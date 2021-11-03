from abc import ABC, abstractmethod
import numpy as np
from .describer import SceneDescriber

class Scene(ABC):
    @abstractmethod
    def __init__(self, scene_limits:SceneDescriber) -> None:
        pass

    @abstractmethod
    def read_each_line(self, input) -> list:
        pass
    
    @abstractmethod
    def check_if_in_lobby(self, screenshot: np.array) -> bool:
        pass