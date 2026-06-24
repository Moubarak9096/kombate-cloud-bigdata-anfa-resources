```markdown
# Rendu Séance 3

**Nom et prénom :** KOMBATE GARIBA Moubarak  
**Identifiant GitHub :** Moubarak9096  
**Date de soumission :** 24/06/2026

---

## Résumé de la séance

Kind a été installé et configuré, un cluster Kubernetes nommé `anfa` a été créé avec succès. Le namespace `anfa` a été configuré, puis MinIO a été déployé via 3 manifestes YAML (PVC, Deployment, Service). Les mécanismes de self-healing ont été observés après suppression manuelle d'un pod, le scaling a été testé de 1 à 3 replicas, et l'Ingress Controller nginx a été activé pour exposer les services.

---

## Étapes principales

1. Installation de Kind et kubectl, création du cluster `anfa`.
2. Création du namespace `anfa` et configuration de kubectl.
3. Déploiement de MinIO via 3 manifestes YAML (PVC, Deployment, Service).
4. Observation du self-healing après suppression manuelle d'un pod.
5. Scaling du Deployment de 1 à 3 replicas, puis retour à 1.
6. Activation de l'Ingress Controller nginx.

---

## Captures d'écran

### Console MinIO accessible via port-forward

![Console MinIO](captures/console-minio.png)  

### Self-healing observé

![Pod recréé](captures/self-healing.png)

### Scaling à 3 replicas

![3 replicas MinIO](captures/scaling-3-replicas.png)

---

## Réponses aux exercices d'application

### Exercice 1 : QCM conceptuel

**1.1** – **Réponse B** (Kubernetes orchestre des conteneurs sur un cluster de machines, en s'appuyant sur un container runtime comme containerd, Docker ou CRI-O).  
*Justification* : Kubernetes est un orchestrateur qui s'appuie sur des runtimes de conteneurs pour exécuter les pods, et ne remplace pas Docker ni la conteneurisation.

**1.2** – **Réponse B** (etcd).  
*Justification* : etcd est le datastore distribué de Kubernetes qui stocke l'état complet et persistant du cluster (configuration, secrets, état des ressources).

**1.3** – **Réponse C** (Scheduler).  
*Justification* : Le Scheduler est le composant responsable de l'affectation des nouveaux pods aux nœuds disponibles, en fonction des ressources et des contraintes spécifiées.

**1.4** – **Réponse C** (À l'API Server, qui est le point d'entrée unique du cluster).  
*Justification* : `kubectl` communique toujours avec l'API Server, qui est l'interface unique et centralisée pour toutes les opérations sur le cluster.

**1.5** – **Réponse B** (Le Deployment recrée immédiatement un nouveau pod pour respecter l'état souhaité).  
*Justification* : Le Deployment gère un ReplicaSet qui assure que le nombre de pods spécifié dans `replicas` est toujours maintenu, même après suppression manuelle d'un pod.

**1.6** – **Réponse D** (Ingress).  
*Justification* : Ingress expose les services HTTP/HTTPS depuis l'extérieur du cluster en utilisant des règles de routage, sans nécessiter un load balancer cloud ni exposer de ports NodePort.

**1.7** – **Réponse B** (Elle modifie l'état souhaité du Deployment à 5 replicas ; Kubernetes converge vers ce nombre).  
*Justification* : La commande `scale` ajuste le champ `replicas` du Deployment, et Kubernetes s'assure automatiquement que le nombre de pods en cours d'exécution correspond à cette nouvelle valeur.

**1.8** – **Réponse B** (À isoler logiquement les ressources pour séparer par équipe, environnement ou application).  
*Justification* : Les Namespaces permettent de partitionner un cluster en environnements virtuels isolés, facilitant la gestion des ressources et le contrôle d'accès.

**1.9** – **Réponse B** (Des conteneurs Docker).  
*Justification* : Kind (Kubernetes in Docker) crée chaque nœud du cluster comme un conteneur Docker, ce qui permet un déploiement léger et rapide pour le développement et les tests.

---

### Exercice 2 : Lecture et interprétation d'un manifeste

#### 2.1 Rôle de `selector.matchLabels` et lien avec `template.metadata.labels`

`selector.matchLabels` indique au Deployment quels pods il doit gérer. Le Deployment recherche et surveille les pods qui possèdent les labels spécifiés (`app: anfa-api`).  
Le `template.metadata.labels` définit les labels qui seront appliqués aux pods créés par ce Deployment. **Le lien est crucial** : les labels du template doivent correspondre exactement au selector pour que le Deployment puisse gérer les pods qu'il crée. Si les labels ne correspondent pas, le Deployment ne pourra pas contrôler ses propres pods.

#### 2.2 Nombre de pods et comportement en cas de mort

Le Deployment créera **2 replicas** (comme spécifié par `replicas: 2`).  
Si l'un des pods meurt (par exemple, à cause d'une panne de nœud), le **ReplicaSet** géré par le Deployment détecte l'écart par rapport à l'état souhaité et recrée automatiquement un nouveau pod pour rétablir le nombre de replicas à 2. C'est le mécanisme de **self-healing** de Kubernetes.

#### 2.3 Résolution de `minio` dans l'endpoint

Le manifeste utilise `http://minio:9000` car `minio` fait référence au **nom du Service** Kubernetes créé pour MinIO. Kubernetes dispose d'un **DNS interne** au cluster (CoreDNS) qui résout automatiquement les noms de services en adresses IP. Ainsi, `minio` est résolu en l'adresse IP du Service MinIO, permettant à l'API de communiquer avec MinIO sans connaître son adresse IP exacte.

