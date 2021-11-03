from typing import Dict, Tuple, Union
import pathlib

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

        #Check if paths are absolute, if not, make them absolute
        if not pathlib.Path(lobby_image_path).is_absolute():
            self.lobby_image_path = construct_path(lobby_image_path)
        else:
            self.lobby_image_path = lobby_image_path

        if not pathlib.Path(mouse_icon_path).is_absolute():
            self.mouse_icon_path = construct_path(mouse_icon_path)
        else:
            self.mouse_icon_path = mouse_icon_path
        
        if not pathlib.Path(controller_icon_path).is_absolute():
            self.controller_icon_path = construct_path(controller_icon_path)
        else:
            self.controller_icon_path = controller_icon_path
        
        self.lobby_image_multiplier     = lobby_image_multiplier
        self.mouse_icon_multiplier      = mouse_icon_multiplier
        self.controller_icon_multiplier = controller_icon_multiplier
        self.space_between_players      = space_between_players

        #Calculate widths and heights
        self.player_list_width  = self.player_list_right - self.player_list_left
        self.player_list_height = self.player_list_bottom - self.player_list_top
        self.lobby_image_width  = self.lobby_image_right - self.lobby_image_left
        self.lobby_image_height = self.lobby_image_bottom - self.lobby_image_top