# DrawIO Vendor Sources
# Archivo de conocimiento del proyecto — DrawIO Specialist
# Mantenido por: Torlaschi Consulting
# Última revisión: mayo 2025
# Uso: referencia de fuentes oficiales, iconografía, patrones y mejores prácticas por vendor

---

## Cómo usar este archivo

Este archivo se activa cuando el diagrama involucra uno de los vendors listados.
Prioridad de consulta: documentación oficial > reference architectures > community guides verificados.
Si una URL no está disponible en la sesión, indicarlo y trabajar con el material aportado.

---

## 1. Oracle Cloud Infrastructure (OCI)

### Fuentes primarias

| Recurso | URL |
|---------|-----|
| Oracle Architecture Center | https://docs.oracle.com/solutions/ |
| OCI Architecture Diagram Toolkit | https://docs.oracle.com/en-us/iaas/Content/General/Reference/graphicsfordiagrams.htm |
| OCI Documentation | https://docs.oracle.com/en-us/iaas/Content/home.htm |
| OCI Reference Architectures | https://docs.oracle.com/solutions/?type=reference-architectures |
| OCI Landing Zones | https://github.com/oracle-quickstart/oci-landing-zones |
| OCI Well-Architected Framework | https://docs.oracle.com/en-us/iaas/Content/cloud-adoption-framework/home.htm |
| OCI Cloud Adoption Framework | https://docs.oracle.com/en-us/iaas/Content/cloud-adoption-framework/home.htm |
| Oracle Database Documentation | https://docs.oracle.com/en/database/ |
| Oracle Exadata Documentation | https://docs.oracle.com/en/engineered-systems/exadata-database-machine/ |
| Oracle Autonomous Database | https://docs.oracle.com/en/cloud/paas/autonomous-database/ |
| Oracle GoldenGate | https://docs.oracle.com/en/middleware/goldengate/ |
| Oracle Data Guard | https://docs.oracle.com/en/database/oracle/oracle-database/19/sbydb/ |
| Oracle Zero Downtime Migration | https://www.oracle.com/database/zero-downtime-migration/ |
| Oracle Database@Azure | https://www.oracle.com/cloud/azure/oracle-database-at-azure/ |
| Oracle Database@Google Cloud | https://www.oracle.com/cloud/google/ |
| OCI Multicloud Docs | https://docs.oracle.com/en-us/iaas/Content/multicloud/home.htm |
| OCI FastConnect | https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/fastconnect.htm |
| OCI Security Zones | https://docs.oracle.com/en-us/iaas/security-zone/home.htm |
| OCI IAM | https://docs.oracle.com/en-us/iaas/Content/Identity/home.htm |

### Iconografía y shapes draw.io

- El **OCI Architecture Diagram Toolkit** incluye stencils SVG descargables para draw.io.
- Descarga oficial: https://docs.oracle.com/en-us/iaas/Content/General/Reference/graphicsfordiagrams.htm
- Formato: archivos `.xml` de librerías draw.io importables directamente.
- Si los stencils no están disponibles en la sesión, usar rectángulos genéricos con nombre oficial del servicio.
- Nunca inventar `shape=mxgraph.oracle.*` sin verificar disponibilidad.

### Servicios OCI clave para diagramas

**Networking:** VCN · Subnet (pública/privada) · Internet Gateway · NAT Gateway · Service Gateway · DRG (Dynamic Routing Gateway) · FastConnect · Site-to-Site VPN · Load Balancer · Network Firewall · DNS

**Compute:** VM · BM · Autoscaling · Container Instances · OKE (Kubernetes)

**Storage:** Object Storage · Block Volume · File Storage · Archive Storage

**Database:** Autonomous Database (Serverless / Dedicated / Exadata) · DB System (VM/BM) · Exadata Cloud Service · MySQL HeatWave · NoSQL Database · GoldenGate · Data Guard

**Seguridad:** IAM · Vault · KMS · Security Zones · Cloud Guard · WAF · Bastion · Certificates

**Observabilidad:** Logging · Monitoring · Events · Notifications · Application Performance Monitoring · Ops Insights

