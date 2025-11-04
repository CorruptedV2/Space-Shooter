# Boss2_AI.py
import random
import math
import pygame

WIDTH, HEIGHT = 800, 600  # You can import these dynamically later

class Boss2AI:
    """Reactive AI for Boss2:
       - Dodges incoming player bullets
       - Fires predictive shots
    """
    def __init__(self, rect, width=WIDTH, height=HEIGHT):
        self.rect = rect.copy()
        self.move_speed = 4
        self.vx = random.choice([-1, 1]) * self.move_speed
        self.vy = random.choice([-1, 1]) * int(self.move_speed * 0.75)
        self.fire_cooldown = 90
        self.fire_timer = 0
        self.dodge_cooldown = 10
        self.dodge_timer = 0
        self.bullet_speed = 7
        self.width = width
        self.height = height

    def update(self, player_positions, player_vels, player_rects, player_enabled, player_bullets_lists):
        """Call each frame"""
        self.dodge_timer = max(0, self.dodge_timer - 1)

        dodge_x, dodge_y = 0, 0
        danger_threshold_time = 60

        # --- Dodge incoming bullets ---
        for blist in player_bullets_lists:
            for b in blist:
                bx, by = b.centerx, b.centery
                bvx, bvy = 0, -12  # player bullet speed assumption
                if bvy == 0:
                    continue
                t = (self.rect.centery - by) / bvy
                if 0 < t < danger_threshold_time:
                    pred_x = bx + bvx * t
                    margin = max(30, self.rect.width // 2)
                    if self.rect.left - margin <= pred_x <= self.rect.right + margin:
                        dodge_x += 1 if pred_x < self.rect.centerx else -1
                        dodge_y += random.choice([-1, 1])
                        break
            if dodge_x or dodge_y:
                break

        if (dodge_x or dodge_y) and self.dodge_timer == 0:
            self.vx = (dodge_x / abs(dodge_x)) * self.move_speed if dodge_x else self.vx
            self.vy = (dodge_y / abs(dodge_y)) * int(self.move_speed * 0.75) if dodge_y else self.vy
            self.dodge_timer = self.dodge_cooldown

        # --- Movement ---
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

        if self.rect.left <= 0 or self.rect.right >= self.width:
            self.vx *= -1
        if self.rect.top <= 0 or self.rect.bottom >= self.height:
            self.vy *= -1

        # --- Firing logic ---
        self.fire_timer += 1
        shots = []
        if self.fire_timer >= self.fire_cooldown:
            self.fire_timer = 0
            targets = [0] if player_enabled == 1 else [0, 1]
            for tidx in targets:
                p_pos = player_positions[tidx]
                p_vel = player_vels[tidx]
                if p_pos is None:
                    continue

                dx = p_pos[0] - self.rect.centerx
                dy = p_pos[1] - self.rect.centery
                dist = math.hypot(dx, dy)
                predict_frames = max(6, int(dist / (self.bullet_speed * 2)))

                pred_x = p_pos[0] + p_vel[0] * predict_frames
                pred_y = p_pos[1] + p_vel[1] * predict_frames
                pred_x = max(0, min(self.width, pred_x))
                pred_y = max(0, min(self.height, pred_y))

                ang = math.atan2(pred_y - self.rect.centery, pred_x - self.rect.centerx)
                vx = math.cos(ang) * self.bullet_speed
                vy = math.sin(ang) * self.bullet_speed
                shots.append((self.rect.centerx, self.rect.centery, vx, vy))

                offset_ang = ang + math.radians(10)
                vx2 = math.cos(offset_ang) * self.bullet_speed
                vy2 = math.sin(offset_ang) * self.bullet_speed
                shots.append((self.rect.centerx, self.rect.centery, vx2, vy2))

                if player_enabled == 1:
                    break
        return shots