#### 2.4 Conséquence pratique de l'absence de Service

Sans Service, l'API Python n'est **pas accessible** depuis l'extérieur du cluster, ni depuis d'autres pods à l'intérieur du cluster de manière stable. Les pods de l'API ne peuvent pas être découverts dynamiquement, et un pod ne peut pas communiquer avec un autre via un nom stable. Il faudrait utiliser l'adresse IP directe du pod, qui change à chaque redémarrage.

#### 2.5 Manifeste de Service (ClusterIP)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: anfa-api-service
  namespace: anfa
spec:
  type: ClusterIP
  selector:
    app: anfa-api
  ports:
    - port: 80
      targetPort: 8000
      protocol: TCP
```

---

### Exercice 3 : Diagnostic

#### 3.1 Le pod qui ne démarre pas

**a. Signification de `ImagePullBackOff`** :  
Ce statut indique que Kubernetes n'arrive pas à télécharger l'image du conteneur depuis le registre. Il a essayé plusieurs fois et est en "backoff" (période d'attente entre les tentatives).

**b. Cause probable** :  
L'image `minio/miniooo:latest` n'existe pas. Il y a une **faute de frappe** : le nom correct est `minio/minio:latest` (avec un seul "o").

**c. Commande pour plus de détails** :  
```bash
kubectl describe pod minio-7d9f8b6c5-x2k9p -n <namespace>
```
Cette commande affiche les événements du pod, y compris le message d'erreur exact du pull d'image.

---

#### 3.2 Le PVC qui ne se lie pas

**a. Signification du statut `Pending`** :  
Le PVC est en attente car Kubernetes n'a pas trouvé de PersistentVolume (PV) correspondant aux critères du PVC (capacité, mode d'accès, storage class).

**b. Cause probable dans un cluster Kind local** :  
Kind ne provisionne pas automatiquement de PV. Il faut soit :
- Créer manuellement un PV correspondant
- Utiliser un StorageClass local (comme `standard` dans Kind, mais il faut configurer un provisionneur)

**c. Commande pour confirmer le diagnostic** :  
```bash
kubectl describe pvc data-pvc -n <namespace>
```
Cette commande montre les événements et la raison précise pour laquelle le PVC ne se lie pas (ex: `no persistent volumes available for this claim`).

---

#### 3.3 Le port-forward qui échoue

**a. Cause de l'erreur** :  
Le pod est en état `Pending`, donc il n'a pas encore démarré. Le port-forward ne peut pas fonctionner car il n'y a pas de conteneur en cours d'exécution sur lequel se connecter.

**b. Commande pour comprendre pourquoi le pod est en `Pending`** :  
```bash
kubectl describe pod <nom-du-pod> -n <namespace>
```
Les événements affichés révéleront si le problème vient du PVC (en attente de volume) ou d'autres ressources manquantes.

**c. Ordre logique avant un port-forward** :  
1. Vérifier que le pod est en état `Running` : `kubectl get pods`
2. Si ce n'est pas le cas, diagnostiquer avec `kubectl describe pod`
3. Résoudre les problèmes (PVC, image, ressources, etc.)
4. Une fois le pod en `Running`, effectuer le port-forward

---

### Exercice 4 : De Docker Compose à Kubernetes

#### 4.1 Nombre de manifestes Kubernetes nécessaires

Pour reproduire la même fonctionnalité que le docker-compose, il faut **4 manifestes** :

| Manifeste | Rôle |
|-----------|------|
| **PVC** | Déclare la demande de stockage persistant pour les données MinIO |
| **Deployment** | Définit l'application MinIO (image, ports, commande, env, volume) |
| **Service** | Expose le port 9000 (API) et 9001 (console) à l'intérieur du cluster |
| **Secret ou ConfigMap** | Stocke les identifiants MINIO_ROOT_USER et MINIO_ROOT_PASSWORD (optionnel mais recommandé) |

---

#### 4.2 Différence conceptuelle entre volume Docker nommé et PVC Kubernetes

Un **volume Docker nommé** est un volume géré par Docker, simplement attaché à un conteneur. La persistance est locale au nœud et limitée à cet hôte.  
Un **PersistentVolumeClaim (PVC)** Kubernetes est une abstraction qui sépare la demande de stockage (PVC) de la ressource physique (PV). Le PVC permet de demander dynamiquement du stockage via des StorageClasses, et le PV peut être provisionné par différents fournisseurs (cloud, NFS, local, etc.), ce qui rend le stockage portable et évolutif.

---

#### 4.3 Différence d'accès entre Compose et Kubernetes

Avec Docker Compose, MinIO expose ses ports directement sur l'hôte via le mapping `"9001:9001"`. Avec Kind, les nœuds sont des conteneurs Docker sans accès direct aux ports de l'hôte. Le Service Kubernetes expose MinIO à l'intérieur du cluster, mais pour accéder depuis l'extérieur, il faut soit :
- Un **NodePort** (ouvre un port sur chaque nœud du cluster)
- Un **LoadBalancer** (nécessite un cloud provider)
- Un **port-forward** (pour le développement seulement)

Pour accéder directement à MinIO comme avec Compose, il faudrait utiliser un Service de type **NodePort** (par exemple, port 30900 sur l'hôte) ou configurer un **Ingress Controller** avec un host réseau approprié.

---

#### 4.4 Avantages de Kubernetes par rapport à Docker Compose (observés en TP)

1. **Self-healing** : Lorsqu'un pod MinIO a été supprimé manuellement, Kubernetes l'a recréé automatiquement pour maintenir le nombre de replicas souhaité (mécanisme observé en TP).
2. **Scaling** : La commande `kubectl scale deployment minio --replicas=3` a permis d'augmenter facilement le nombre de pods MinIO à 3, puis de revenir à 1 (observé en TP).

---

### Exercice 5 : Mini-cas d'architecture

#### 5.1 Types d'objets Kubernetes pour chaque composant

| Composant | Type d'objet | Justification |
|-----------|--------------|---------------|
| `pipeline-anfa` (batch nocturne) | **CronJob** | S'exécute selon un planning défini (toutes les nuits à 2h) et se termine après avoir traité les données. |
| `anfa-api` (API REST) | **Deployment** | Doit être toujours disponible avec plusieurs replicas (50 req/s aux heures de pointe), scalable et sans état persistant. |
| `anfa-dashboard` (Grafana) | **Deployment** | Service web standard, consulté en journée uniquement, avec possibilité de scaling si nécessaire. |

---

#### 5.2 Paramètres pour l'Horizontal Pod Autoscaler (HPA)

```yaml
minReplicas: 2
maxReplicas: 5
targetCPUUtilizationPercentage: 70
```

**Justification** : 
- `minReplicas: 2` : pour assurer une haute disponibilité (éviter un point de défaillance unique).
- `maxReplicas: 5` : suffisant pour gérer les pics à 50 req/s (marge de 2.5x).
- `targetCPUUtilizationPercentage: 70` : seuil classique qui déclenche le scaling lorsque l'utilisation CPU atteint 70%, laissant une marge avant saturation.

---

#### 5.3 Type de Service pour `anfa-api`

**LoadBalancer**  
*Justification* : L'API est consommée par des applications mobiles depuis l'extérieur du cluster. LoadBalancer fournit une adresse IP publique stable et scalable, contrairement à NodePort qui expose un port dynamique, et ClusterIP qui ne fonctionne qu'en interne.

---

#### 5.4 Gestion des mises à jour sans coupure

Kubernetes gère les mises à jour via **RollingUpdate** (stratégie par défaut des Deployments). Lors d'une mise à jour :
1. Un nouveau ReplicaSet est créé avec la nouvelle version.
2. De nouveaux pods sont progressivement déployés (un par un ou par vagues, selon `maxSurge` et `maxUnavailable`).
3. Les anciens pods sont terminés progressivement.
4. Les requêtes sont réparties entre les anciens et nouveaux pods pendant la transition.
5. Les pods sont considérés comme prêts grâce aux **readiness probes**, assurant qu'ils reçoivent du trafic seulement lorsqu'ils sont opérationnels.

Ce mécanisme garantit qu'il y a toujours au moins un pod disponible pour répondre aux requêtes, évitant ainsi toute coupure de service.

---

#### 5.5 Squelette de manifeste YAML pour `anfa-api`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: anfa-api
  namespace: anfa
  labels:
    app: anfa-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: anfa-api
  template:
    metadata:
      labels:
        app: anfa-api
    spec:
      containers:
        - name: api
          image: anfa-api:latest
          imagePullPolicy: Always
          ports:
            - containerPort: 8000
              name: http
              protocol: TCP
          env:
            - name: MINIO_ENDPOINT
              value: "http://minio:9000"
            - name: LOG_LEVEL
              value: "INFO"
          resources:
            requests:
              memory: "64Mi"
              cpu: "100m"
            limits:
              memory: "128Mi"
              cpu: "200m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
```

