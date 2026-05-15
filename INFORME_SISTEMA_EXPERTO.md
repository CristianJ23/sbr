# Informe Técnico: Simulador de Sistema Basado en Reglas (SBR)

## 1. Introducción
Este proyecto consiste en un **Sistema Basado en Reglas (SBR)** diseñado con fines didácticos para el área de Representación del Conocimiento. El sistema simula el proceso de toma de decisiones de un experto en turismo, permitiendo a los usuarios entender cómo se derivan conclusiones a partir de hechos iniciales mediante mecanismos de inferencia lógica.

## 2. Arquitectura del Sistema
El sistema se divide en tres capas principales:
*   **Motor de Inferencia (`expert_system/engine.py`):** El núcleo lógico escrito en Python que implementa los algoritmos de encadenamiento.
*   **Interfaz de Usuario (Frontend):** Una aplicación web reactiva construida con HTML5, CSS3 (estilo "Dark Mode" moderno) y JavaScript.
*   **Servidor de Aplicación (`main.py`):** Utiliza el framework **FastAPI** para gestionar la comunicación entre la web y el motor lógico.

## 3. Motor de Inferencia y Resolución de Conflictos
La característica principal de esta versión es la capacidad de gestionar **Conflictos de Reglas**.

### 3.1. Mecanismos de Razonamiento
1.  **Encadenamiento hacia Adelante (Forward Chaining):** El motor parte de los hechos conocidos y busca reglas cuyas condiciones se cumplan para generar nuevos hechos.
2.  **Encadenamiento hacia Atrás (Backward Chaining):** El motor parte de una meta (objetivo) y busca recursivamente si existen hechos o reglas que puedan probar dicha meta.

### 3.2. Estrategias de Resolución de Conflictos
Cuando múltiples reglas pueden activarse al mismo tiempo (conjunto de conflicto), el sistema aplica los siguientes criterios de selección en orden de jerarquía:

1.  **Especificidad (Criterio de Mayor Condicionamiento):** Se prioriza la regla que tiene un mayor número de condiciones (`conditions`). Esto se basa en el principio de que una regla con más requisitos es "más específica" y, por tanto, más precisa para el caso actual.
2.  **Prioridad Explícita:** El sistema permite asignar un peso numérico (`priority`) a cada regla. A mayor número, mayor relevancia.
3.  **Orden de Definición:** Como último recurso, se utiliza el identificador de la regla para mantener un comportamiento determinista.

## 4. Funcionalidades Destacadas
*   **Memoria de Trabajo Dinámica:** Los hechos se activan y desactivan en tiempo real, disparando el motor automáticamente.
*   **Creador de Reglas Interactivo:** El usuario puede expandir la base de conocimiento sin modificar el código, definiendo nuevas reglas y sus prioridades.
*   **Explicación del Razonamiento:** Cada paso de la inferencia se documenta visualmente, indicando por qué se eligió una regla y qué hecho nuevo se dedujo.
*   **Logs de Depuración:** Una consola integrada muestra los detalles técnicos del ciclo de razonamiento y la resolución de conflictos.

## 5. Ejemplo de Resolución de Conflicto
En la base de datos preconfigurada, existen dos reglas:
*   **R6 (General):** SI (Montaña) ENTONCES (Perfil Aventurero).
*   **R7 (Específica):** SI (Montaña) Y (Deporte) ENTONCES (Perfil Aventurero Extremo).

Si el usuario selecciona ambos hechos ("Montaña" y "Deporte"), el motor identifica que ambas reglas son válidas. Aplicando la lógica de **especificidad**, el sistema elige primero la **R7**, informando al usuario sobre la resolución del conflicto para priorizar el conocimiento más detallado.

## 6. Conclusión
El sistema cumple con los requisitos de un simulador de SBR robusto, proporcionando no solo la capacidad de inferencia, sino también una transparencia total en la toma de decisiones mediante su módulo de resolución de conflictos. Es una herramienta eficaz para demostrar la complejidad y potencia de los sistemas expertos modernos.
