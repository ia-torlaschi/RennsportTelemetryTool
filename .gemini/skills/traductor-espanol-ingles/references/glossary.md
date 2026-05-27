# Glosario técnico ES ↔ EN

Glosario de referencia para traducciones técnicas en los dominios habituales del usuario: Oracle, cloud (OCI/AWS/Azure/GCP), administración de bases de datos, IaC, contenedores, CI/CD, seguridad, compliance y FinOps.

**Cómo usarlo:** consultar antes de fijar terminología en un documento técnico largo. La columna "Notas" indica cuándo conservar el original, cuándo traducir, y los matices.

---

## 1. Bases de datos y administración (Oracle)

| ES | EN | Notas |
|---|---|---|
| base de datos | database | — |
| instancia | instance | — |
| esquema | schema | En BBDD siempre `schema`, no `scheme` |
| tabla | table | — |
| vista | view | — |
| vista materializada | materialized view | — |
| índice | index | plural EN: `indexes` (BBDD) o `indices` (matemático) |
| clave primaria | primary key (PK) | — |
| clave foránea | foreign key (FK) | — |
| restricción | constraint | nunca `restriction` en este contexto |
| disparador | trigger | habitualmente se mantiene `trigger` también en ES |
| procedimiento almacenado | stored procedure | — |
| paquete (PL/SQL) | package | — |
| secuencia | sequence | — |
| tablespace | tablespace | no se traduce |
| segmento | segment | — |
| extensión (de segmento) | extent | en ES también se usa `extent` |
| bloque | block | — |
| redo log | redo log | no se traduce |
| archive log | archive log | no se traduce |
| undo | undo | no se traduce |
| flashback | flashback | no se traduce |
| optimizador | optimizer | — |
| plan de ejecución | execution plan | — |
| recolección de estadísticas | stats gathering | — |
| transacción | transaction | nunca `transition` |
| confirmar / hacer commit | commit | — |
| deshacer / rollback | rollback | habitualmente `rollback` también en ES |
| punto de salvado | savepoint | — |
| bloqueo | lock | — |
| punto muerto / abrazo mortal | deadlock | en ES técnico se usa `deadlock` directamente |
| latencia | latency | — |
| rendimiento | throughput / performance | `throughput`= caudal; `performance`= rendimiento general |
| cuello de botella | bottleneck | — |
| ajuste / tuning | tuning | en ES técnico es habitual `tuning` |
| copia de seguridad | backup | — |
| restauración | restore | — |
| recuperación | recovery | — |
| punto de recuperación | recovery point (RPO) | — |
| tiempo de recuperación | recovery time (RTO) | — |
| alta disponibilidad | high availability (HA) | — |
| recuperación ante desastres | disaster recovery (DR) | — |
| sitio primario / secundario | primary site / standby site | en Oracle: `primary` y `standby` |
| conmutación planificada | switchover | **importante:** `switchover` ≠ `failover` |
| conmutación por error | failover | **automática y no planificada** |
| sitio activo-activo | active-active | — |
| sitio activo-pasivo | active-passive / active-standby | — |
| particionamiento | partitioning | — |
| compresión | compression | — |
| cifrado en reposo | encryption at rest | — |
| cifrado en tránsito | encryption in transit | — |
| cifrado transparente de datos | Transparent Data Encryption (TDE) | — |
| auditoría unificada | unified auditing | — |
| ajuste fino | fine-tuning | — |
| carga de trabajo | workload | — |
| pico de carga | load spike / peak load | — |
| sobrecarga | overload / overhead | `overhead` = sobrecoste/sobrecarga residual; `overload` = saturación |
| espera | wait (event) | en AWR / ASH: `wait events` |

---

## 2. Cloud (multicloud y servicios)

### Términos transversales

| ES | EN | Notas |
|---|---|---|
| nube | cloud | — |
| nube pública / privada / híbrida | public / private / hybrid cloud | — |
| multinube | multicloud | sin guion en EN |
| arrendatario / inquilino | tenant | en OCI: `tenancy` (cuenta/organización) |
| compartimento (OCI) | compartment | no se traduce, es propio de OCI |
| dominio de disponibilidad | availability domain (OCI) | — |
| dominio de fallos | fault domain (OCI) | — |
| zona de disponibilidad | availability zone (AWS, Azure, GCP) | — |
| región | region | — |
| despliegue | deployment | — |
| puesta en marcha / aprovisionamiento | provisioning | — |
| escalado horizontal | horizontal scaling / scale-out | — |
| escalado vertical | vertical scaling / scale-up | — |
| autoescalado | autoscaling | — |
| balanceador de carga | load balancer | — |
| punto de conexión | endpoint | habitualmente se mantiene `endpoint` |
| pasarela | gateway | — |
| pasarela NAT | NAT gateway | — |
| red virtual | virtual network / VCN (OCI) / VPC (AWS, GCP) / VNet (Azure) | — |
| subred | subnet | — |
| tabla de rutas | route table | — |
| lista de seguridad | security list (OCI) | — |
| grupo de seguridad | security group (AWS) / NSG (Azure) | — |
| almacenamiento de objetos | object storage | — |
| almacenamiento de bloques | block storage / block volume (OCI) | — |
| almacenamiento de archivos | file storage | — |
| cubo / contenedor | bucket | en OCI: `bucket`; en Azure: `container` (objeto), `blob` |
| capacidad de cómputo | compute | — |
| forma (OCI) | shape | no se traduce |
| imagen (de instancia) | image | — |
| plantilla / blueprint | template / blueprint | — |
| huella (de despliegue) | footprint | — |
| consumo / facturación | usage / billing | — |
| factura | invoice | — |
| crédito (universal credit) | credit | — |
| reservación de capacidad | reserved capacity | — |
| precio bajo demanda | on-demand pricing | — |
| precio comprometido | committed-use pricing | — |
| spot / preemptible | spot / preemptible | no se traduce |

