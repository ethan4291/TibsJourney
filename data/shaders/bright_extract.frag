#version 330

uniform sampler2D scene;
in vec2 uv;
out vec4 frag_color;

void main() {
    vec3 color = texture(scene, uv).rgb;
    float brightness = dot(color, vec3(0.2126, 0.7152, 0.0722));
    float threshold = 0.62;
    float knee = 0.25;
    float soft = clamp(brightness - threshold + knee, 0.0, 2.0 * knee);
    soft = (soft * soft) / (4.0 * knee + 0.0001);
    float contribution = max(soft, brightness - threshold);
    contribution = max(contribution, 0.0);
    frag_color = vec4(color * contribution, 1.0);
}