**Integración:** API Gateway · OCI Integration (OIC) · Streaming · Queue · Functions · Data Flow · Data Integration

**IA/ML:** OCI Generative AI · OCI AI Services · Data Science · AI Vector Search (Oracle 23ai)

### Contenedores y agrupación OCI

```
Tenancy
  └── Compartment (anidables hasta 6 niveles)
        └── Region
              └── Availability Domain (AD-1, AD-2, AD-3)
                    └── Fault Domain
                          └── VCN
                                └── Subnet (pública / privada / delegada)
```

### Patrones OCI frecuentes

- **Landing Zone**: compartments de seguridad, network, aplicaciones y datos + logging centralizado + Cloud Guard
- **Hub-and-Spoke**: DRG central + VCNs spoke por workload/entorno
- **Multicloud OCI-Azure**: Oracle Interconnect for Azure + Entra ID federation + Oracle Database@Azure
- **Multicloud OCI-GCP**: Google Cloud Interconnect + ODB@Google Cloud
- **HA activo-activo**: 2+ ADs con Data Guard o RAC + Load Balancer
- **DR cross-region**: Data Guard far sync + Object Storage cross-region replication
- **Exadata dedicada**: Exadata Infrastructure → VM Cluster → CDB → PDB

---

## 2. Amazon Web Services (AWS)

### Fuentes primarias

| Recurso | URL |
|---------|-----|
| AWS Architecture Center | https://aws.amazon.com/architecture/ |
| AWS Well-Architected Framework | https://aws.amazon.com/architecture/well-architected/ |
| AWS Architecture Icons | https://aws.amazon.com/architecture/icons/ |
| AWS Prescriptive Guidance | https://aws.amazon.com/prescriptive-guidance/ |
| AWS Reference Architectures | https://aws.amazon.com/architecture/reference-architecture-diagrams/ |
| AWS Documentation | https://docs.aws.amazon.com/ |
| AWS Solutions Library | https://aws.amazon.com/solutions/ |
| AWS Landing Zone / Control Tower | https://docs.aws.amazon.com/controltower/latest/userguide/what-is-control-tower.html |
| AWS Organizations | https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html |
| Amazon VPC | https://docs.aws.amazon.com/vpc/latest/userguide/ |
| Amazon EKS | https://docs.aws.amazon.com/eks/latest/userguide/ |
| Amazon RDS | https://docs.aws.amazon.com/rds/latest/userguide/ |
| Amazon Aurora | https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/ |

### Iconografía y shapes draw.io

- AWS publica icon packs oficiales en: https://aws.amazon.com/architecture/icons/
- Formatos disponibles: SVG · PNG · Sketch · draw.io asset library (`.xml`)
- El archivo draw.io oficial se descarga desde esa URL.
- Shapes draw.io: `shape=mxgraph.aws4.*` — verificar que la librería esté cargada antes de usar.
- Si no está disponible, usar rectángulos con nombre oficial del servicio.

### Servicios AWS clave para diagramas

**Networking:** VPC · Subnet (pública/privada/aislada) · Internet Gateway · NAT Gateway · Transit Gateway · Direct Connect · VPN Gateway · Route 53 · CloudFront · WAF · Shield · ELB (ALB/NLB/GLB) · Security Group · NACL

**Compute:** EC2 · Auto Scaling Group · Lambda · ECS · EKS · Fargate · Elastic Beanstalk · Outposts

**Storage:** S3 · EBS · EFS · FSx · S3 Glacier · Storage Gateway · Backup

**Database:** RDS · Aurora · DynamoDB · ElastiCache · Redshift · Neptune · DocumentDB · Keyspaces · MemoryDB · Database Migration Service (DMS)

**Seguridad:** IAM · Cognito · KMS · Secrets Manager · ACM · GuardDuty · Security Hub · Inspector · Macie · CloudTrail · Config · Control Tower

**Observabilidad:** CloudWatch · X-Ray · CloudTrail · AWS Config · Trusted Advisor · Compute Optimizer

**Integración:** API Gateway · SNS · SQS · EventBridge · Step Functions · AppSync · Kinesis · MSK · MQ