### Productos cuyos nombres NO se traducen

`Oracle Autonomous Database`, `Oracle Exadata`, `Oracle Cloud Infrastructure (OCI)`, `Oracle Database@Azure`, `Oracle Database@Google Cloud`, `Oracle Database@AWS`, `Amazon S3`, `Amazon RDS`, `AWS Lambda`, `Microsoft Entra ID` (antes Azure AD), `Azure Blob Storage`, `Google BigQuery`, `Google Cloud Run`, `Anthos`, `Apigee`, `Vertex AI`, `OCI Generative AI`.

---

## 3. Contenedores, Kubernetes, IaC

| ES | EN | Notas |
|---|---|---|
| contenedor | container | — |
| imagen de contenedor | container image | — |
| registro de imágenes | image registry | — |
| orquestador | orchestrator | — |
| nodo | node | — |
| pod | pod | no se traduce |
| espacio de nombres | namespace | — |
| despliegue (recurso K8s) | Deployment | mantener mayúscula al referirse al recurso K8s |
| servicio (recurso K8s) | Service | idem |
| ingress | ingress | no se traduce |
| volumen persistente | persistent volume (PV) | — |
| reclamación de volumen persistente | persistent volume claim (PVC) | — |
| sidecar | sidecar | no se traduce |
| malla de servicios | service mesh | — |
| infraestructura como código | infrastructure as code (IaC) | — |
| módulo (Terraform) | module | — |
| estado (Terraform) | state | — |
| plan (Terraform) | plan | — |
| aplicar (Terraform) | apply | — |
| destruir (Terraform) | destroy | — |
| variable | variable | — |
| salida | output | — |
| zona de aterrizaje | landing zone | habitual mantener `landing zone` también en ES |

---

## 4. CI/CD, DevOps, observabilidad

| ES | EN | Notas |
|---|---|---|
| integración continua | continuous integration (CI) | — |
| entrega continua | continuous delivery (CD) | — |
| despliegue continuo | continuous deployment (CD) | — |
| canalización / pipeline | pipeline | habitual `pipeline` también en ES |
| repositorio | repository / repo | — |
| rama | branch | — |
| fusionar | merge | — |
| solicitud de incorporación | pull request (PR) | habitual mantener `pull request` o `PR` |
| revisión de código | code review | — |
| compilación | build | — |
| ejecución / corrida | run | — |
| versión | version / release | `release` = lanzamiento/entrega |
| etiqueta | tag | — |
| instantánea | snapshot | — |
| reversión | rollback | habitual mantener `rollback` |
| despliegue azul-verde | blue-green deployment | — |
| despliegue canario | canary deployment | — |
| característica de bandera / feature flag | feature flag | habitual mantener |
| trazabilidad | traceability | — |
| monitorización | monitoring | en LatAm: `monitoreo` |
| observabilidad | observability | — |
| traza | trace | — |
| métrica | metric | — |
| registro / log | log | habitual `log` también en ES |
| panel | dashboard | habitual `dashboard` |
| alerta | alert | — |
| umbral | threshold | — |
| incidencia / incidente | incident / issue | `incident` = fallo operativo; `issue` = elemento de tracking |
| postmortem | postmortem | habitual mantener |
| análisis de causa raíz | root cause analysis (RCA) | — |

---

## 5. Seguridad y compliance

