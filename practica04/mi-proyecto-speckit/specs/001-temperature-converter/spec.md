# Feature Specification: Convertidor de Temperatura

**Feature Branch**: `001-temperature-converter`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Implementa el convertidor siguiendo esta spec: practica3/clase-ssd/spec_manual.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Conversión entre Celsius y Fahrenheit (Priority: P1)

Como usuario, quiero convertir valores de temperatura entre las escalas Celsius y Fahrenheit para interpretar temperaturas en el sistema métrico o anglosajón según mi necesidad.

**Why this priority**: Es la conversión más común y utilizada internacionalmente; representa el núcleo funcional mínimo viable (MVP).

**Independent Test**: Se puede validar introduciendo temperaturas conocidas (ej. punto de congelación 0 °C = 32 °F, o punto de ebullición 100 °C = 212 °F) y verificando el resultado numérico exacto redondeado a 2 decimales.

**Acceptance Scenarios**:

1. **Given** una temperatura de 0 °C, **When** el usuario solicita la conversión a Fahrenheit, **Then** el sistema entrega 32.00 °F.
2. **Given** una temperatura de 212 °F, **When** el usuario solicita la conversión a Celsius, **Then** el sistema entrega 100.00 °C.
3. **Given** una temperatura de 37 °C (temperatura corporal promedio), **When** el usuario solicita la conversión a Fahrenheit, **Then** el sistema entrega 98.60 °F.

---

### User Story 2 - Conversión entre Celsius y Kelvin con validación de cero absoluto (Priority: P2)

Como usuario científico o estudiante, quiero convertir temperaturas entre Celsius y Kelvin asegurando que no se permitan valores por debajo del cero absoluto para evitar mediciones físicamente imposibles.

**Why this priority**: Kelvin es la escala fundamental en ciencia y requiere reglas de validación físicas críticas (no existen valores negativos en Kelvin).

**Independent Test**: Se puede verificar convirtiendo 0 °C a Kelvin (273.15 K), 0 K a Celsius (-273.15 °C), e intentando ingresar valores menores a 0 K para comprobar que sean rechazados.

**Acceptance Scenarios**:

1. **Given** una temperatura de 0 °C, **When** el usuario solicita la conversión a Kelvin, **Then** el sistema entrega 273.15 K.
2. **Given** una temperatura de 300 K, **When** el usuario solicita la conversión a Celsius, **Then** el sistema entrega 26.85 °C.
3. **Given** una temperatura de -10 K, **When** el usuario solicita cualquier conversión, **Then** el sistema rechaza la operación informando que la temperatura no puede ser menor a 0 Kelvin.

---

### User Story 3 - Conversión entre Fahrenheit y Kelvin (Priority: P3)

Como usuario, quiero convertir temperaturas directamente entre Fahrenheit y Kelvin sin necesidad de calcular pasos intermedios de forma manual.

**Why this priority**: Completa la interoperabilidad total entre las tres escalas termométricas soportadas.

**Independent Test**: Se valida ingresando valores en Fahrenheit (ej. -459.67 °F) y comprobando que resulte en 0.00 K, así como valores en Kelvin a Fahrenheit.

**Acceptance Scenarios**:

1. **Given** una temperatura de 32 °F, **When** el usuario solicita la conversión a Kelvin, **Then** el sistema entrega 273.15 K.
2. **Given** una temperatura de 373.15 K, **When** el usuario solicita la conversión a Fahrenheit, **Then** el sistema entrega 212.00 °F.

---

### User Story 4 - Conversión de identidad y preservación de valor (Priority: P4)

Como usuario, si indico la misma escala como origen y destino, deseo que el sistema retorne el mismo valor formateado adecuadamente para evitar cálculos innecesarios o confusiones.

**Why this priority**: Evita inconsistencias de cálculo o transformaciones redundantes.

**Independent Test**: Ingresar cualquier número válido con origen y destino idénticos (ej. Celsius a Celsius) y verificar que devuelva el mismo valor con 2 decimales.

**Acceptance Scenarios**:

1. **Given** una temperatura de 25 °C, **When** el usuario solicita la conversión a Celsius, **Then** el sistema devuelve 25.00 °C sin modificaciones.

---

### User Story 5 - Modo Interactivo Guiado por Consola (Priority: P5)

Como usuario que ejecuta la aplicación por terminal sin recordar los argumentos, quiero que el sistema me solicite interactivamente el valor y las escalas paso a paso para poder realizar conversiones de forma intuitiva.

**Why this priority**: Mejora la experiencia de usuario y accesibilidad desde terminal cuando no se conoce la sintaxis de banderas.

