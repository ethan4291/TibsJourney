#version 330

uniform sampler2D scene;
uniform sampler2D bloom;
uniform float time;
uniform float shake;
uniform float flash;
uniform float aberration_strength;
uniform float vignette_strength;
uniform float grain_strength;
uniform float bloom_strength;

in vec2 uv;
out vec4 frag_color;

float rand(vec2 co) {
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
    vec2 centered = uv - 0.5;

    vec2 wobble = vec2(sin(time * 41.0 + uv.y * 22.0), cos(time * 37.0 + uv.x * 22.0)) * shake * 0.0045;
    vec2 sample_uv = uv + wobble;

    float ab = aberration_strength * (0.35 + shake * 1.6 + length(centered) * 0.7);
    vec2 dir = length(centered) > 0.0001 ? normalize(centered) : vec2(0.0);
    float r = texture(scene, sample_uv - dir * ab).r;
    float g = texture(scene, sample_uv).g;
    float b = texture(scene, sample_uv + dir * ab).b;
    vec3 color = vec3(r, g, b);

    vec3 bloom_color = texture(bloom, sample_uv).rgb;
    color += bloom_color * bloom_strength;

    // Soft highlight roll-off so hot spots (sun, bloom, flashes) compress
    // gracefully instead of clipping into a flat blinding white patch.
    color = color / (1.0 + color * 0.6) * 1.35;

    float vignette = smoothstep(0.95, 0.25, length(centered) * (1.0 + vignette_strength));
    color *= mix(1.0, vignette, vignette_strength * 1.6);

    float grain = (rand(uv * fract(time) * 400.0 + time) - 0.5) * grain_strength;
    color += grain;

    color = mix(color, vec3(1.0), clamp(flash, 0.0, 1.0) * 0.85);

    float luma = dot(color, vec3(0.299, 0.587, 0.114));
    color = mix(vec3(luma), color, 1.12);
    color = (color - 0.5) * 1.04 + 0.5;

    frag_color = vec4(clamp(color, 0.0, 1.0), 1.0);
}
