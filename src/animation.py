"""Reusable time-based sprite-sheet animation; rows contain equal-sized cells."""
import pygame


class SpriteAnimation:
    def __init__(self, path, frame_size, clips):
        sheet = pygame.image.load(str(path)).convert_alpha()
        width, height = frame_size
        if sheet.get_width() % width or sheet.get_height() % height:
            raise ValueError('Sprite sheet dimensions must be multiples of frame size')
        self.clips = {}
        self.intervals = {}
        for name, (row, columns, fps) in clips.items():
            if fps <= 0 or not columns:
                raise ValueError('Animation needs frames and a positive frame rate')
            frames = [sheet.subsurface((column*width, row*height, width, height)).copy()
                      for column in columns]
            self.clips[name] = {1: frames, -1: [pygame.transform.flip(f, True, False) for f in frames]}
            self.intervals[name] = 1.0/fps
        self.state = None
        self.elapsed = 0.0

    def frame(self, state, dt, facing=1):
        if state != self.state:
            self.state = state
            self.elapsed = 0.0
        else:
            self.elapsed += max(0.0, dt)
        frames = self.clips[state][facing]
        return frames[int(self.elapsed/self.intervals[state]) % len(frames)]
