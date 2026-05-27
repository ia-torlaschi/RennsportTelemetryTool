# DrawIO — Referencia de XML y Layout
# Archivo de referencia para drawio-specialist skill
# Leer cuando se necesiten reglas detalladas de XML, estilos, ERD o layout por arquitectura

---

## Tabla de contenidos

1. [Reglas XML completas](#1-reglas-xml-completas)
2. [Estilos visuales recomendados](#2-estilos-visuales-recomendados)
3. [Layout por tipo de arquitectura](#3-layout-por-tipo-de-arquitectura)
4. [Reglas para ERD relacional](#4-reglas-para-erd-relacional)
5. [Reglas para modelos documentales MongoDB/NoSQL](#5-reglas-para-modelos-documentales-mongodbnosql)
6. [Reglas para Terraform / IaC](#6-reglas-para-terraform--iac)
7. [Reglas para diagramas de seguridad y cumplimiento](#7-reglas-para-diagramas-de-seguridad-y-cumplimiento)
8. [Patrones de mejora de diagramas existentes](#8-patrones-de-mejora-de-diagramas-existentes)

---

## 1. Reglas XML completas

### Estructura base de un archivo draw.io multi-página

```xml
<mxfile host="app.diagrams.net" modified="2025-01-01T00:00:00Z" version="21.0.0">
  <diagram id="page-overview" name="00 Overview">
    <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1"
                  tooltips="1" connect="1" arrows="1" fold="1"
                  page="1" pageScale="1" pageWidth="1654" pageHeight="1169"
                  math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- elementos aquí -->
      </root>
    </mxGraphModel>
  </diagram>
  <diagram id="page-arch" name="01 Arquitectura completa">
    <!-- segunda página -->
  </diagram>
</mxfile>
```

### Nodo contenedor (swim lane / grupo)

```xml
<mxCell id="container-vpc" value="VPC Producción" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],
  [1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];
  shape=mxgraph.cisco.sites.generic_building;html=1;whiteSpace=wrap;fillColor=#dae8fc;
  strokeColor=#6c8ebf;swimlane=0;fontSize=12;fontStyle=1;align=left;
  container=1;collapsible=0;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="600" height="400" as="geometry"/>
</mxCell>
```

**Forma más segura y genérica para contenedores (sin shapes de librería):**

```xml
<mxCell id="ctr-vpc" value="VPC — 10.0.0.0/16" style="rounded=1;whiteSpace=wrap;html=1;
  fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;fontStyle=1;align=left;verticalAlign=top;
  spacingLeft=10;container=1;collapsible=0;" vertex="1" parent="1">
  <mxGeometry x="80" y="80" width="700" height="500" as="geometry"/>
</mxCell>
```

### Nodo simple (servicio/componente)

```xml
<mxCell id="svc-api-gw" value="API Gateway&lt;br&gt;prod-api.example.com"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;
  fontSize=11;" vertex="1" parent="ctr-vpc">
  <mxGeometry x="20" y="60" width="160" height="60" as="geometry"/>
</mxCell>
```

### Conector con etiqueta

```xml
<mxCell id="conn-gw-lb" value="HTTPS:443" style="edgeStyle=orthogonalEdgeStyle;
  rounded=0;orthogonalLoop=1;jettySize=auto;exitX=1;exitY=0.5;exitDx=0;exitDy=0;
  entryX=0;entryY=0.5;entryDx=0;entryDy=0;fontSize=10;" edge="1"
  source="svc-api-gw" target="svc-lb" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

### Conector discontinuo (dependencia / control plane)

```xml
<mxCell id="conn-ctrl" value="control plane" style="edgeStyle=orthogonalEdgeStyle;
  dashed=1;dashPattern=8 8;rounded=0;fontSize=10;" edge="1"
  source="svc-k8s-ctrl" target="svc-k8s-node" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

### Nota / supuesto

```xml
<mxCell id="note-001" value="⚠ SUPUESTO: región eu-west-1 asumida.&lt;br&gt;Validar con cliente."
  style="text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;rounded=0;
  fillColor=#fffacd;strokeColor=#d6b656;fontSize=10;" vertex="1" parent="1">
  <mxGeometry x="20" y="20" width="260" height="50" as="geometry"/>
</mxCell>
```

### IDs recomendados

Usa IDs descriptivos y únicos. Evita IDs numéricos secuenciales en diagramas grandes:

```
ctr-{scope}-{nombre}         → ctr-prod-vpc, ctr-sec-subnet
svc-{tipo}-{nombre}          → svc-db-oracle, svc-lb-external
conn-{origen}-{destino}      → conn-apigw-lb, conn-app-db
note-{número}                → note-001, note-002
page-{nombre}                → page-overview, page-network
```

### Escaping XML — referencia rápida

| Carácter | Escape |
|----------|--------|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` dentro de atributo | `&quot;` |
| Salto de línea en label | `&lt;br&gt;` (HTML activado con `html=1`) |

---

## 2. Estilos visuales recomendados

### Estilos de contenedor por tipo

```
# Cloud Provider (OCI / AWS / GCP / Azure)
fillColor=#f5f5f5;strokeColor=#666666;fontStyle=1;fontSize=14;
verticalAlign=top;align=left;spacingLeft=10;container=1;collapsible=0;

# Región
fillColor=#f0f4ff;strokeColor=#4a6fa5;fontStyle=1;fontSize=12;
container=1;collapsible=0;

# VPC / VNet / VCN
fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=11;
container=1;collapsible=0;

# Subnet pública
fillColor=#d5e8d4;strokeColor=#82b366;fontSize=10;
container=1;collapsible=0;

# Subnet privada
fillColor=#fff2cc;strokeColor=#d6b656;fontSize=10;
container=1;collapsible=0;

# Subnet de datos
fillColor=#e8def8;strokeColor=#7b5ea7;fontSize=10;
container=1;collapsible=0;

# Security boundary / DMZ
fillColor=#ffe6cc;strokeColor=#d79b00;fontStyle=1;fontSize=10;
container=1;collapsible=0;

# Zona de gestión / administración
fillColor=#f8cecc;strokeColor=#b85450;fontStyle=1;fontSize=10;
container=1;collapsible=0;
```

### Estilos de nodo por tipo de servicio

```
# Base de datos / almacenamiento
shape=cylinder3;fillColor=#d5e8d4;strokeColor=#82b366;
whiteSpace=wrap;html=1;fontSize=10;

# Load Balancer
shape=rhombus;fillColor=#dae8fc;strokeColor=#6c8ebf;
whiteSpace=wrap;html=1;fontSize=10;

# Firewall / WAF
shape=mxgraph.cisco.firewalls.firewall;
# Alternativa genérica si shape no disponible:
fillColor=#f8cecc;strokeColor=#b85450;whiteSpace=wrap;html=1;fontSize=10;

# Compute / VM / Pod
rounded=1;fillColor=#dae8fc;strokeColor=#6c8ebf;
whiteSpace=wrap;html=1;fontSize=10;

# Función serverless / Lambda / Functions
shape=mxgraph.aws4.lambda_function;
# Alternativa genérica:
rounded=2;fillColor=#fff2cc;strokeColor=#d6b656;
whiteSpace=wrap;html=1;fontSize=10;

# Identidad / IAM
fillColor=#e1d5e7;strokeColor=#9673a6;
whiteSpace=wrap;html=1;fontSize=10;

# Usuario / Actor externo
shape=mxgraph.basic.person2;
# Alternativa genérica:
ellipse;fillColor=#f5f5f5;strokeColor=#666666;
fontColor=#333333;whiteSpace=wrap;html=1;fontSize=10;
```

---

## 3. Layout por tipo de arquitectura

### Cloud (top-down)

Flujo de arriba hacia abajo en este orden:

```
[Usuarios / consumidores / sistemas externos]
           ↓
[DNS / Edge / CDN / WAF / DDoS protection]
           ↓
[Conectividad: VPN / ExpressRoute / FastConnect / Direct Connect]
           ↓
[Networking: VPC/VNet/VCN → subnets]
           ↓
[Capa de aplicación: compute / containers / serverless]
           ↓
[Capa de integración: APIs / mensajería / eventos]
           ↓
[Capa de datos: bases de datos / almacenamiento / streaming]

[Seguridad / Identidad]  ←→  [Diagrama principal]  ←→  [Observabilidad]
                    ↓
         [Backup / DR / HA]
                    ↓
         [DevOps / CI-CD / Administración]
```

### Híbrido

Divide el canvas horizontalmente en dos zonas principales:

```
┌─────────────────────────┬─────────────────────────┐
│     ON-PREMISE          │      CLOUD              │
│  DC / Colo / Edge       │  VPC/VNet/VCN           │
│  ─ Servers              │  ─ Compute              │
│  ─ Databases            │  ─ Managed DBs          │
│  ─ AD / LDAP            │  ─ IAM / Entra / OCI IAM│
└──────────┬──────────────┴──────────┬──────────────┘
           │   CONECTIVIDAD PRIVADA  │
           │  VPN / ExpressRoute /   │
           │  FastConnect / DX       │
           └─────────────────────────┘
```

Elementos transversales (observabilidad, backup, identidad, DNS) en banda horizontal inferior o como columna lateral.

### Multicloud

Un contenedor separado por proveedor con color de borde distinto. Zona central o inferior para elementos compartidos.

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│      OCI         │    │      AWS         │    │      Azure       │
│  (naranja borde) │    │  (naranja borde) │    │  (azul borde)    │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                       │                        │
┌────────┴───────────────────────┴────────────────────────┴──────┐
│                     ZONA COMPARTIDA                             │
│  Identidad federada · Conectividad · Observabilidad            │
│  FinOps · Seguridad · CI-CD · Integración                      │
└────────────────────────────────────────────────────────────────┘
```

### Kubernetes / OKE / EKS / AKS / GKE

```
┌─ Cluster ──────────────────────────────────────────┐
│  ┌─ Control Plane (managed) ─────────────────────┐ │
│  │  API Server · etcd · Controller · Scheduler   │ │
│  └───────────────────────────────────────────────┘ │
│  ┌─ Namespace: prod ──────────────────────────────┐│
│  │  ┌─ Deployment ─┐  ┌─ Service ──┐  ┌─ HPA ──┐ ││
│  │  │  Pod × N     │→ │  ClusterIP │  │        │ ││
│  │  └──────────────┘  └────────────┘  └────────┘ ││
│  └────────────────────────────────────────────────┘│
│  ┌─ Namespace: monitoring ───────────────────────┐ │
│  │  Prometheus · Grafana · Loki · OTel Collector │ │
│  └───────────────────────────────────────────────┘ │
│  Ingress (ALB / AGIC / NGINX) ← [External Traffic] │
└────────────────────────────────────────────────────┘
```

---

## 4. Reglas para ERD relacional

### Estructura de entidad en draw.io

Usa `swimlane` con filas para columnas. Formato recomendado de label:

```
Entidad: NOMBRE_TABLA
─────────────────────
PK  id              INT
    nombre          VARCHAR(100)
    created_at      TIMESTAMP
FK  cliente_id      INT
UK  email           VARCHAR(255)
    activo          BOOLEAN
```

XML base para entidad ERD:

```xml
<mxCell id="ent-cliente" value="CLIENTE" style="shape=table;startSize=30;
  container=1;collapsible=1;childLayout=tableLayout;fixedRows=1;rowLines=0;
  fontStyle=1;align=center;resizeLast=1;fontSize=12;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="240" height="180" as="geometry"/>
</mxCell>
<mxCell id="ent-cliente-pk" value="" style="shape=tableRow;horizontal=0;
  startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;collapsible=0;
  dropTarget=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;fontSize=11;top=0;
  left=0;right=0;bottom=1;" vertex="1" parent="ent-cliente">
  <mxGeometry y="30" width="240" height="30" as="geometry"/>
</mxCell>
```

### Conectores ERD con cardinalidades

```xml
<!-- Uno a muchos -->
<mxCell id="rel-cli-ped" value=""
  style="edgeStyle=entityRelationEdgeStyle;endArrow=ERmanyToOne;
  startArrow=ERmandOne;exitX=1;exitY=0.5;entryX=0;entryY=0.5;"
  edge="1" source="ent-pedido-fk" target="ent-cliente-pk" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

Cardinalidades disponibles: `ERone` · `ERmany` · `ERmandOne` · `ERmanyToOne` · `ERzeroToOne` · `ERoneToMany`.

### Organización por dominio funcional

Agrupa entidades en contenedores por dominio:

```
┌─ Dominio: Clientes ──────┐  ┌─ Dominio: Pedidos ───────┐
│  CLIENTE                 │  │  PEDIDO                  │
│  DIRECCIÓN               │  │  LINEA_PEDIDO            │
│  CONTACTO                │  │  ESTADO_PEDIDO           │
└──────────────────────────┘  └──────────────────────────┘
┌─ Dominio: Productos ─────┐  ┌─ Dominio: Auditoría ─────┐
│  PRODUCTO                │  │  AUDIT_LOG               │
│  CATEGORIA               │  │  CAMBIO_ESTADO           │
│  STOCK                   │  └──────────────────────────┘
└──────────────────────────┘
```

Crea una página `00 Overview ERD` con todas las entidades simplificadas (solo nombre y PK).
Crea páginas por dominio con el detalle completo de columnas, FK y cardinalidades.

---

## 5. Reglas para modelos documentales MongoDB/NoSQL

### Representación de colecciones y documentos

```
┌─ Colección: orders ────────────────────────────────────┐
│  _id: ObjectId                  PK                     │
│  customerId: ObjectId           REF → customers._id    │
│  status: string                                        │
│  createdAt: Date                                       │
│  ┌─ Array: items [ ] ───────────────────────────────┐  │
│  │  productId: ObjectId         REF → products._id  │  │
│  │  quantity: number                                │  │
│  │  price: number                                   │  │
│  │  ┌─ Subdoc: snapshot { } ─────────────────────┐ │  │
│  │  │  name: string            SNAPSHOT           │ │  │
│  │  │  sku: string                                │ │  │
│  │  └────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

### Marcadores de tipo

| Marcador | Significado |
|----------|-------------|
| `EMB` | Subdocumento embebido |
| `REF` | Referencia externa (`ObjectId`) |
| `SNAPSHOT` | Copia desnormalizada en el momento de la operación |
| `[ ]` | Array / lista |
| `{ }` | Subdocumento único |
| `TTL` | Campo con expiración automática |

### Reglas críticas para MongoDB

- No forzar normalización relacional en un modelo documental.
- No convertir automáticamente REF en FK con join.
- Mostrar patrones documentales solo si están justificados en el caso:
  - **Bucket Pattern**: para series temporales o logs
  - **Outlier Pattern**: cuando pocos documentos superan el tamaño típico del array
  - **Materialized Path**: para jerarquías de árbol
  - **Embedded Documents**: subdocumentos en documentos padre
- Indicar índices relevantes: `idx_compuesto(campo1, campo2)` si existen.

---

## 6. Reglas para Terraform / IaC

Cuando la entrada sea código Terraform, el objetivo es representar la **arquitectura resultante**, no la estructura del código.

### Qué extraer del código

| Bloque Terraform | Qué representa en el diagrama |
|------------------|-------------------------------|
| `provider` | Cloud provider / tenant |
| `module` | Componente agrupado (landing zone, VPC, cluster) |
| `resource "aws_vpc"` / `"oci_core_vcn"` | Red contenedora |
| `resource "aws_subnet"` / `"oci_core_subnet"` | Subnet con CIDR |
| `resource "aws_security_group"` / `"oci_core_security_list"` | Reglas de firewall (nota en contenedor) |
| `resource "aws_instance"` / `"oci_core_instance"` | Compute node |
| `resource "aws_db_instance"` / `"oci_database_db_system"` | Base de datos |
| `resource "aws_lb"` / `"oci_load_balancer"` | Load balancer |
| `resource "aws_iam_role"` | IAM / identidad |
| `depends_on` | Conector de dependencia explícita |
| `variable` | Configuración parametrizable (nota) |
| `output` | Valor expuesto (etiqueta en el componente) |
| `locals` | No representa nodo; puede contextualizar etiquetas |

### Qué NO hacer con Terraform

- No mapear cada `resource` como un nodo si son del mismo tipo lógico (ej. 3 subnets → contenedor subnet × 3, no 3 nodos individuales)
- No mostrar la estructura de directorios/módulos como el diagrama
- No omitir relaciones implícitas derivadas de referencias entre recursos

---

## 7. Reglas para diagramas de seguridad y cumplimiento

Cuando el contexto sea enterprise, regulado o multicloud, incluir:

### Segmentación de red
- Distinción clara de zonas: pública / DMZ / privada / datos / gestión
- Firewall entre cada zona
- Direction del tráfico en conectores
- Puertos y protocolos en etiquetas cuando sea relevante para el caso

### Identidad y acceso
- Directorio de identidad principal
- Federación cross-cloud si aplica
- Zonas de confianza (trust boundaries) como contenedores con borde rojo

### Controles a representar cuando aplique
- Gestión de secretos (Vault / Key Vault / OCI Vault / Secrets Manager)
- Cifrado en tránsito: TLS en conectores
- Cifrado en reposo: ícono/nota en nodos de datos
- Logging y auditoría: flecha hacia SIEM o log aggregator
- Bastion / jump host para acceso administrativo

### Nota de validación obligatoria para entornos regulados

Añade siempre en página `99 Leyenda y notas`:
```
⚠ Controles regulatorios (ENS / RGPD / ISO 27001 / PCI-DSS) no verificados en este diagrama.
  Validar con el equipo de seguridad antes de aprobar para producción.
```

---

## 8. Patrones de mejora de diagramas existentes

Cuando el usuario entregue un `.drawio` o XML existente:

### Diagnóstico antes de modificar

1. Identificar páginas existentes y su propósito
2. Listar IDs y detectar duplicados
3. Detectar conectores sin `source` o `target`
4. Detectar elementos fuera de contenedor (huérfanos)
5. Detectar solapamientos visuales
6. Detectar estilos inconsistentes
7. Detectar componentes sin nombre o con nombres genéricos (Node1, Shape2...)
8. Detectar relaciones técnicas incorrectas o incompletas

### Qué preservar obligatoriamente

- Todo el contenido funcional: nodos, relaciones, etiquetas
- Nombres de componentes establecidos por el cliente
- Relaciones técnicas existentes (no cambiar sin evidencia)
- Estructura de páginas si está bien organizada

### Qué mejorar

- Distribución y espaciado (sin solapamientos)
- Normalización de estilos (paleta consistente)
- Agrupación por dominios si no existe
- Corrección de IDs duplicados
- Conexión de conectores huérfanos
- Adición de leyenda si no existe
- Adición de página overview si el diagrama es grande

### Qué reportar al usuario

Lista corta de inconsistencias detectadas antes o después de la mejora:
- Relaciones que podrían estar incompletas
- Componentes con nombre genérico que requieren revisión
- Decisiones técnicas que no pudieron verificarse