**DevOps:** CodePipeline · CodeBuild · CodeDeploy · CodeCommit · CDK · CloudFormation

### Contenedores y agrupación AWS

```
Organization (AWS Organizations)
  └── Management Account
  └── Organizational Unit (OU)
        └── AWS Account
              └── Region
                    └── Availability Zone (AZ-a, AZ-b, AZ-c)
                          └── VPC
                                └── Subnet (pública / privada / data)
                                      └── Recursos
```

### Patrones AWS frecuentes

- **Landing Zone / Control Tower**: management account + security OU + sandbox OU + workload OUs + log archive + audit accounts
- **Multi-VPC hub-spoke**: Transit Gateway central + VPCs spoke por entorno o workload
- **Three-tier web**: ALB → EC2/ECS (privada) → RDS Multi-AZ (data subnet)
- **Serverless**: API Gateway → Lambda → DynamoDB / Aurora Serverless
- **EKS baseline**: EKS control plane + node groups en subnets privadas + ALB Ingress + Karpenter + Fargate profiles
- **DR activo-pasivo**: Route 53 failover + Aurora Global Database + S3 Cross-Region Replication

---

## 3. Google Cloud Platform (GCP)

### Fuentes primarias

| Recurso | URL |
|---------|-----|
| Google Cloud Architecture Center | https://cloud.google.com/architecture |
| Google Cloud Architecture Framework | https://cloud.google.com/architecture/framework |
| Google Cloud Icons | https://cloud.google.com/icons |
| Google Cloud Documentation | https://cloud.google.com/docs |
| Google Cloud Solutions | https://cloud.google.com/solutions |
| Google Cloud Reference Architectures | https://cloud.google.com/architecture#reference-architectures |
| Google Cloud Landing Zones | https://cloud.google.com/architecture/landing-zones |
| Google Cloud Networking | https://cloud.google.com/vpc/docs |
| GKE Documentation | https://cloud.google.com/kubernetes-engine/docs |
| BigQuery Documentation | https://cloud.google.com/bigquery/docs |
| Vertex AI Documentation | https://cloud.google.com/vertex-ai/docs |
| Cloud Spanner | https://cloud.google.com/spanner/docs |
| AlloyDB | https://cloud.google.com/alloydb/docs |
| Oracle Database@Google Cloud | https://cloud.google.com/oracle/database |
| Google Cloud Interconnect | https://cloud.google.com/network-connectivity/docs/interconnect |

### Iconografía y shapes draw.io

- Iconos oficiales GCP: https://cloud.google.com/icons (SVG · PNG)
- draw.io incluye librería GCP nativa: activar en Extras → Edit Diagram o en la barra de shapes.
- Shapes: `shape=mxgraph.gcp2.*` — verificar disponibilidad antes de usar.
- Si no está disponible, usar rectángulos con nombre oficial del servicio.

### Servicios GCP clave para diagramas

**Networking:** VPC (global) · Subnet (regional) · Cloud Router · Cloud NAT · Cloud DNS · Cloud CDN · Cloud Armor · Load Balancing (Global/Regional/Internal) · Cloud Interconnect · VPN · Private Service Connect · Shared VPC · VPC Service Controls · Network Intelligence Center

**Compute:** Compute Engine · GKE · Cloud Run · Cloud Functions · App Engine · Anthos · Bare Metal Solution

**Storage:** Cloud Storage (GCS) · Persistent Disk · Filestore · Cloud Storage FUSE

**Database:** Cloud SQL · Cloud Spanner · AlloyDB · BigQuery · Firestore · Bigtable · Memorystore · Datastore · Oracle Database@GCP

**Seguridad:** IAM · Cloud Identity · BeyondCorp · Secret Manager · Cloud KMS · Security Command Center · Chronicle · VPC Service Controls · Binary Authorization · Cloud Audit Logs

**Observabilidad:** Cloud Monitoring · Cloud Logging · Cloud Trace · Cloud Profiler · Error Reporting · Log Analytics

**Datos / Analytics:** BigQuery · Dataflow · Dataproc · Pub/Sub · Composer (Airflow) · Looker · Looker Studio · Vertex AI · Data Catalog · Dataplex

