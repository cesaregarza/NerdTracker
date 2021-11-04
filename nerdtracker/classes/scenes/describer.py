from typing import Dict, Tuple, Union
import pathlib
import cv2
import numpy as np
import numpy.typing as npt

base_path = pathlib.Path(__file__).parent
def construct_path(path: str) -> str:
    return str( (base_path / path).resolve())


class SceneDescriber:
    def __init__(self, resolution                   :Union[Tuple[int, int], Dict[str, int]], 
                       player_list_limits           :Union[Tuple[int, int, int, int], Dict[str, int]],
                       space_between_players        :int,
                       lobby_image_limits           :Union[Tuple[int, int, int, int], Dict[str, int]],
                       frames_per_second            :int,
                       lobby_image_path             :str,
                       mouse_icon_path              :str,
                       controller_icon_path         :str,
                       lobby_image_multiplier       :float = 1.0,
                       mouse_icon_multiplier        :float = 1.0,
                       controller_icon_multiplier   :float = 1.0,
                       **kwargs) -> None:
        """Object that holds all the information about the scene.

        Args:
            resolution (Union[Tuple[int, int], Dict[str, int]]): Resolution of the monitor.
            player_list_limits (Union[Tuple[int, int, int, int], Dict[str, int]]): The top, right, bottom, left coordinates of the player list in pixels.
            space_between_players (int): The space between players in pixels.
            lobby_image_limits (Union[Tuple[int, int, int, int], Dict[str, int]]): The top, right, bottom, left coordinates of where to search for the lobby image in pixels.
            frames_per_second (int): The frames per second of the scene.
            lobby_image_path (str): The path to the lobby image, can be a relative path or an absolute path.
            mouse_icon_path (str): The path to the mouse icon, can be a relative path or an absolute path.
            controller_icon_path (str): The path to the controller icon, can be a relative path or an absolute path.
            lobby_image_multiplier (float, optional): Size multiplier for icon. Defaults to 1.0.
            mouse_icon_multiplier (float, optional): Size multiplier for icon. Defaults to 1.0.
            controller_icon_multiplier (float, optional): Size multiplier for icon. Defaults to 1.0.
        """
        
        #Parse inputs and save them
        if isinstance(resolution, tuple):
            self.width  = resolution[0]
            self.height = resolution[1]
        else:
            self.width  = resolution['width']
            self.height = resolution['height']
        
        if isinstance(player_list_limits, tuple):
            self.player_list_top    = player_list_limits[0]
            self.player_list_right  = player_list_limits[1]
            self.player_list_bottom = player_list_limits[2]
            self.player_list_left   = player_list_limits[3]
        else:
            self.player_list_top    = player_list_limits['top']
            self.player_list_right  = player_list_limits['right']
            self.player_list_bottom = player_list_limits['bottom']
            self.player_list_left   = player_list_limits['left']
        
        
        if isinstance(lobby_image_limits, tuple):
            self.lobby_image_top    = lobby_image_limits[0]
            self.lobby_image_right  = lobby_image_limits[1]
            self.lobby_image_bottom = lobby_image_limits[2]
            self.lobby_image_left   = lobby_image_limits[3]
        else:
            self.lobby_image_top    = lobby_image_limits['top']
            self.lobby_image_right  = lobby_image_limits['right']
            self.lobby_image_bottom = lobby_image_limits['bottom']
            self.lobby_image_left   = lobby_image_limits['left']

        self.frames_per_second      = frames_per_second

        icon_paths = {
            'lobby_image':      {'path': lobby_image_path,     
                                 'multiplier': lobby_image_multiplier},
            'mouse_icon':       {'path': mouse_icon_path,
                                 'multiplier': mouse_icon_multiplier},
            'controller_icon':  {'path': controller_icon_path,
                                 'multiplier': controller_icon_multiplier}
        }
        self.icon_paths = {}

        for key, value in icon_paths.items():
            self.icon_paths[key] = {'multiplier': value['multiplier'],}
            if not pathlib.Path(value['path']).is_absolute():
                self.icon_paths[key]['path'] = construct_path(value['path'])
            else:
                self.icon_paths[key]['path'] = value['path']
        
        self.space_between_players      = space_between_players

        #Calculate widths and heights
        self.player_list_width  = self.player_list_right - self.player_list_left
        self.player_list_height = self.player_list_bottom - self.player_list_top
        self.lobby_image_width  = self.lobby_image_right - self.lobby_image_left
        self.lobby_image_height = self.lobby_image_bottom - self.lobby_image_top
    
    def _get_icon(self, icon_path: str, icon_multiplier: float) -> np.ndarray:
        """Get the icon from the path.

        Args:
            icon_path (str): The path to the icon.
            icon_multiplier (float): The size multiplier for the icon.

        Returns:
            npt.ndarray: The icon.
        """
        icon = cv2.imread(icon_path, cv2.IMREAD_GRAYSCALE)
        icon = cv2.resize(icon, (0, 0), fx=icon_multiplier, fy=icon_multiplier)
        return icon

    def get_lobby_icon(self) -> np.ndarray:
        """Get the lobby icon.

        Returns:
            npt.ndarray: The lobby icon.
        """
        return self._get_icon(self.icon_paths['lobby_image']['path'], self.icon_paths['lobby_image']['multiplier'])
    
    def get_mouse_icon(self) -> np.ndarray:
        """Get the mouse icon.

        Returns:
            npt.ndarray: The mouse icon.
        """
        return self._get_icon(self.icon_paths['mouse_icon']['path'], self.icon_paths['mouse_icon']['multiplier'])
    
    def get_controller_icon(self) -> np.ndarray:
        """Get the controller icon.

        Returns:
            npt.ndarray: The controller icon.
        """
        return self._get_icon(self.icon_paths['controller_icon']['path'], self.icon_paths['controller_icon']['multiplier'])
    

    def get_lobby_limits(self) -> Tuple[int, int, int, int]:
        """Get the lobby limits.

        Returns:
            Tuple[int, int, int, int]: The lobby limits.
        """
        return self.lobby_image_top, self.lobby_image_right, self.lobby_image_bottom, self.lobby_image_left

    def get_player_list_limits(self) -> Tuple[int, int, int, int]:
        """Get the player list limits.

        Returns:
            Tuple[int, int, int, int]: The player list limits.
        """
        return self.player_list_top, self.player_list_right, self.player_list_bottom, self.player_list_left