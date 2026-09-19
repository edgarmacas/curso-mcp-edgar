# Tasks: Convertidor de Temperatura

**Feature**: `001-temperature-converter`
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Configure project configuration and dependencies in pyproject.toml
- [X] T002 [P] Create package and test directory structure in src/temperature_converter/ and tests/
- [X] T003 [P] Create test configuration in tests/conftest.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Implement custom exception hierarchy in src/temperature_converter/exceptions.py
- [X] T005 [P] Implement Scale enum, symbol mappings, and absolute zero constants in src/temperature_converter/models.py
- [X] T006 Implement public exports in src/temperature_converter/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Conversión entre Celsius y Fahrenheit (Priority: P1) 🎯 MVP

**Goal**: Convertir valores de temperatura entre las escalas Celsius y Fahrenheit con redondeo a 2 decimales.

**Independent Test**: Verificar que 0 °C convierte a 32.00 °F, 212 °F a 100.00 °C, y 37 °C a 98.60 °F con precisión exacta.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [P] [US1] Unit tests for Celsius <-> Fahrenheit conversion in tests/unit/test_celsius_fahrenheit.py

### Implementation for User Story 1

- [X] T008 [US1] Implement Celsius <-> Fahrenheit conversion logic and rounding in src/temperature_converter/converter.py
- [X] T009 [US1] Implement core CLI argument parsing and conversion dispatch for Celsius and Fahrenheit in src/temperature_converter/cli.py

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently (MVP)

---

## Phase 4: User Story 2 - Conversión entre Celsius y Kelvin con Cero Absoluto (Priority: P2)

**Goal**: Convertir temperaturas entre Celsius y Kelvin con validación estricta de cero absoluto (Kelvin >= 0, Celsius >= -273.15).

**Independent Test**: Verificar que 0 °C convierte a 273.15 K, 300 K a 26.85 °C, y valores como -10 K o -300 °C lanzan AbsoluteZeroViolationError.

### Tests for User Story 2

- [X] T010 [P] [US2] Unit tests for Celsius <-> Kelvin and absolute zero enforcement in tests/unit/test_celsius_kelvin.py

### Implementation for User Story 2

- [X] T011 [US2] Implement Celsius <-> Kelvin conversion and absolute zero validation in src/temperature_converter/converter.py
- [X] T012 [US2] Update CLI error handling for absolute zero violations in src/temperature_converter/cli.py

**Checkpoint**: User Stories 1 AND 2 both work independently and handle boundary conditions

---

## Phase 5: User Story 3 - Conversión entre Fahrenheit y Kelvin (Priority: P3)

**Goal**: Convertir temperaturas directamente entre Fahrenheit y Kelvin asegurando el límite de cero absoluto (Fahrenheit >= -459.67).

**Independent Test**: Verificar que 32 °F convierte a 273.15 K, 373.15 K a 212.00 °F, y valores inferiores a -459.67 °F son rechazados.

### Tests for User Story 3

- [X] T013 [P] [US3] Unit tests for Fahrenheit <-> Kelvin conversion in tests/unit/test_fahrenheit_kelvin.py

### Implementation for User Story 3

- [X] T014 [US3] Implement Fahrenheit <-> Kelvin conversion in src/temperature_converter/converter.py

**Checkpoint**: Full interoperability between Celsius, Fahrenheit and Kelvin is complete

---

## Phase 6: User Story 4 - Conversión de Identidad y Preservación de Valor (Priority: P4)

**Goal**: Retornar el mismo valor numérico (redondeado a 2 decimales) cuando la unidad de origen y de destino sean la misma.

**Independent Test**: Verificar que 25 °C a Celsius retorna 25.00 °C, y 100 K a Kelvin retorna 100.00 K sin recálculos.

### Tests for User Story 4

- [X] T015 [P] [US4] Unit tests for identity conversions in tests/unit/test_identity.py

### Implementation for User Story 4

- [X] T016 [US4] Implement identity conversion short-circuit in src/temperature_converter/converter.py

**Checkpoint**: All 4 user stories are independently functional and fully implemented

---

## Phase 7: User Story 5 - Modo Interactivo por Consola (Priority: P5)

**Goal**: Permitir la ejecución interactiva guiada por consola solicitando valor y escalas paso a paso cuando no se proporcionan argumentos o con la bandera `--interactive`.

**Independent Test**: Ejecutar `python -m temperature_converter` sin argumentos y verificar que solicite valor, unidad de origen y unidad de destino, devolviendo el resultado formateado.

### Implementation for User Story 5

- [X] T017 [US5] Implement interactive input prompts and handler in src/temperature_converter/cli.py

**Checkpoint**: Modo interactivo y modo argumentos funcionan de forma coordinada.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Robustez de CLI, ejecución como módulo, pruebas de integración y validación quickstart

- [X] T018 [P] Implement executable module entry point in src/temperature_converter/__main__.py
- [X] T019 [P] Implement CLI end-to-end integration tests in tests/integration/test_cli.py
- [X] T020 [P] Implement edge case tests (non-numeric inputs, empty inputs, case tolerance) in tests/integration/test_edge_cases.py
- [X] T021 Run quickstart.md validation scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion.
  - US1 (P1) is the MVP and establishes `converter.py` and `cli.py`.
  - US2 (P2) builds on the converter logic to add Kelvin and absolute zero enforcement.
  - US3 (P3) adds Fahrenheit ↔ Kelvin conversion formulas.
  - US4 (P4) adds identity conversion bypass.
- **Polish (Phase 7)**: Depends on all user stories being implemented.

### User Story Dependencies

- **User Story 1 (P1)**: Depends only on Foundational (Phase 2). Delivers viable MVP.
- **User Story 2 (P2)**: Depends on Foundational (Phase 2) and `converter.py` from US1.
- **User Story 3 (P3)**: Depends on Foundational (Phase 2) and `converter.py` from US1/US2.
- **User Story 4 (P4)**: Depends on Foundational (Phase 2) and `converter.py`.

### Parallel Opportunities

- Within Phase 1: T002 and T003 can run in parallel.
- Within Phase 2: T004 (`exceptions.py`) and T005 (`models.py`) can run in parallel.
- Within User Story 1: T007 (`test_celsius_fahrenheit.py`) can be written before/parallel to setup.
- Within Phase 7: T017, T018, and T019 can all run in parallel.

---

## Parallel Example: User Story 1

```bash
# Launch test and models in parallel:
Task: "Unit tests for Celsius <-> Fahrenheit conversion in tests/unit/test_celsius_fahrenheit.py"
Task: "Implement custom exception hierarchy in src/temperature_converter/exceptions.py"
Task: "Implement Scale enum, symbol mappings, and absolute zero constants in src/temperature_converter/models.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (`pyproject.toml`, carpetas, `conftest.py`).
2. Complete Phase 2: Foundational (`exceptions.py`, `models.py`, `__init__.py`).
3. Complete Phase 3: User Story 1 (`test_celsius_fahrenheit.py`, `converter.py`, `cli.py`).
4. **STOP and VALIDATE**: Run `uv run pytest tests/unit/test_celsius_fahrenheit.py` and CLI manual check.
5. MVP complete: Conversión Celsius ↔ Fahrenheit funcional.

### Incremental Delivery

1. Setup + Foundational -> Base sólida y probada.
2. US1 -> Celsius ↔ Fahrenheit (MVP).
3. US2 -> Celsius ↔ Kelvin con validación de cero absoluto.
4. US3 -> Fahrenheit ↔ Kelvin.
5. US4 -> Conversiones de identidad.
6. Polish -> CLI module entry point, edge case & integration tests, quickstart validation.
