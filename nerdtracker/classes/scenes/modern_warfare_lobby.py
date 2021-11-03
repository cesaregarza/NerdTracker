from .scene import Scene
from .describer import SceneDescriber
from typing import Dict, Tuple
import numpy as np

class ModernWarfareScene(Scene):
    def __init__(self, scene_description:SceneDescriber, **kwargs) -> None:
        """Scene for a Modern Warfare lobby

        Args:
            scene_description (SceneDescriber): Scene description
        """
        self.scene_description = scene_description
    
    def check_if_in_lobby(self, screenshot: np.array) -> bool:
        """Checks if the player is in the lobby

        Args:
            screenshot (np.array): Screenshot of the game

        Returns:
            bool: True if the player is in the lobby, False otherwise
        """
