#version 330 core
out vec4 FragColor;

in vec2 TexCoord;

uniform float time;
uniform int numBubbles;
uniform vec2 bubblePositions[125];
uniform float bubbleStrengths[125];
uniform vec3 bubbleColors[125];
uniform vec2 resolution;

float metaball(vec2 pos, vec2 center, float strength) {
    float dist = distance(pos, center);
    return strength / (dist * dist + 0.1);
    // Función de caída que caracteriza a la metaball, inversamente proporcional a su distancia
}

void main()
{
    vec2 pos = TexCoord * resolution;
    float value = 0.0; // Acumulará el efecto de todas las metaball en ese píxel
    
    // Encontrar burbuja dominante
    int dominantIndex = -1;
    float maxMetaballValue = 0.0;

    for (int i = 0; i < numBubbles; i++) {
        if (i >= 125) break;
        float metaballValue = metaball(pos, bubblePositions[i], bubbleStrengths[i]);
        value += metaballValue;
        
        if (metaballValue > maxMetaballValue) {
            maxMetaballValue = metaballValue;
            dominantIndex = i;
        }
    }
    
    // Umbral de pertenencia, si el value es mayor, se considera que el píxel está dentro del campo de las burbujas
    float threshold = 1.2;
    
    if (value > threshold) {
        float intensity = smoothstep(threshold, threshold * 1.5, value);
        
        // Usar color burbuja dominante o predeterminado si no se encuentra dominante
        vec3 bubbleColor = vec3(0.3, 0.6, 0.95);
        if (dominantIndex != -1) {
            bubbleColor = bubbleColors[dominantIndex];
        }
        
        // Añadir efecto de brillo
        float shimmer = 0.05 * sin(time * 3.0 + pos.x * 0.02 + pos.y * 0.02);
        bubbleColor += shimmer;
        
        // Agregar resplandor más fuerte en el centro
        if (dominantIndex != -1) {
            float highlight = 0.1 * (1.0 - distance(pos, bubblePositions[dominantIndex]) / 100.0);
            bubbleColor += vec3(highlight * 0.3, highlight * 0.3, highlight * 0.1);
        }
        
        // Transparencia, más opaco en el centro
        float alpha = 0.7 + intensity * 0.25;
        
        // Una especie de iluminación de borde, para que destaque del fondo
        float edge = 1.0 - smoothstep(threshold, threshold * 1.3, value);
        alpha += edge * 0.1;
        
        FragColor = vec4(bubbleColor, alpha);
    } else { // No se supera el umbral, no se pinta nada
        // Fondo transparente
        FragColor = vec4(0.0, 0.0, 0.0, 0.0);
    }
}