**Integración / Mensajería:** Pub/Sub · Cloud Tasks · Workflows · Eventarc · Apigee · Cloud Endpoints

**DevOps:** Cloud Build · Cloud Deploy · Artifact Registry · Source Repositories · GKE Autopilot

### Contenedores y agrupación GCP

```
Organization
  └── Folder (anidables)
        └── Project
              └── Region
                    └── Zone (zone-a, zone-b, zone-c)
                          └── VPC (global)
                                └── Subnet (regional)
                                      └── Recursos
```

GCP VPC es **global** — una VPC puede tener subnets en múltiples regiones. Representarlo explícitamente en el diagrama.

### Patrones GCP frecuentes

- **Landing Zone Hub-and-Spoke**: Shared VPC + host project + service projects por entorno/equipo
- **GKE Baseline**: GKE Autopilot/Standard + Workload Identity + Cloud Armor + Ingress GCLB + VPC-native networking
- **Data Platform**: Pub/Sub → Dataflow → BigQuery → Looker/Vertex AI
- **Multicloud OCI-GCP**: Google Cloud Interconnect + Oracle Database@GCP + federated identity con Cloud Identity
- **Serverless**: API Gateway → Cloud Functions/Cloud Run → Firestore/Cloud SQL
- **DR activo-pasivo**: Cloud SQL multi-region replica + Cloud Storage multi-region bucket + Traffic Director failover

---

## 4. Microsoft Azure

### Fuentes primarias

| Recurso | URL |
|---------|-----|
| Azure Architecture Center | https://learn.microsoft.com/en-us/azure/architecture/ |
| Azure Well-Architected Framework | https://learn.microsoft.com/en-us/azure/well-architected/ |
| Azure Architecture Icons | https://learn.microsoft.com/en-us/azure/architecture/icons/ |
| Azure Cloud Adoption Framework (CAF) | https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ |
| Azure Documentation | https://learn.microsoft.com/en-us/azure/ |
| Azure Reference Architectures | https://learn.microsoft.com/en-us/azure/architecture/browse/ |
| Azure Landing Zones | https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/ |
| Azure Virtual Network | https://learn.microsoft.com/en-us/azure/virtual-network/ |
| Azure Kubernetes Service (AKS) | https://learn.microsoft.com/en-us/azure/aks/ |
| Azure SQL | https://learn.microsoft.com/en-us/azure/azure-sql/ |
| Oracle Database@Azure | https://learn.microsoft.com/en-us/azure/oracle/ |
| Microsoft Entra ID | https://learn.microsoft.com/en-us/entra/identity/ |
| Azure Firewall | https://learn.microsoft.com/en-us/azure/firewall/ |
| Azure ExpressRoute | https://learn.microsoft.com/en-us/azure/expressroute/ |

### Iconografía y shapes draw.io

- Azure publica icon sets oficiales: https://learn.microsoft.com/en-us/azure/architecture/icons/
- Formato: SVG descargable en zip con categorías.
- draw.io incluye librería Azure nativa: activar en la barra de shapes.
- Shapes: `shape=mxgraph.azure2.*` — verificar disponibilidad antes de usar.
- Si no está disponible, usar rectángulos con nombre oficial del servicio.

### Servicios Azure clave para diagramas

**Networking:** Virtual Network (VNet) · Subnet · Network Security Group (NSG) · Application Security Group (ASG) · Azure Firewall · Azure Bastion · ExpressRoute · VPN Gateway · Virtual WAN · Azure Front Door · Application Gateway (WAF) · Load Balancer · Traffic Manager · Private Endpoint · Private DNS Zone · Azure DNS · DDoS Protection

**Compute:** Virtual Machines · VM Scale Sets · AKS · App Service · Azure Functions · Container Apps · Azure Spring Apps · Azure Batch

**Storage:** Blob Storage · Azure Files · Queue Storage · Table Storage · Data Lake Storage Gen2 · Azure Backup · Site Recovery

**Database:** Azure SQL Database · SQL Managed Instance · Azure Database for PostgreSQL / MySQL · Cosmos DB · Azure Cache for Redis · Azure Synapse Analytics · Azure Data Explorer · Oracle Database@Azure · SQL Server on VM

