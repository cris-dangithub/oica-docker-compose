# Reglas de diseño para futuras IAs

Estado: borrador inicial; se consolidará con OICA Design System v1.

1. No introducir colores hardcoded si existe un token semántico.
2. Los componentes consumen tokens semánticos, nunca primitivos de color directamente.
3. Buscar un componente existente antes de crear otro.
4. Reutilizar la escala de spacing, sizing, radius, borde y elevación.
5. No crear una variante sin un caso real del producto.
6. Implementar default, hover, active, focus-visible, disabled y error cuando correspondan.
7. Mantener labels persistentes y nombres accesibles; el placeholder no sustituye al label.
8. Preservar navegación por teclado, orden de foco y targets táctiles adecuados.
9. Responsive significa recomponer, priorizar y controlar overflow; no solo reducir tamaños.
10. Las tablas densas requieren una estrategia móvil explícita.
11. Mantener Lucide como iconografía salvo decisión registrada.
12. No cambiar lógica, API ni semántica funcional para resolver un problema visual.
13. Actualizar Figma, documentación y código cuando se añada una primitive o componente nuevo.
14. Ejecutar visual QA y las verificaciones del frontend antes de declarar una migración terminada.
15. Toda cifra visible usa el formato numérico de `DESIGN-SYSTEM.md` (punto decimal, sin separador de miles, espacio antes de la unidad) mediante los ayudantes `decimal`, `entero`, `pct`, `pp`, `kg`, `numero` y `metros`; nunca `toFixed` ni `toLocaleString` sueltos. Las entradas decimales usan `DecimalInput` o texto con `inputMode="decimal"` y `leerDecimal`.

