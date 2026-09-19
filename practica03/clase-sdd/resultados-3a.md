# Resultados de Pruebas — Bloque 3.A (Spec a mano)

Proyecto: **Convertidor de Unidades de Temperatura (Celsius, Fahrenheit, Kelvin)**  
Especificación de origen: `spec_manual.md`

---

## Casos de Prueba Evaluados

| Tipo de caso | Entrada / Escenario | Salida Esperada | Salida Obtenida | Estado |
|---|---|---|---|---|
| **1. Caso normal** | `convert_temperature(100, "C", "F")` | `212.0` (Fahrenheit) | `212.0` | ✅ PASÓ |
| **2. Caso borde de la spec** | `convert_temperature(-5, "K", "C")` | Rechazar con error claro (`ValueError: ... menor a 0 K`) | `ValueError: Error de límite físico: La temperatura en Kelvin no puede ser menor a 0 K. Recibido: -5.0 K.` | ✅ PASÓ |
| **3. Caso no contemplado** | `convert_temperature(" 98.6 ", "°f", "kelvin")` | Manejo de espacios en blanco, símbolos de grados (`°`) y unidades en minúsculas mixtas, convirtiendo a Kelvin | `310.15` (Kelvin con redondeo a 2 decimales) | ✅ PASÓ |

---

## Resumen de Verificación de Criterios de Aceptación

- [x] **Convierte correctamente de Celsius a Fahrenheit y viceversa:**  
  - `0 °C` $\rightarrow$ `32.0 °F`  
  - `100 °C` $\rightarrow$ `212.0 °F`  
  - `212.0 °F` $\rightarrow$ `100.0 °C`
- [x] **Convierte correctamente de Celsius a Kelvin y viceversa:**  
  - `0 °C` $\rightarrow$ `273.15 K`  
  - `273.15 K` $\rightarrow$ `0.0 °C`
- [x] **Redondea el resultado a 2 decimales:**  
  - `70 °F` $\rightarrow$ `21.11 °C`
- [x] **Rechaza una temperatura en Kelvin menor a 0:**  
  - `-1 K` $\rightarrow$ `ValueError: Error de límite físico: La temperatura en Kelvin no puede ser menor a 0 K.`
- [x] **Casos borde contemplados:**
  - Valor no numérico (`"abc"`) genera mensaje de error explicativo sin excepción no controlada.
  - Misma unidad de entrada y salida (`25 °C` a `°C`) devuelve el valor original (`25.0`).
  - Temperaturas negativas válidas (`-40 °C` a `°F`) producen `-40.0 °F`.