**Seguridad:** Microsoft Entra ID · Azure AD B2C · Managed Identity · Key Vault · Azure Policy · Microsoft Defender for Cloud · Microsoft Sentinel · Privileged Identity Management (PIM) · Conditional Access · Azure RBAC

**Observabilidad:** Azure Monitor · Log Analytics · Application Insights · Azure Advisor · Service Health · Azure Dashboards · Grafana (Azure Managed)

**Datos / Analytics:** Azure Synapse · Data Factory · Azure Databricks · Event Hubs · Service Bus · Azure Stream Analytics · Purview · Power BI Embedded

**Integración:** API Management · Logic Apps · Service Bus · Event Grid · Event Hubs · Azure Integration Services

**DevOps:** Azure DevOps · GitHub Actions (integrado) · Azure Container Registry · Artifact Registry · Azure Policy as Code

### Contenedores y agrupación Azure

```
Tenant (Entra ID)
  └── Management Group (anidables)
        └── Subscription
              └── Resource Group
                    └── Region
                          └── Availability Zone (1, 2, 3)
                                └── Virtual Network (VNet)
                                      └── Subnet
                                            └── Recursos
```

### Patrones Azure frecuentes

- **Landing Zone (CAF)**: Management Groups (Platform / Landing Zones / Sandbox) + subscriptions Connectivity + Identity + Management + workload subscriptions
- **Hub-and-Spoke**: Hub VNet (Azure Firewall + Bastion + VPN/ExpressRoute) + spoke VNets por workload con VNet Peering
- **Virtual WAN**: para múltiples regiones y conectividad simplificada; reemplaza hub-spoke manual
- **AKS Baseline**: AKS private cluster + Azure CNI + Azure Firewall egress + Application Gateway Ingress + Workload Identity + Azure Monitor + Defender for Containers
- **Oracle Database@Azure**: Oracle Exadata X9M en Azure datacenter + ExpressRoute Oracle Interconnect + Entra ID federation con OCI IAM
- **Multicloud OCI-Azure**: Oracle Interconnect (FastConnect + ExpressRoute) + Entra ID ↔ OCI IAM SAML federation
- **DR activo-pasivo**: Azure Site Recovery + Azure Backup + Traffic Manager geographic routing + paired regions

---

## 5. Kubernetes / CNCF

### Fuentes primarias

| Recurso | URL |
|---------|-----|
| Kubernetes Documentation | https://kubernetes.io/docs/ |
| CNCF Landscape | https://landscape.cncf.io/ |
| AKS Documentation | https://learn.microsoft.com/en-us/azure/aks/ |
| EKS Documentation | https://docs.aws.amazon.com/eks/latest/userguide/ |
| GKE Documentation | https://cloud.google.com/kubernetes-engine/docs |
| OKE Documentation | https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm |
| Istio | https://istio.io/latest/docs/ |
| Helm | https://helm.sh/docs/ |
| Karpenter | https://karpenter.sh/docs/ |
| Prometheus | https://prometheus.io/docs/ |
| Grafana | https://grafana.com/docs/ |

### Componentes Kubernetes para diagramas

**Control plane:** API Server · etcd · Controller Manager · Scheduler · Cloud Controller Manager

**Worker nodes:** kubelet · kube-proxy · Container Runtime (containerd)

**Workloads:** Pod · Deployment · StatefulSet · DaemonSet · Job · CronJob · ReplicaSet

**Networking:** Service (ClusterIP / NodePort / LoadBalancer) · Ingress · IngressClass · NetworkPolicy · EndpointSlice · CoreDNS

**Storage:** PersistentVolume (PV) · PersistentVolumeClaim (PVC) · StorageClass · VolumeSnapshot

**Configuración:** ConfigMap · Secret · ServiceAccount · RBAC (Role / ClusterRole / RoleBinding)

**Observabilidad:** Metrics Server · Prometheus · Grafana · Loki · Jaeger / Tempo · OpenTelemetry Collector

**Service Mesh:** Istio (Pilot/Envoy/Ingress/Egress Gateway) · Linkerd · Cilium

