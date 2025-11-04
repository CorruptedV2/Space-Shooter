import pygame
import os
import sys

class MusicMenu:
    def __init__(self, base_path):
        self.base_path = base_path
        self.active = False
        self.selected = 0
        self.music_files = self.get_music_files()

        # Volume system
        self.volume_bars = 10  # 10 bars total
        self.max_bars = 10
        self.volume = 1.0      # Start full volume
        pygame.mixer.music.set_volume(self.volume)

    def get_music_files(self):
        folder = os.path.join(self.base_path, "Music")
        os.makedirs(folder, exist_ok=True)
        return [f for f in os.listdir(folder) if f.endswith(".mp3")]

    def play_music(self, filename):
        path = os.path.join(self.base_path, "Music", filename)
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(-1)

    def toggle(self):
        self.active = not self.active

    def increase_volume(self):
        if self.volume_bars < self.max_bars:
            self.volume_bars += 1
        self.volume = self.volume_bars / self.max_bars
        pygame.mixer.music.set_volume(self.volume)

    def decrease_volume(self):
        if self.volume_bars > 0:
            self.volume_bars -= 1
        self.volume = self.volume_bars / self.max_bars
        pygame.mixer.music.set_volume(self.volume)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                self.toggle()
            elif event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.music_files)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.music_files)
            elif event.key == pygame.K_RETURN and self.music_files:
                self.play_music(self.music_files[self.selected])
            elif event.key == pygame.K_RIGHT:  # Increase volume
                self.increase_volume()
            elif event.key == pygame.K_LEFT:   # Decrease volume
                self.decrease_volume()

    def draw(self, screen, font):
        screen.fill((0, 0, 0))
        title = font.render("Music Menu", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 80))

        for i, file in enumerate(self.music_files):
            color = (0, 255, 0) if i == self.selected else (255, 255, 255)
            text = font.render(f"{i+1}. {file[:-4]}", True, color)
            screen.blit(text, (50, 200 + i * 40))

        # Volume bar display
        vol_text = font.render(f"Volume: {int(self.volume * 100)}%", True, (255, 255, 255))
        screen.blit(vol_text, (50, 500))

        # Draw 10 rectangles as volume bars
        bar_width = 20
        for i in range(self.max_bars):
            color = (0, 255, 0) if i < self.volume_bars else (80, 80, 80)
            pygame.draw.rect(screen, color, (200 + i * (bar_width + 5), 505, bar_width, 20))

        esc_text = font.render("Press ESC or M to go Back", True, (255, 255, 0))
        screen.blit(esc_text, (400 - esc_text.get_width() // 2, 550))
