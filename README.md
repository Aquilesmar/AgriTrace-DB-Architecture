# AgriTrace: Relational Database Architecture for Coffee Supply Chain

## Visión General
Este proyecto presenta el diseño y la arquitectura de una base de datos relacional orientada a la trazabilidad agrícola y el cumplimiento de normativas internacionales (como la EUDR - European Union Deforestation Regulation). 

El sistema modela la complejidad de la cadena de suministro del café, gestionando desde la información legal de los productores hasta las certificaciones orgánicas de cada parcela de tierra.

## Arquitectura de Datos y Reglas de Negocio
El modelo está construido utilizando **Python y el ORM de Django**, aplicando validaciones estrictas a nivel de backend para garantizar la integridad de los datos.

### Entidades Principales:
1. **Productor:** Gestión de identidades (Personas Naturales vs. Jurídicas). Implementa validaciones algorítmicas de documentos fiscales (RUC/DNI) para prevenir la corrupción de datos en origen.
2. **Predio (Finca):** Almacena datos geoespaciales (Lat/Long) y evalúa el cumplimiento de la ley europea de cero deforestación (`eudr_compliant`).
3. **Parcela & Cultivo:** Desglose del uso de la tierra (Hectáreas, Tipo de Cultivo) con relación *One-To-Many* hacia el Predio.
4. **PlanCampana:** Historial de auditorías y estatus de certificación anual (Orgánico, Transición, Convencional).

## Desafíos Técnicos Resueltos
* **Prevención de Inconsistencias:** Desarrollo de un método `clean()` personalizado que intercepta el guardado de datos para verificar prefijos fiscales peruanos (RUCs 10, 15, 17, 20) y forzar la estructura correcta (Razón Social vs. Nombres).
* **Escalabilidad Geográfica:** Estructura preparada para manejar múltiples coordenadas por lote y facilitar integraciones con APIs de mapas o validación satelital.