### Agrupación Kubernetes en diagramas

```
Cluster
  └── Namespace
        └── Workload (Deployment / StatefulSet)
              └── Pod
                    └── Container(s)
```

Distinguir siempre: control plane (managed o self-hosted) / data plane / ingress layer / service mesh / observabilidad.

---

## 6. Convenciones de color por vendor (para consistencia entre diagramas)

| Vendor | Color de contenedor recomendado | HEX sugerido |
|--------|--------------------------------|--------------|
| OCI | Naranja corporativo | `#F80000` (borde) / `#FFF3EF` (fondo) |
| AWS | Naranja AWS | `#FF9900` (borde) / `#FFF8F0` (fondo) |
| GCP | Azul Google | `#4285F4` (borde) / `#EEF3FD` (fondo) |
| Azure | Azul Microsoft | `#0078D4` (borde) / `#EFF6FC` (fondo) |
| On-premise | Gris | `#6E6E6E` (borde) / `#F5F5F5` (fondo) |
| Kubernetes | Azul CNCF | `#326CE5` (borde) / `#EDF2FD` (fondo) |
| Seguridad (cualquier cloud) | Rojo suave | `#C00000` (borde) / `#FFF0F0` (fondo) |
| Datos / BD | Verde | `#107C10` (borde) / `#F0FFF0` (fondo) |
| Identidad | Morado | `#7719AA` (borde) / `#F7F0FC` (fondo) |
| Zona neutra / compartida | Gris medio | `#404040` (borde) / `#FAFAFA` (fondo) |

---

## 7. Checklist de componentes enterprise multicloud

Usar como guía para verificar completitud en diagramas de arquitectura enterprise:

### Networking
- [ ] Redes y subredes (pública / privada / datos / gestión)
- [ ] Conectividad privada (FastConnect / ExpressRoute / Direct Connect / Cloud Interconnect)
- [ ] VPN de respaldo
- [ ] Firewall perimetral y reglas de seguridad
- [ ] DNS (interno y externo)
- [ ] Balanceadores de carga (externos e internos)
- [ ] CDN / WAF / DDoS (si aplica)

### Identidad y acceso
- [ ] Directorio de identidad principal
- [ ] Federación cross-cloud (SAML / OIDC)
- [ ] Gestión de privilegios (PIM / PAM)
- [ ] Managed Identities / Instance Principals / Service Accounts

### Seguridad
- [ ] Gestión de secretos y certificados
- [ ] Cifrado en tránsito y reposo
- [ ] Logging y auditoría centralizada
- [ ] SIEM / CSPM si aplica
- [ ] Security Zones / Defender / Security Command Center

### Datos
- [ ] Bases de datos primarias
- [ ] Replicación y alta disponibilidad
- [ ] Backup (frecuencia, retención, destino)
- [ ] DR con RPO/RTO si están definidos
- [ ] Flujos de datos y ETL/ELT si aplica

### Observabilidad
- [ ] Métricas, logs y trazas
- [ ] Alertas y notificaciones
- [ ] Dashboards operativos

### DevOps / Gestión
- [ ] CI/CD pipeline
- [ ] Registro de contenedores
- [ ] IaC (Terraform / Ansible / ARM / Deployment Manager)
- [ ] Gestión de costes / FinOps

---

## 8. Supuestos comunes y notas de validación

Cuando el diagrama incluya estos elementos, añadir nota de validación:

- **Oracle Database@Azure / ODB@GCP**: verificar región de disponibilidad actual con el cliente. La cobertura geográfica se expande continuamente.
- **Latencia de Oracle Interconnect**: típicamente <2ms entre OCI y Azure en regiones colocalizadas, pero confirmar con documentación vigente según región.
- **Límites de servicio**: no afirmar en el diagrama límites concretos (número de VCNs, IPs, instancias) sin citar fuente oficial actualizada.
- **SKUs y tipos de instancia**: verificar disponibilidad por región antes de incluir en diagramas de sizing.
- **Conectividad multicloud gratuita**: el Oracle Interconnect tiene condiciones específicas; no asumir gratuidad sin verificar pricing oficial actualizado.