| ES | EN | Notas |
|---|---|---|
| seguridad | security | — |
| identidad y acceso | identity and access management (IAM) | — |
| inicio de sesión único | single sign-on (SSO) | — |
| autenticación multifactor | multi-factor authentication (MFA) | — |
| federación | federation | — |
| privilegio mínimo | least privilege | — |
| principio de separación de funciones | segregation of duties (SoD) | — |
| endurecimiento | hardening | habitual `hardening` también en ES |
| cumplimiento normativo | compliance | — |
| gobernanza | governance | — |
| auditoría | audit / auditing | — |
| análisis de riesgos | risk assessment | — |
| evaluación de impacto | impact assessment | — |
| amenaza | threat | — |
| vulnerabilidad | vulnerability | — |
| superficie de ataque | attack surface | — |
| brecha de seguridad / fuga de datos | data breach | — |
| dato personal | personal data / PII | en EN técnico-legal: `personally identifiable information` |
| anonimización | anonymization | — |
| seudonimización | pseudonymization | — |
| RGPD | GDPR | **misma normativa, distinto acrónimo** |
| LOPDGDD | Spain's Organic Law on Personal Data Protection (LOPDGDD) | en EN expandir en primera mención |
| ENS | ENS (Spain's National Security Framework) | sin acrónimo EN, expandir |
| ISO 27001 | ISO 27001 | idéntico |
| NIST | NIST | idéntico |
| SOC 2 | SOC 2 | idéntico |
| PCI DSS | PCI DSS | idéntico |
| HIPAA | HIPAA | idéntico |
| cifrado | encryption | — |
| clave (criptográfica) | key | — |
| par de claves | key pair | — |
| certificado | certificate | — |
| autoridad certificadora | certificate authority (CA) | — |
| firma digital | digital signature | — |
| token | token | — |
| ámbito (OAuth) | scope | — |
| concesión (OAuth) | grant | — |
| portador (token) | bearer | — |

---

## 6. FinOps y económico-financiero

| ES | EN | Notas |
|---|---|---|
| FinOps | FinOps | idéntico |
| coste | cost | — |
| coste operativo | operating cost / OPEX | — |
| coste de inversión | capital expenditure / CAPEX | — |
| coste total de propiedad | total cost of ownership (TCO) | — |
| retorno de la inversión | return on investment (ROI) | — |
| ahorro | savings | — |
| optimización de costes | cost optimization | — |
| asignación de costes | cost allocation | — |
| centro de coste | cost center | — |
| etiquetado | tagging | — |
| presupuesto | budget | — |
| previsión | forecast | — |
| desviación | variance | — |
| consumo a la vista | usage visibility | — |
| ejercicio fiscal | fiscal year (FY) | nunca `exercise` |
| trimestre | quarter (Q1, Q2, Q3, Q4) | — |
| facturación recurrente anual | annual recurring revenue (ARR) | — |
| facturación recurrente mensual | monthly recurring revenue (MRR) | — |

---

## 7. IA, ML, datos

| ES | EN | Notas |
|---|---|---|
| inteligencia artificial | artificial intelligence (AI) | — |
| aprendizaje automático | machine learning (ML) | — |
| aprendizaje profundo | deep learning | — |
| modelo | model | — |
| entrenamiento | training | — |
| inferencia | inference | — |
| ajuste fino | fine-tuning | — |
| IA generativa | generative AI / GenAI | — |
| modelo de lenguaje | language model | — |
| modelo de lenguaje grande | large language model (LLM) | — |
| ingeniería de prompts | prompt engineering | — |
| recuperación aumentada con generación | retrieval-augmented generation (RAG) | — |
| incrustación / embedding | embedding | habitual `embedding` también en ES |
| búsqueda vectorial | vector search | — |
| base de datos vectorial | vector database | — |
| almacén de vectores | vector store | — |
| canalización de datos | data pipeline | — |
| ingesta de datos | data ingestion | — |
| limpieza de datos | data cleansing / data cleaning | — |
| almacén de datos | data warehouse | — |
| lago de datos | data lake | — |
| lakehouse | lakehouse | no se traduce |
| linaje de datos | data lineage | — |
| catálogo de datos | data catalog | — |
| gobernanza de datos | data governance | — |

---

## 8. Términos de gestión de proyectos y comunicación corporativa

| ES | EN | Notas |
|---|---|---|
| ámbito / alcance | scope | — |
| hito | milestone | — |
| entregable | deliverable | — |
| parte interesada | stakeholder | habitual mantener `stakeholder` |
| patrocinador | sponsor | — |
| comité de dirección | steering committee | — |
| acta | minutes | — |
| memorándum | memorandum / memo | — |
| pliego / propuesta | proposal / SoW (statement of work) | — |
| acuerdo de nivel de servicio | service level agreement (SLA) | — |
| objetivo de nivel de servicio | service level objective (SLO) | — |
| ejercicio (año fiscal) | fiscal year | **nunca `exercise`** |
| panel ejecutivo | executive dashboard | — |
| resumen ejecutivo | executive summary | — |
| caso de negocio | business case | — |
| hoja de ruta | roadmap | — |
| punto de control | checkpoint / gate | — |
| riesgo | risk | — |
| dependencia | dependency | — |
| bloqueante | blocker | — |
| seguimiento | tracking / follow-up | — |
| informe | report | — |
| postmortem / retrospectiva | postmortem / retrospective | — |
