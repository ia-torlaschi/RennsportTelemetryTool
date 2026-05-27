---
name: traductor-espanol-ingles
description: Traduccion tecnica y profesional entre espanol e ingles. Usar solo cuando la intencion principal sea traducir o reescribir de forma explicita entre ESdescription: Traduccion tecnica y profesional entre espanol e ingles. Usar solo cuando la intencion principal sea traducir o reescribir de forma explicita entre ES↔EN.EN.
---

# Traductor Espanol <-> Ingles (Low-Noise)

Skill de traduccion ES<->EN para contenido tecnico y profesional con terminologia precisa y salida limpia.


## Usar cuando

- El usuario pide traducir explicitamente entre espanol e ingles.
- El usuario pide reescritura bilingue: mas formal, mas natural, version ejecutiva, version tecnica, version literal.
- El input es texto, email, informe, tabla, comentario en codigo, log en prosa o imagen con texto y objetivo de traduccion ES<->EN.

## No usar cuando

- La intencion principal es tecnica (arquitectura, debugging, scripting, DBA, IaC, seguridad) y no traduccion.
- El usuario pide diseno o implementacion, no conversion de idioma.
- El texto no requiere ES<->EN (por ejemplo, solo aleman, solo frances, etc.).

## Prioridad

- Esta skill solo aplica si la tarea principal es traduccion.
- Si la tarea principal es tecnica, priorizar la skill tecnica del dominio.

## Comportamiento por defecto

1. Detectar idioma origen y traducir al idioma destino solicitado.
2. Si no hay destino explicito, traducir al idioma opuesto.
3. Devolver solo la traduccion limpia, sin preambulos.
4. Preservar formato: titulos, listas, tablas, saltos de linea, bloques de codigo, etiquetas.
5. Mantener consistencia terminologica en todo el documento.
6. No inventar contenido; usar [ilegible], [parcialmente visible] o [ambiguo] cuando haga falta.
7. Pedir aclaracion solo si una ambiguedad cambia el sentido tecnico.

## Reglas de calidad

- Registro por defecto: profesional neutro.
- Mantener acronimos tecnicos sin traducir: API, SQL, JSON, YAML, OCI, AWS, GCP, K8s, RPO, RTO, SLO, SLA, CI/CD.
- No traducir nombres de productos, comandos, rutas, identificadores, codigos de error (por ejemplo ORA-xxxxx), ni claves de configuracion.
- En codigo, traducir solo comentarios o texto de prosa, nunca la sintaxis o identificadores.

## Falsos amigos criticos

EN -> ES:
- actually -> en realidad (no actualmente)
- eventually -> finalmente / con el tiempo (no eventualmente)
- realize -> darse cuenta (no realizar)
- assist -> ayudar (no asistir)
- sensible -> sensato / razonable (no sensible)

ES -> EN:
- actualmente -> currently
- asistir a -> attend
- sensible -> sensitive
- compromiso -> commitment
- pretender -> intend

## Formato de salida

- Modo default: solo traduccion.
- Modos opcionales si el usuario lo pide:
  - lado a lado (original/traduccion)
  - literal + natural
  - ejecutiva + tecnica
  - traduccion + glosario breve

## Referencias internas

- references/glossary.md
- references/false-friends.md

Consultar referencias solo si hay duda terminologica o riesgo de literalismo.
