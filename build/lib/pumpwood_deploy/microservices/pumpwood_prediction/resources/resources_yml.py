app_deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pumpwood-prediction-app
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      type: app
      endpoint: pumpwood-prediction-app
  template:
    metadata:
      labels:
        type: app
        endpoint: pumpwood-prediction-app
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: bucket-key
        secret:
          secretName: bucket-key
      containers:
      - name: pumpwood-prediction
        image: {repository}/pumpwood-prediction-app:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: bucket-key
            readOnly: true
            mountPath: /etc/secrets
        ports:
        - containerPort: 5000
        readinessProbe:
          httpGet:
            path: /health-check/pumpwood-prediction-app/
            port: 5000
        env:
        - name: DEBUG
          value: "{debug}"

        - name: HASH_SALT
          valueFrom:
            secretKeyRef:
              name: hash-salt
              key: hash_salt

        #Database
        - name: DB_HOST
          value: "postgres-pumpwood-prediction"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: pumpwood-prediction
              key: db_password

        # Microsservice
        - name: MICROSERVICE_PASSWORD
          valueFrom:
              secretKeyRef:
                name: pumpwood-prediction
                key: microservice_password

        # RABBITMQ QUEUE
        - name: RABBITMQ_HOST
          value: "rabbitmq-main"
        - name: RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rabbitmq-main-secrets
              key: password
        # Google
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: "/etc/secrets/key-storage.json"
        - name: STORAGE_BUCKET_NAME
          value: {bucket_name}
        - name: STORAGE_TYPE
          value: 'google_bucket'
---
apiVersion : "v1"
kind: Service
metadata:
  name: pumpwood-prediction-app
  labels:
    type: app
    endpoint: pumpwood-prediction-app
spec:
  type: ClusterIP
  ports:
    - port: 5000
      targetPort: 5000
  selector:
    type: app
    endpoint: pumpwood-prediction-app
"""

worker_dataloader = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pumpwood-prediction-dataloader-workers
spec:
  replicas: 1
  selector:
    matchLabels:
      type: worker
      endpoint: pumpwood-prediction-app
      function: dataloader
  template:
    metadata:
      labels:
        type: worker
        endpoint: pumpwood-prediction-app
        function: dataloader
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: bucket-key
        secret:
          secretName: bucket-key

      containers:
      - name: pumpwood-prediction-dataloader-workers
        image: {repository}/pumpwood-prediction-dataloader-worker:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: bucket-key
            readOnly: true
            mountPath: /etc/secrets

        env:
        #DATABASE
        - name: DB_HOST
          value: "postgres-pumpwood-prediction"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: pumpwood-prediction
              key: db_password

        #Google
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: "/etc/secrets/key-storage.json"
        - name: STORAGE_BUCKET_NAME
          value: {bucket_name}
        - name: STORAGE_TYPE
          value: 'google_bucket'

        # RABBITMQ QUEUE
        - name: RABBITMQ_HOST
          value: "rabbitmq-main"
        - name: RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rabbitmq-main-secrets
              key: password

        # Microsservice
        - name: MICROSERVICE_PASSWORD
          valueFrom:
              secretKeyRef:
                name: pumpwood-prediction
                key: microservice_password

        # CHUNKS
        - name: N_CHUNKS
          value: "4"
        - name: CHUNK_SIZE
          value: "2000"
"""

worker_rawdata = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pumpwood-prediction-rawdata-workers
spec:
  replicas: 1
  selector:
    matchLabels:
      type: worker
      endpoint: pumpwood-prediction-app
      function: rawdata
  template:
    metadata:
      labels:
        type: worker
        endpoint: pumpwood-prediction-app
        function: rawdata
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: bucket-key
        secret:
          secretName: bucket-key
      containers:
      - name: pumpwood-prediction-rawdata-workers
        image: {repository}/pumpwood-prediction-rawdata-worker:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: bucket-key
            readOnly: true
            mountPath: /etc/secrets
        env:
        # DATALAKE DATALAKE
        - name: DATALAKE_DB_HOST
          value: "postgres-pumpwood-datalake"
        - name: DATALAKE_DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: pumpwood-datalake
              key: db_password

        # DATALAKE PREDICTION
        - name: PREDICTION_DB_HOST
          value: "postgres-pumpwood-prediction"
        - name: PREDICTION_DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: pumpwood-prediction
              key: db_password

        #Google
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: "/etc/secrets/key-storage.json"
        - name: STORAGE_BUCKET_NAME
          value: {bucket_name}
        - name: STORAGE_TYPE
          value: 'google_bucket'

        # RABBITMQ QUEUE
        - name: RABBITMQ_HOST
          value: "rabbitmq-main"
        - name: RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rabbitmq-main-secrets
              key: password

        #Microsservice
        - name: MICROSERVICE_PASSWORD
          valueFrom:
              secretKeyRef:
                name: pumpwood-prediction
                key: microservice_password
