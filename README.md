# Bubble Simulator

**Simulador de burbujas utilizando metaballs en 2D**

Este proyecto es una simulación interactiva de burbujas basada en el algoritmo de metaballs, implementada en Python con GLSL para el renderizado. La simulación permite visualizar cómo las burbujas interactúan entre sí, fusionándose y separándose, creando efectos visuales fluidos y orgánicos.

![Simulación de burbujas](https://github.com/mariaemg/bubble_simulator/assets/imagen_ejemplo.png)

---

## 🚀 Descripción

El **Bubble Simulator** es una herramienta educativa y experimental que utiliza técnicas de computación gráfica para simular la interacción de burbujas en un espacio bidimensional. Emplea el algoritmo de metaballs para representar las burbujas como superficies isovalores que se fusionan al acercarse, creando una apariencia de fluidez y cohesión.

---

## 🧪 Características

- **Simulación en tiempo real**: Interacción dinámica con las burbujas en el espacio 2D.
- **Renderizado con GLSL**: Uso de sombreadores para efectos visuales avanzados.
- **Interactividad**: Posibilidad de agregar, mover y eliminar burbujas durante la simulación.
- **Implementación modular**: Código organizado en clases y funciones para facilitar la comprensión y extensión.

---

## 📂 Estructura del Proyecto

```bash
bubble_simulator/
├── shaders/                # Archivos GLSL para el renderizado
├── __init__.py             # Inicialización del paquete
├── __main__.py             # Punto de entrada principal
├── bubble_agent.py         # Lógica de las burbujas
├── renderer.py             # Manejo de la renderización
└── simulation.py           # Control de la simulación