---

## Difficultés rencontrées

### 1. Installation et configuration de Kind
- **Problème :** Kind ne s'installait pas correctement via winget dans CMD.
- **Cause :** Le chemin de Kind n'était pas dans le PATH, et l'exécutable n'était pas accessible.
- **Solution :** Utilisation de PowerShell Admin pour installer `kind` via winget, puis ajout manuel du chemin au PATH système.

### 2. Création du cluster avec Kind
- **Problème :** Kind ne trouvait pas Docker Desktop.
- **Cause :** Docker Desktop n'était pas installé ou mal configuré.
- **Solution :** Installation de Docker Desktop via winget, puis redémarrage de la machine.

### 3. Déploiement du PVC MinIO
- **Problème :** Le PVC restait en statut `Pending` indéfiniment.
- **Cause :** Kind ne provisionne pas automatiquement les PV. La StorageClass `standard` n'était pas configurée.
- **Solution :** Création manuelle d'un PersistentVolume pour le PVC.

### 4. Port-forwarding vers MinIO
- **Problème :** `kubectl port-forward` échouait avec l'erreur "pod is not running".
- **Cause :** Le pod MinIO n'avait pas démarré car le PVC restait en `Pending`.
- **Solution :** Résolution du problème du PVC (création d'un PV manuel), puis le pod a démarré et le port-forward a fonctionné.

### 5. Compréhension des concepts Kubernetes
- **Problème :** Difficulté à saisir la différence entre Deployment, Service, PVC et leurs interactions.
- **Cause :** Architecture Kubernetes complexe avec de nombreux concepts interconnectés.
- **Solution :** Lecture de la documentation, schématisation des relations entre les ressources, et pratique en TP.

---

## Conclusion

Cette séance m'a permis de maîtriser les concepts fondamentaux de Kubernetes à travers une mise en pratique concrète avec Kind. J'ai appris à déployer une application (MinIO) dans un cluster Kubernetes en utilisant des manifestes YAML, à gérer le stockage persistant avec PVC, et à observer les mécanismes de self-healing et de scaling. J'ai également compris les différences entre Docker Compose et Kubernetes en termes d'architecture, de persistance des données et d'exposition des services. Ces compétences sont essentielles pour industrialiser des pipelines Big Data et pour déployer des applications en production dans un environnement cloud native.
```