"""

secrets = """
apiVersion: v1
kind: Secret
metadata:
  name: pumpwood-prediction
type: Opaque
data:
  db_password: {db_password}
  microservice_password: {microservice_password}
  ssl_key: {ssl_key}
  ssl_crt: {ssl_crt}
"""

services__load_balancer = """
apiVersion : "v1"
kind: Service
metadata:
  name: loadbalancer-postgres-pumpwood-prediction
  labels:
    type: loadbalancer-db
    endpoint: pumpwood-prediction-app
    function: prediction
spec:
  type: LoadBalancer
  ports:
    - port: 7000
      targetPort: 5432
  selector:
      type: db
      endpoint: pumpwood-prediction-app
      function: prediction
  loadBalancerIP: {{ postgres_public_ip }}
  loadBalancerSourceRanges:
    {%- for ip in firewall_ips %}
      - {{ip}}
    {%- endfor %}
"""

volume_postgres = """
kind: PersistentVolume
apiVersion: v1
metadata:
  name: {disk_name}
  labels:
    type: db
    endpoint: pumpwood-prediction-app
    function: prediction
    disk: {disk_name}
spec:
  accessModes:
    - ReadWriteOnce
  capacity:
    storage: {disk_size}
  storageClassName: standard
  gcePersistentDisk:
    fsType: ext4
    pdName: {disk_name}
---
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: postgres-pumpwood-prediction
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: {disk_size}
  volumeName: {disk_name}
"""

deployment_postgres = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-pumpwood-prediction
spec:
  replicas: 1
  selector:
    matchLabels:
      type: db
      endpoint: pumpwood-prediction-app
      function: prediction
  template:
    metadata:
      labels:
        type: db
        endpoint: pumpwood-prediction-app
        function: prediction
    spec:
      volumes:
      - name: postgres-pumpwood-prediction
        persistentVolumeClaim:
          claimName: postgres-pumpwood-prediction
      - name: postgres-init-configmap
        configMap:
          name: postgres-init-configmap
      - name: secrets
        secret:
          secretName: pumpwood-prediction
      - name: dshm
        emptyDir:
          medium: Memory

      containers:
      - name: postgres-pumpwood-prediction
        image: timescale/timescaledb-postgis:1.7.3-pg12
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "10m"
          limits:
            cpu: "2"
        ports:
        - containerPort: 5432

        env:
        - name: POSTGRES_USER
          value: pumpwood
        - name: POSTGRES_DB
          value: pumpwood
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: pumpwood-prediction
              key: db_password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata

        volumeMounts:
        - name: postgres-pumpwood-prediction
          mountPath: /var/lib/postgresql/data/
        - name: postgres-init-configmap
          mountPath: /docker-entrypoint-initdb.d/
        - name: secrets
          mountPath: /etc/secrets
          readOnly: true
        - name: dshm
          mountPath: /dev/shm
---
apiVersion : "v1"
kind: Service
metadata:
  name: postgres-pumpwood-prediction
  labels:
    type: db
    endpoint: pumpwood-prediction-app
    function: prediction
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    type: db
    endpoint: pumpwood-prediction-app
    function: prediction
"""

test_postgres = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-pumpwood-prediction
spec:
  replicas: 1
  selector:
    matchLabels:
      type: db
      endpoint: pumpwood-prediction-app
      function: prediction
  template:
    metadata:
      labels:
        type: db
        endpoint: pumpwood-prediction-app
        function: prediction
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: dshm
        emptyDir:
          medium: Memory

      containers:
      - name: postgres-pumpwood-prediction
        image: {repository}/test-db-pumpwood-prediction:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "10m"
          limits:
            cpu: "2"
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: dshm
          mountPath: /dev/shm
---
apiVersion : "v1"
kind: Service
metadata:
  name: postgres-pumpwood-prediction
  labels:
    type: db
    endpoint: pumpwood-prediction-app
    function: prediction
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    type: db
    endpoint: pumpwood-prediction-app
    function: prediction
"""
