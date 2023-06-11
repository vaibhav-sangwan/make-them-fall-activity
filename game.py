import pygame
from gi.repository import Gtk
from generator import Generator
from guy import Guy

black = (0, 0, 0)
white = (255, 255, 255)
spawn_spike_event = pygame.USEREVENT + 1


class Game:

    def __init__(self, bg_image_path, keymap, border_width=16, speed=7):
        info = pygame.display.Info()
        self.background = pygame.image.load(bg_image_path)
        self.background = pygame.transform.scale(self.background,
                                                 (600, info.current_h))
        self.border_width = border_width
        self.speed = speed // (len(keymap))

        self.bg_rect = self.background.get_rect()
        self.gameDisplay = pygame.display.get_surface()
        self.display_rect = self.gameDisplay.get_rect()
        self.offset = [0, 0]
        self.offset[0] = (self.display_rect.width - self.bg_rect.width) // 2

        rows = [len(i) for i in keymap]

        pane_coordinates = self.get_pane_coordinates(rows)
        guy_offset = 100 / (1 + (len(rows) - 1))

        # format -> [left spike coords, right spike coords,
        #           path_length, max_spikes]
        spikes_config = []

        pane_height = self.bg_rect.height / len(rows)
        for pane in pane_coordinates:
            spikes_config.append([[pane[0][0], pane[1][1]],
                                  [pane[1][0], pane[1][1]],
                                  pane_height, 4])

        self.generator = Generator()
        self.generator.configure(spikes_config)
        if len(rows) == 1:
            self.generator.generate()

        self.spike_spawn_delay = ((self.display_rect.height / 2)
                                  / self.speed) * 20
        pygame.time.set_timer(spawn_spike_event, int(self.spike_spawn_delay))

        guys_config = []
        self.guys = []

        for pane in pane_coordinates:
            guys_config.append([[pane[0][0], pane[1][0]],
                                pane[0][1] + guy_offset])

        for guy in guys_config:
            self.guys.append(Guy(guy[0], guy[1]))

        # Keys which control each guy (in order of 'guys' array)
        self.keymap = []
        for row in keymap:
            self.keymap += row

        font_path = "fonts/arial.ttf"
        font_size = 50
        self.font1 = pygame.font.Font(font_path, font_size)

        self.score = 0

        self.clock = pygame.time.Clock()
        self.last_spawned = pygame.time.get_ticks()

        self.sounds = {
            "jump": pygame.mixer.Sound("data/sound/jump.wav"),
            "score": pygame.mixer.Sound("data/sound/score.wav"),
            "collide": pygame.mixer.Sound("data/sound/fall.wav")
        }

    def get_pane_coordinates(self, rows):
        coordinates = []
        pane_height = self.bg_rect.height / len(rows)
        for i in range(len(rows)):
            for j in range(rows[i]):
                pane_width = self.bg_rect.width / rows[i]
                origin = [self.offset[0] + pane_width * j, pane_height * i]
                if j > 0 and j <= rows[i] - 1:
                    origin[0] += self.border_width / 2
                end = origin.copy()
                end[0] += pane_width
                end[1] += pane_height
                if (j <= rows[i] - 1):
                    end[0] -= self.border_width / 2
                coordinates.append([origin, end])
        return coordinates  # Array of [top-left coords, bottom-right coords]

    def show_score(self):
        scores = self.font1.render(str(self.score), 1, (0, 0, 0))
        self.gameDisplay.blit(scores, (200 + 650, 30))

    def play_sound(self, sound_name):
        self.sounds[sound_name].play()

    def run(self):
        while self.running:
            # Gtk events
            while Gtk.events_pending():
                Gtk.main_iteration()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                # Manage jumps
                for i, key in enumerate(self.keymap):
                    if event.type == pygame.KEYDOWN and event.key == key:
                        self.play_sound("jump")
                        self.guys[i].move()

            # Assign speed as per score
            self.speed = 7 + self.score // 8
            self.spike_spawn_delay = ((self.display_rect.height / 2)
                                      / self.speed) * 18

            self.gameDisplay.fill(black)
            self.gameDisplay.blit(self.background, self.offset)

            # Generate spikes and increase score
            if self.last_spawned + self.spike_spawn_delay < pygame.time.get_ticks():
                self.generator.generate(self.speed)
                self.score += 1
                self.play_sound("score")
                self.last_spawned = pygame.time.get_ticks()

            self.show_score()

            # updates
            if self.generator.update(self.guys):
                # returns true if player is dead
                return self.score
            for guy in self.guys:
                guy.update()

            pygame.display.update()
            self.clock.tick(60)