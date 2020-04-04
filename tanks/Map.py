
import kivy
from kivy.app import App
from kivy.lang import Builder

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from random import random, randint
from kivy.graphics import Color, Ellipse, Line, Rectangle

from pathlib import Path
import os

from kivy.graphics import Mesh
from functools import partial
from math import cos, sin, pi

from statistics import mean
from HallOfFame import HallOfFameScreen
from Menu import MenuScreen
from Point import Point

import numpy as np

import kivy.clock

class MapWidget(Widget):
    map_segments_count = 300
    map_edge_tank_padding = 25
    min_tank_mutual_distance = 25

    def clear(self):
        self.canvas.clear()

    def generate_terrain(self):
        self.scene = self.parent.parent
        self._generate_surface()
        self._regenerate_mesh()     

    def generate_tanks_positions(self, number_of_tanks):
        positions = []

        for _ in range(number_of_tanks):
            while True:
                # generate random position and check whether it is distant enought from all other
                position = randint(MapWidget.map_edge_tank_padding, MapWidget.map_segments_count - MapWidget.map_edge_tank_padding)
                if all(map(lambda other_position: abs(position - other_position) > MapWidget.min_tank_mutual_distance, positions)):
                    break
            positions.append(position)

        # translate segment position to pixels
        positions_in_map = list(map(lambda x_index: Point(self._position_index_to_pixels(x_index), self.surface_y[x_index]), positions))
        return positions_in_map

    def _generate_surface(self):
        self.surface = []
        self.surface_x = []
        self.surface_y = []

        # initial (left) point of surface
        surface_height = random() * 0.4 + 0.3 # (0.3 - 0.7)
        # controls slope (height change) to the next terrain segment
        steepness = 0

        for i in range(MapWidget.map_segments_count):
            # revert steepness if it is too high/low
            if surface_height > 0.8 or surface_height < 0.2:
                steepness *= -0.1
            # add random noise
            steepness += np.random.normal() / 2000
            # steer direction towards the middle
            steepness += (0.5 - surface_height) / 500
            # clip (for lower hills)
            steepness = np.clip(steepness, -0.005, 0.005)

            surface_height = surface_height + steepness
            x_pixels = self._position_index_to_pixels(i)
            surface_height_pixels = self.scene.float_y_to_pixels(surface_height)

            self.surface.append(Point(x_pixels, surface_height_pixels))
            self.surface_x.append(x_pixels)
            self.surface_y.append(surface_height_pixels)

    def _regenerate_mesh(self):
        vertices = []
        indices = []

        scene = self.scene

        for i in range(MapWidget.map_segments_count):
            x, y = self.surface[i]
            # surface point
            vertices.extend([int(x), int(y), 0, 0])
            # map bottom point
            vertices.extend([int(x), int(0), 0, 0])

        min_x = scene.float_x_to_pixels(0)
        min_y = scene.float_y_to_pixels(0)
        max_x = scene.float_x_to_pixels(1)
        max_y = scene.float_y_to_pixels(1)
        # corners to make it polygonal fill of widget under surface
        vertices.extend([max_x, scene.float_y_to_pixels(random()), 0, 0])
        vertices.extend([max_x, min_y, 0, 0])
        vertices.extend([max_x, min_y, 0, 0])
        vertices.extend([min_x, min_y, 0, 0])

        indices = list(range(MapWidget.map_segments_count*2 + 4))

        with self.canvas.before:
            # blue sky
            Color(0.4, 0.9, 1)
            self.mesh = Mesh(vertices=[min_x,min_y,0,0 ,min_x,max_y,0,0 ,max_x,max_y,0,0 , max_x,min_y,0,0], indices=[0,1,2,3], mode='triangle_fan')
        with self.canvas:
            # green terrain
            Color(0.2, 0.85, 0.3)
            self.mesh = Mesh(vertices=vertices, indices=indices, mode='triangle_strip') 
            

    def _position_index_to_pixels(self, index):
        return self.scene.float_x_to_pixels(index / (MapWidget.map_segments_count - 1))
