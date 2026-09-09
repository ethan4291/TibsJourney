#version 330

uniform sampler2D image;
uniform bool horizontal;
uniform vec2 texel_size;
in vec2 uv;
out vec4 frag_color;

const float weights[5] = float[](0.2270270270, 0.1945945946, 0.1216216216, 0.0540540541, 0.0162162162);

void main() {
    vec3 result = texture(image, uv).rgb * weights[0];
    vec2 dir = horizontal ? vec2(texel_size.x, 0.0) : vec2(0.0, texel_size.y);
    for (int i = 1; i < 5; i++) {
        result += texture(image, uv + dir * float(i)).rgb * weights[i];
        result += texture(image, uv - dir * float(i)).rgb * weights[i];
    }
    frag_color = vec4(result, 1.0);
}
