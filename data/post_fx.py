"""moderngl-based post-processing pipeline: bloom, chromatic aberration,
vignette, film grain and screen-shake/flash reactive wobble.

The game is drawn as usual onto a normal software pygame.Surface each frame.
That surface is uploaded as a texture and run through a small GPU pipeline,
then the result is drawn to the real (OpenGL) display surface.
"""

import array
import os

import moderngl
import pygame

SHADER_DIR = os.path.join(os.path.dirname(__file__), "shaders")


def _read_shader(name):
    with open(os.path.join(SHADER_DIR, name), "r") as shader_file:
        return shader_file.read()


class PostFX:
    def __init__(self, width, height, bloom_scale=0.5, blur_passes=6):
        self.width = width
        self.height = height
        self.ctx = moderngl.create_context()

        self.time = 0.0
        self.shake_trauma = 0.0
        self.flash = 0.0

        self.aberration_strength = 0.0016
        self.vignette_strength = 0.35
        self.grain_strength = 0.035
        self.bloom_strength = 0.7
        self.blur_passes = blur_passes

        quad = array.array(
            "f",
            [
                -1.0, -1.0, 0.0, 0.0,
                 1.0, -1.0, 1.0, 0.0,
                -1.0,  1.0, 0.0, 1.0,
                 1.0,  1.0, 1.0, 1.0,
            ],
        )
        self.quad_vbo = self.ctx.buffer(quad.tobytes())

        self.scene_texture = self._make_target(width, height)

        bloom_w = max(1, int(width * bloom_scale))
        bloom_h = max(1, int(height * bloom_scale))
        self.bloom_size = (bloom_w, bloom_h)
        self.bright_texture = self._make_target(bloom_w, bloom_h)
        self.bright_fbo = self.ctx.framebuffer(color_attachments=[self.bright_texture])
        self.ping_textures = [self._make_target(bloom_w, bloom_h) for _ in range(2)]
        self.ping_fbos = [self.ctx.framebuffer(color_attachments=[tex]) for tex in self.ping_textures]

        self.extract_program = self._load_program("quad.vert", "bright_extract.frag")
        self.blur_program = self._load_program("quad.vert", "blur.frag")
        self.final_program = self._load_program("quad.vert", "final.frag")

        self.extract_vao = self.ctx.vertex_array(
            self.extract_program, [(self.quad_vbo, "2f 2f", "in_pos", "in_uv")]
        )
        self.blur_vao = self.ctx.vertex_array(
            self.blur_program, [(self.quad_vbo, "2f 2f", "in_pos", "in_uv")]
        )
        self.final_vao = self.ctx.vertex_array(
            self.final_program, [(self.quad_vbo, "2f 2f", "in_pos", "in_uv")]
        )

    def _make_target(self, w, h):
        texture = self.ctx.texture((w, h), 4)
        texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
        texture.repeat_x = False
        texture.repeat_y = False
        return texture

    def _load_program(self, vert_name, frag_name):
        return self.ctx.program(
            vertex_shader=_read_shader(vert_name),
            fragment_shader=_read_shader(frag_name),
        )

    def add_shake(self, amount):
        self.shake_trauma = min(1.0, self.shake_trauma + amount)

    def add_flash(self, amount=1.0):
        self.flash = min(1.0, self.flash + amount)

    def update(self, dt):
        self.time += dt
        self.shake_trauma = max(0.0, self.shake_trauma - dt * 2.2)
        self.flash = max(0.0, self.flash - dt * 3.2)

    def render(self, surface):
        pixel_data = pygame.image.tostring(surface, "RGBA", True)
        self.scene_texture.write(pixel_data)

        # Bright-pass extract at reduced resolution.
        self.bright_fbo.use()
        self.ctx.viewport = (0, 0, *self.bloom_size)
        self.scene_texture.use(location=0)
        self.extract_program["scene"] = 0
        self.extract_vao.render(moderngl.TRIANGLE_STRIP)

        # Ping-pong separable gaussian blur.
        read_texture = self.bright_texture
        for i in range(self.blur_passes):
            target_fbo = self.ping_fbos[i % 2]
            target_fbo.use()
            self.ctx.viewport = (0, 0, *self.bloom_size)
            read_texture.use(location=0)
            self.blur_program["image"] = 0
            self.blur_program["horizontal"] = (i % 2 == 0)
            self.blur_program["texel_size"] = (1.0 / self.bloom_size[0], 1.0 / self.bloom_size[1])
            self.blur_vao.render(moderngl.TRIANGLE_STRIP)
            read_texture = self.ping_textures[i % 2]

        # Final composite straight to the window.
        self.ctx.screen.use()
        self.ctx.viewport = (0, 0, self.width, self.height)
        self.scene_texture.use(location=0)
        read_texture.use(location=1)
        self.final_program["scene"] = 0
        self.final_program["bloom"] = 1
        self.final_program["time"] = self.time
        self.final_program["shake"] = self.shake_trauma
        self.final_program["flash"] = self.flash
        self.final_program["aberration_strength"] = self.aberration_strength
        self.final_program["vignette_strength"] = self.vignette_strength
        self.final_program["grain_strength"] = self.grain_strength
        self.final_program["bloom_strength"] = self.bloom_strength
        self.final_vao.render(moderngl.TRIANGLE_STRIP)
