"""Lightweight particle system for game-juice effects (dust, sparkles)."""

import random

import pygame


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "radius", "gravity", "fade")

    def __init__(self, x, y, vx, vy, life, color, radius, gravity=0.0, fade=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.radius = radius
        self.gravity = gravity
        self.fade = fade

    def update(self, dt):
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surface, camera_x, camera_y):
        t = max(0.0, self.life / self.max_life)
        radius = max(1, round(self.radius * (t if self.fade else 1.0)))
        alpha = round(255 * t)
        size = radius * 2
        particle_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (*self.color, alpha), (radius, radius), radius)
        surface.blit(particle_surface, (round(self.x - camera_x - radius), round(self.y - camera_y - radius)))


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def spawn_dust(self, x, y, count=8):
        for _ in range(count):
            angle_spread = random.uniform(-1.0, 1.0)
            speed = random.uniform(40, 120)
            vx = angle_spread * speed
            vy = -random.uniform(20, 70)
            life = random.uniform(0.25, 0.5)
            shade = random.randint(200, 235)
            self.particles.append(
                Particle(x, y, vx, vy, life, (shade, shade - 15, shade - 40), random.uniform(2, 4), gravity=260)
            )

    def spawn_sparkles(self, x, y, color, count=16):
        for _ in range(count):
            angle = random.uniform(0, 6.2832)
            speed = random.uniform(60, 220)
            vx = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).x
            vy = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).y
            life = random.uniform(0.35, 0.75)
            self.particles.append(Particle(x, y, vx, vy, life, color, random.uniform(2, 5), gravity=140))

    def spawn_landing_dust(self, x, y, intensity):
        self.spawn_dust(x, y, count=min(16, max(4, round(intensity * 14))))

    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface, camera_x, camera_y):
        for particle in self.particles:
            particle.draw(surface, camera_x, camera_y)
