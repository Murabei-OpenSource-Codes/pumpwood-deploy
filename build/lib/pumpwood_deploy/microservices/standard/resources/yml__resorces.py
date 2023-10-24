hash_salt = """
apiVersion: v1
kind: Secret
metadata:
  name: hash-salt
type: Opaque
data:
  hash_salt: {hash_salt}
"""

rabbitmq_deployment = """
apiVersion : "v1"
kind: Service
metadata:
  name: rabbitmq-main
  labels:
    type: queue
    queue: rabbitmq-main
spec:
  type: ClusterIP
  ports:
    - name: ui
      port: 15672
      targetPort: 15672
    - name: broker
      port: 5672
      targetPort: 5672
  selector:
    type: queue
    queue: rabbitmq-main
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rabbitmq-main
spec:
  replicas: 1
  selector:
    matchLabels:
      type: queue
      queue: rabbitmq-main
  template:
    metadata:
      labels:
        type: queue
        queue: rabbitmq-main
    spec:
      restartPolicy: Always
      volumes:
      - name: secrets
        secret:
          secretName: rabbitmq-main-secrets
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: function
                operator: NotIn
                values:
                - system
      containers:
      - name: rabbitmq-main
        image: rabbitmq:3.8-management
        resources:
          requests:
            cpu: "1m"
        env:
        - name: RABBITMQ_DEFAULT_USER
          value: 'pumpwood'
        - name: RABBITMQ_DEFAULT_PASS
          valueFrom:
            secretKeyRef:
              name: rabbitmq-main-secrets
              key: password
        ports:
        - name: 'queue'
          containerPort: 5672
        - name: 'ui'
          containerPort: 15672
"""

rabbitmq_secrets = """
apiVersion: v1
kind: Secret
metadata:
  name: rabbitmq-main-secrets
type: Opaque
data:
  password: {password}
"""

storage_config_map = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: storage
data:
  storage_type: "{storage_type}"
"""

azure__storage_key_secrets = """
apiVersion: v1
kind: Secret
metadata:
  name: azure--storage-key
type: Opaque
data:
  azure_storage_connection_string: {azure_storage_connection_string}
"""

gcp__storage_key_secrets = """
apiVersion: v1
kind: Secret
metadata:
  name: gcp--storage-key
type: Opaque
data:
  empty: bm90X2NvbmZpZ3VyZWQ=
"""

aws__storage_key_secrets = """
apiVersion: v1
kind: Secret
metadata:
  name: aws--storage-key
type: Opaque
data:
  aws_access_key_id: {aws_access_key_id}
  aws_secret_access_key: {aws_secret_access_key}
"""

model_secrets = """
apiVersion: v1
kind: Secret
metadata:
  name: microservice-model-secrets
type: Opaque
data:
  password: {password}
"""

kong_postgres_deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-kong-database
spec:
  replicas: 1
  selector:
    matchLabels:
      type: db
      db: postgres-kong-database
  template:
    metadata:
      labels:
        type: db
        db: postgres-kong-database
    spec:
      volumes:
      - name: postgres-kong-database-data
        persistentVolumeClaim:
          claimName: postgres-kong-database
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: function
                operator: NotIn
                values:
                - system
      containers:
      - name: postgres-kong-database
        image: postgres:11
        resources:
          requests:
            cpu: "1m"
        env:
        - name: POSTGRES_USER
          value: kong
        - name: POSTGRES_PASSWORD
          value: kong
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        volumeMounts:
        - name: postgres-kong-database-data
          mountPath: /var/lib/postgresql/data/
        ports:
        - containerPort: 5432
---
apiVersion : "v1"
kind: Service
metadata:
  name: postgres-kong-database
  labels:
    type: db
    db: postgres-kong-database
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    type: db
    db: postgres-kong-database
"""


kong_deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: apigateway-kong
spec:
  replicas: 2
  selector:
    matchLabels:
      type: apigateway-kong
  template:
    metadata:
      labels:
        type: apigateway-kong
    spec:
      imagePullSecrets:
        - name: dockercfg
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: function
                operator: NotIn
                values:
                - system
      containers:
      - name: apigateway-kong
        image: andrebaceti/autoboostrap-kong:1.0
        resources:
          requests:
            cpu: "1m"
        readinessProbe:
           exec:
             command:
               - kong
               - health
        ports:
        # Consumers Ports
        - containerPort: 8000
        - containerPort: 8443
        # Admin Ports
        - containerPort: 8001
        - containerPort: 8444
---
apiVersion : "v1"
kind: Service
metadata:
  name: load-balancer
  labels:
    type: load-balancer
    destination: internal
spec:
  type: ClusterIP
  selector:
    type: apigateway-kong
  ports:
  # Consumers Ports
  - name: consumers-http
    port: 8000
    targetPort: 8000
  - name: consumers-https
    port: 8443
    targetPort: 8443
  # Admin Ports
  - name: admin-http
    port: 8001
    targetPort: 8001
  - name: admin-https
    port: 8444
    targetPort: 8444
"""
