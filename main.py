#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Make Them Fall
# Copyright (C) 2015  Utkarsh Tiwari
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact information:
# Utkarsh Tiwari    iamutkarshtiwari@gmail.com


import os
import pygame
import pickle
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from sugar3.activity.activity import get_activity_root

from scorescreen import scorewindow
from howtoplay import rules
from settings import settings
from button import Button
from game import Game

disp_width = 600
disp_height = 600

try:
    score_path = os.path.join(get_activity_root(), 'data', 'score.pkl')
except KeyError:
    score_path = '/tmp/score.pkl'

black = (0, 0, 0)
white = (255, 255, 255)


class MakeThemFallGame:

    sound = True

    def __init__(self):
        self.running = True
        self.running_mode = None
        self.clock = pygame.time.Clock()

        self.gameDisplay = None
        self.info = None
        self.offset = [0, 0]
        self.bg_dimensions = [0, 0]

        self.buttons = []

        self.maxscore = [0, 0, 0, 0, 0, 0]

        self.config = {
            "difficulty": 1,
            "muted": False
        }

    def run_game(self, gamenumber, bg_image_path, keymap, border_width=16, type_="spikes"):
        self.running_mode = Game(bg_image_path, keymap, self.config,
                                 border_width=border_width, type_=type_)
        self.running_mode.running = self.running
        score_data = self.running_mode.run()

        if scorewindow(self.gameDisplay, score_data, gamenumber, self).run():
            self.run_game(gamenumber, bg_image_path,
                          keymap, border_width=border_width,
                          type_=type_)

        self.start()

    def show_help(self):
        self.running_mode = rules()
        self.running_mode.running = self.running
        self.running_mode = self.running_mode.run(self.gameDisplay,
                                                  self.bg_dimensions,
                                                  self.offset)

        self.start()

    def show_settings(self):
        self.running_mode = settings()
        self.running_mode.running = self.running
        self.running_mode = self.running_mode.run(self.gameDisplay,
                                                  self.bg_dimensions,
                                                  self.offset,
                                                  self.config)

        self.start()

    def update_highscore(self):
        if os.path.getsize(score_path) > 0:
            with open(score_path, 'rb') as inp:  # Reading
                self.maxscore = pickle.load(inp)

    def vw(self, x):
        return self.offset[0] + (x / 100) * self.bg_dimensions[0]

    def vh(self, y):
        return self.offset[1] + (y / 100) * self.bg_dimensions[1]

    def blit_centre(self, surf, x, y):
        rect = surf.get_rect()
        centered_coords = (x - rect.width // 2, y - rect.height // 2)
        self.gameDisplay.blit(surf, centered_coords)

    def start(self):

        self.gameDisplay = pygame.display.get_surface()

        self.info = pygame.display.Info()

        if not (self.gameDisplay):

            self.gameDisplay = pygame.display.set_mode(
                (self.info.current_w, self.info.current_h))

            pygame.display.set_caption("Make Them Fall")
            gameicon = pygame.image.load('data/images/icon.png')
            pygame.display.set_icon(gameicon)

        self.gameDisplay.fill(black)

        background = pygame.image.load(
            "data/images/welcomescreen/background.png")

        bg_rect = background.get_rect()
        display_rect = self.gameDisplay.get_rect()

        self.offset[0] = (display_rect.width - bg_rect.width) // 2
        self.bg_dimensions = [bg_rect.width, bg_rect.height]

        self.gameDisplay.blit(background, self.offset)

        font_path = "fonts/arial.ttf"
        font_size = 18
        font1 = pygame.font.Font(font_path, font_size)
        font1.set_bold(True)

        if not os.path.exists(score_path):
            open(score_path, 'w+')

        self.update_highscore()

        maxnormal = font1.render("Best: " + str(self.maxscore[0]), True, black)
        maxnightmare = font1.render(
            "Best: " + str(self.maxscore[1]), True, black)
        maxfear = font1.render("Best: " + str(self.maxscore[2]), True, black)
        maxinferno = font1.render(
            "Best: " + str(self.maxscore[3]), True, black)
        maximpossible = font1.render(
            "Best: " + str(self.maxscore[4]), True, black)
        maxcardiac = font1.render(
            "Best: " + str(self.maxscore[5]), True, black)

        button_data = [
            {
                'position': (50, 26),
                'image_path': "data/images/welcomescreen/2pane.png",
                'function': lambda: self.run_game(1, "data/images/2pane.png",
                                                 [[pygame.K_LEFT,
                                                   pygame.K_RIGHT]]),
                'max_score': maxnormal
            },
            {
                'position': (50, 38),
                'image_path': "data/images/welcomescreen/3pane.png",
                'function': lambda: self.run_game(2, "data/images/3pane.png",
                                                 [[pygame.K_LEFT,
                                                   pygame.K_DOWN,
                                                   pygame.K_RIGHT]]),
                'max_score': maxnightmare
            },
            {
                'position': (20, 38),
                'image_path': "data/images/welcomescreen/4pane.png",
                'function': lambda: self.run_game(3, "data/images/4pane.png",
                                                 [[pygame.K_a, pygame.K_d],
                                                  [pygame.K_LEFT,
                                                   pygame.K_RIGHT]]),
                'max_score': maxfear
            },
            {
                'position': (80, 38),
                'image_path': "data/images/welcomescreen/5pane.png",
                'function': lambda: self.run_game(4, "data/images/5pane.png",
                                                 [[pygame.K_a,
                                                   pygame.K_s,
                                                   pygame.K_d],
                                                  [pygame.K_LEFT,
                                                   pygame.K_RIGHT]]),
                'max_score': maxinferno
            },
            {
                'position': (50, 50),
                'image_path': "data/images/welcomescreen/6pane.png",
                'function': lambda: self.run_game(5, "data/images/6pane.png",
                                                 [[pygame.K_a,
                                                   pygame.K_s,
                                                   pygame.K_d],
                                                  [pygame.K_LEFT,
                                                   pygame.K_DOWN,
                                                   pygame.K_RIGHT]]),
                'max_score': maximpossible
            },
            {
                'position': (50, 62),
                'image_path': "data/images/welcomescreen/2paneheart.png",
                'function': lambda: self.run_game(6, "data/images/2pane.png",
                                                 [[pygame.K_LEFT,
                                                   pygame.K_RIGHT]],
                                                 type_="cardiac"),
                'max_score': maxcardiac
            },
            {
                'position': (25, 75),
                'image_path': "data/images/welcomescreen/help.png",
                'function': self.show_help,
                'max_score': None
            },
            {
                'position': (75, 75),
                'image_path': "data/images/welcomescreen/settings.png",
                'function': self.show_settings,
                'max_score': None
            }
        ]

        for button_info in button_data:
            position = button_info['position']
            image_path = button_info['image_path']
            function = button_info['function']
            max_score = button_info['max_score']
            
            x, y = position
            self.buttons.append(Button(self.vw(x), self.vh(y), image_path, function, max_score))

    def run(self):
        self.start()

        while self.running:
            # Gtk events
            while Gtk.events_pending():
                Gtk.main_iteration()
            if not self.running:
                break

            # Pump PyGame messages.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.VIDEORESIZE:
                    pass

            for btn in self.buttons:
                btn.update()

            self.f = 1
            pygame.display.update()
            self.clock.tick(30)

        return


def main():
    pygame.init()
    pygame.display.set_mode((0, 0), pygame.RESIZABLE)
    game = MakeThemFallGame()
    game.run()


if __name__ == "__main__":
    main()