**Independent Test**: Ejecutar el comando sin argumentos o con la bandera `-i`, ingresar interactivamente valor, escala origen y escala destino, y verificar que entregue el resultado formateado y finalice con código de salida 0.

**Acceptance Scenarios**:

1. **Given** que el usuario ejecuta la aplicación sin argumentos, **When** ingresa "100", "C" y "F" en los prompts interactivos, **Then** el sistema presenta el resultado formateado y termina exitosamente.
2. **Given** que el usuario ingresa datos inválidos en el prompt interactivo, **When** se produce un error de validación, **Then** el sistema muestra el mensaje de error correspondiente y finaliza con código de salida 1.

---

### Edge Cases

- **Entrada no numérica**: Cuando el usuario introduce texto alfanumérico o caracteres inválidos (por ejemplo "abc", "NaN", vacío) en el valor de temperatura, el sistema debe emitir un mensaje de error claro y descriptivo en lugar de fallar abruptamente.
- **Valores inferiores al cero absoluto**: Cuando se ingresa un valor físicamente imposible (Kelvin < 0, Celsius < -273.15, o Fahrenheit < -459.67), el sistema debe rechazar la solicitud indicando la violación del límite inferior físico.
- **Temperaturas negativas válidas**: Temperaturas negativas dentro del rango físico válido (por ejemplo -40 °C, que equivale a -40 °F) deben procesarse con total normalidad y precisión.
- **Misma escala de origen y destino**: Conversiones donde la unidad origen y destino coinciden (ej. Kelvin a Kelvin) deben devolver el valor original conservando el formato a 2 decimales.
- **Precisión y redondeo de decimales recurrentes**: En valores con infinitos decimales (ej. conversiones de grados Fahrenheit con factor 5/9), el resultado debe redondearse estrictamente a 2 decimales según la regla estándar de redondeo.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir la conversión de valores de temperatura entre las tres escalas: Celsius (°C), Fahrenheit (°F) y Kelvin (K).
- **FR-002**: El sistema DEBE redondear el resultado numérico de cualquier conversión a exactamente 2 lugares decimales.
- **FR-003**: El sistema DEBE validar que la temperatura proporcionada no sea inferior al cero absoluto (0 Kelvin, -273.15 Celsius o -459.67 Fahrenheit) y rechazar la solicitud en caso de incumplimiento.
- **FR-004**: El sistema DEBE validar que el valor de entrada sea estrictamente numérico y devolver un mensaje de error claro ante entradas no numéricas o vacías.
- **FR-005**: El sistema DEBE admitir números negativos válidos en Celsius y Fahrenheit que se encuentren por encima o igual al cero absoluto.
- **FR-006**: El sistema DEBE retornar el mismo número formateado a 2 decimales cuando la unidad de origen y la de destino sean la misma.
- **FR-007**: El sistema DEBE admitir la especificación de unidades de forma insensible a mayúsculas y minúsculas (ej. 'c', 'C', 'celsius', 'CELSIUS').

### Key Entities *(include if feature involves data)*

- **Medición de Temperatura**: Representa una magnitud escalar numérica asociada a una escala termométrica específica.
- **Escala Termométrica**: Unidad de medida de temperatura soportada (Celsius, Fahrenheit o Kelvin).
- **Solicitud de Conversión**: Estructura que encapsula el valor numérico inicial, la escala de origen y la escala de destino deseada.
- **Resultado de Conversión**: Estructura que encapsula el valor numérico final redondeado y la unidad de destino correspondiente, o el detalle del error en caso de fallo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las conversiones entre escalas válidas producen resultados matemáticamente correctos redondeados a 2 decimales.
- **SC-002**: El 100% de las entradas no numéricas o con valores inferiores al cero absoluto son interceptadas y rechazadas con mensajes informativos claros sin interrupción del servicio.
- **SC-003**: El tiempo de respuesta para calcular y presentar una conversión es menor a 100 milisegundos desde el momento en que se solicita.
- **SC-004**: Las operaciones de identidad (origen igual a destino) preservan el valor numérico con cero margen de error.

## Assumptions

- Las escalas soportadas en esta versión están limitadas a Celsius, Fahrenheit y Kelvin (Rankine y otras escalas quedan fuera de alcance).
- Se adopta la constante estándar para el cero absoluto: 0 K = -273.15 °C = -459.67 °F.
- El formato decimal de salida utiliza punto decimal con dos cifras (ejemplo: 25.00).
- La interacción con el usuario no requiere persistencia de datos históricos ni conexión a servicios externos de red.
