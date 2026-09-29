# Decisiones del rediseño

## ADR-UI-001 — Autoridad de código y Figma

- Estado: aceptada.
- Fecha: 2026-09-29.
- Decisión: el código conserva autoridad sobre lógica, API, modelos, validaciones y estado funcional. Figma será la referencia para layout, lenguaje visual, componentes y estados visuales.
- Consecuencia: la migración será incremental y no reescribirá lógica de negocio para alcanzar coincidencia visual.

## ADR-UI-002 — Archivo de producto

- Estado: aceptada.
- Fecha: 2026-09-29.
- Decisión: usar `OICA — Product Design`, file key `pQYp8TECtmWQLDcHISqfZP`.
- Consecuencia: exploraciones, foundations, componentes, patrones y pantallas vivirán en el mismo archivo con páginas separadas.

## ADR-UI-003 — Sistema propio, no derivado de un kit genérico

- Estado: aceptada.
- Fecha: 2026-09-29.
- Contexto: Figma expone Material 3 y Simple Design System, pero el código no tiene Code Connect ni un sistema previo compatible.
- Decisión: construir OICA Design System v1 con tokens y APIs propios; usar kits externos solo como referencia puntual. Mantener Lucide como familia de iconos en código.
- Motivo: evita heredar una matriz de variantes, tokens y estética que no responden al dominio industrial de OICA.

## ADR-UI-004 — Dirección visual

- Estado: aceptada.
- Fecha: 2026-09-29.
- Alternativas: A Precision Engineering, B Industrial Clarity, C CAD Control Room.
- Decisión: **B — Industrial Clarity** como lenguaje base, incorporando de A los
  numerales monoespaciados para métricas y la precisión geométrica de tablas y
  diagramas.
- Autoridad: elección explícita del usuario («elijo tu recomendación»).
- Consecuencia visual: superficies cálidas y claras, acción cobalto, teal para
  eficiencia/éxito, densidad media y color reservado a significado.
- Consecuencia técnica: tema claro v1, tokens semánticos obligatorios, Geist y
  Geist Mono como objetivo tipográfico con fallback verificable, Lucide como
  iconografía y responsive por composición, no por reducción uniforme.

## ADR-UI-005 — Alcance y arquitectura de tokens v1

- Estado: aceptada.
- Fecha: 2026-09-29.
- Decisión: usar colecciones separadas para primitivos, color semántico y
  dimensiones. Los componentes solo pueden enlazar tokens semánticos o de
  dimensión; nunca colores primitivos directamente.
- Tema: un único modo claro en v1. No se construirá un modo oscuro incompleto;
  la arquitectura de alias permite añadirlo después sin cambiar las APIs de los
  componentes.
- Escalas: base espacial de 4 px; radios 0/4/8/12/16/full; controles 32/40/48;
  iconos 16/20/24; movimiento 100/160/240 ms.
- Motivo: OICA no ofrece cambio de tema y la dirección C fue descartada. Un modo
  oscuro ahora aumentaría alcance y QA sin cubrir una necesidad funcional real.

## ADR-UI-006 — Implementación code-first mientras Figma está limitado

- Estado: aceptada.
- Fecha: 2026-09-29.
- Contexto: el plan Figma Starter agotó la cuota MCP después de crear las
  exploraciones; inspección, librerías y escritura están bloqueadas.
- Decisión: por autorización explícita del usuario (opción B), implementar
  foundations, componentes y pantallas primero en código usando
  `DESIGN-SYSTEM.md` como especificación visual temporal.
- Sincronización: cuando vuelva Figma, generar variables, biblioteca y pantallas
  desde la implementación validada, conservar los mismos nombres semánticos y
  realizar QA bidireccional.
- Consecuencia: el código será temporalmente la evidencia visual ejecutable; no
  se elimina Figma del criterio final ni se declara terminado el proyecto sin él.
