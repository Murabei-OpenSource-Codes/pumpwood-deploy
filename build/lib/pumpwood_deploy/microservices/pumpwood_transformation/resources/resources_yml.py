secrets = """
apiVersion: v1
kind: Secret
metadata:
  name: pumpwood-transformation
type: Opaque
data:
  db_password: {db_password}
  microservice_password: {microservice_password}
  ssl_key: {ssl_key}
  ssl_crt: {ssl_crt}
"""

transformation_deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pumpwood-transformation-app
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      type: app
      endpoint: pumpwood-transformation-app
      function: prediction
  template:
    metadata:
      labels:
        type: app
        endpoint: pumpwood-transformation-app
        function: prediction
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: gcp--storage-key
        secret:
          secretName: gcp--storage-key
      containers:
      - name: pumpwood-transformation
        image: {repository}/pumpwood-transformation-app:{version}
        imagePullPolicy: Always
        resources:
          requests:
            memory: "{requests_memory}"
            cpu:  "{requests_cpu}"
          limits:
            memory: "{limits_memory}"
            cpu:  "{limits_cpu}"
        volumeMounts:
          - name: gcp--storage-key
            readOnly: true
            mountPath: /etc/secrets
        ports:
        - containerPort: 5000
        readinessProbe:
          httpGet:
            path: /health-check/pumpwood-transformation-app/
            port: 5000

        env:
        - name: DEBUG
          value: "{debug}"

        - name: HASH_SALT
          valueFrom:
            secretKeyRef:
              name: hash-salt
              key: hash_salt

        # Database
        - name: DB_USERNAME
          value: {db_username}
        - name: DB_HOST
          value: {db_host}
        - name: DB_PORT
          value: "{db_port}"
        - name: DB_DATABASE
          value: {db_database}
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: pumpwood-transformation
              key: db_password

        # Microsservice
        - name: MICROSERVICE_PASSWORD
          valueFrom:
              secretKeyRef:
                name: pumpwood-transformation
                key: microservice_password

        # RABBITMQ QUEUE
        - name: RABBITMQ_HOST
          value: "rabbitmq-main"
        - name: RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rabbitmq-main-secrets
              key: password

        ###########
        # STORAGE #
        - name: STORAGE_BUCKET_NAME
          value: {bucket_name}
        - name: STORAGE_TYPE
          valueFrom:
            configMapKeyRef:
              name: storage
              key: storage_type

        # GCP
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: "/etc/secrets/key-storage.json"

        # AZURE
        - name: AZURE_STORAGE_CONNECTION_STRING
          valueFrom:
              secretKeyRef:
                name: azure--storage-key
                key: azure_storage_connection_string

        # AWS
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
              secretKeyRef:
                name: aws--storage-key
                key: aws_access_key_id
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
              secretKeyRef:
                name: aws--storage-key
                key: aws_secret_access_key

        # Timeout
        - name: WORKERS_TIMEOUT
          value: "{workers_timeout}"
---
apiVersion : "v1"
kind: Service
metadata:
  name: pumpwood-transformation-app
  labels:
    type: app
    endpoint: pumpwood-transformation-app
    function: prediction
spec:
  type: ClusterIP
  ports:
    - port: 5000
      targetPort: 5000
  selector:
    type: app
    endpoint: pumpwood-transformation-app
    function: prediction
"""

transformation_worker_estimation = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pumpwood-transformation-estimation-worker
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      type: worker
      endpoint: pumpwood-transformation-app
      function: transformation-estimation
  template:
    metadata:
      labels:
        type: worker
        endpoint: pumpwood-transformation-app
        function: transformation-estimation
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: gcp--storage-key
        secret:
          secretName: gcp--storage-key
      containers:
      - name: pumpwood-transformation
        image: {repository}/pumpwood-transformation-app:{version}
        imagePullPolicy: Always
        resources:
          requests:
            memory: "{requests_memory}"
            cpu:  "{requests_cpu}"
          limits:
            memory: "{limits_memory}"
            cpu:  "{limits_cpu}"
        volumeMounts:
          - name: gcp--storage-key
            readOnly: true
            mountPath: /etc/secrets
        command: ["bash", "/app/start_estimation_worker.sh"]
        env:
        - name: APP_DEBUG
          value: "False"

        # Database
        - name: DB_USERNAME
          value: {db_username}
        - name: DB_HOST
          value: {db_host}
        - name: DB_PORT
          value: "{db_port}"
        - name: DB_DATABASE
          value: {db_database}
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: pumpwood-transformation
              key: db_password

        # Microsservice
        - name: MICROSERVICE_PASSWORD
          valueFrom:
              secretKeyRef:
                name: pumpwood-transformation
                key: microservice_password

        # RABBITMQ QUEUE
        - name: RABBITMQ_HOST
          value: "rabbitmq-main"
        - name: RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rabbitmq-main-secrets
              key: password

        ###########
        # STORAGE #
        - name: STORAGE_BUCKET_NAME
          value: {bucket_name}
        - name: STORAGE_TYPE
          valueFrom:
            configMapKeyRef:
              name: storage
              key: storage_type

        # GCP
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: "/etc/secrets/key-storage.json"

        # AZURE
        - name: AZURE_STORAGE_CONNECTION_STRING
          valueFrom:
              secretKeyRef:
                name: azure--storage-key
                key: azure_storage_connection_string

        # AWS
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
              secretKeyRef:
                name: aws--storage-key
                key: aws_access_key_id
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
              secretKeyRef:
                name: aws--storage-key
                key: aws_secret_access_key
"""

transformation_worker_prediction = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pumpwood-transformation-prediction-worker
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      type: worker
      endpoint: pumpwood-transformation-app
      function: transformation-prediction
  template:
    metadata:
      labels:
        type: worker
        endpoint: pumpwood-transformation-app
        function: transformation-prediction
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: gcp--storage-key
        secret:
          secretName: gcp--storage-key
      containers:
      - name: pumpwood-transformation
        image: {repository}/pumpwood-transformation-app:{version}
        imagePullPolicy: Always
        resources:
          requests:
            memory: "{requests_memory}"
            cpu:  "{requests_cpu}"
          limits:
            memory: "{limits_memory}"
            cpu:  "{limits_cpu}"
        volumeMounts:
          - name: gcp--storage-key
            readOnly: true
            mountPath: /etc/secrets
        command: ["bash", "/app/start_prediction_worker.sh"]
        env:
        - name: APP_DEBUG
          value: "False"

        # Database
        - name: DB_USERNAME
          value: {db_username}
        - name: DB_HOST
          value: {db_host}
        - name: DB_PORT
          value: "{db_port}"
        - name: DB_DATABASE
          value: {db_database}
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: pumpwood-transformation
              key: db_password

        # Microsservice
        - name: MICROSERVICE_PASSWORD
          valueFrom:
              secretKeyRef:
                name: pumpwood-transformation
                key: microservice_password

        # RABBITMQ QUEUE
        - name: RABBITMQ_HOST
          value: "rabbitmq-main"
        - name: RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rabbitmq-main-secrets
              key: password

        ###########
        # STORAGE #
        - name: STORAGE_BUCKET_NAME
          value: {bucket_name}
        - name: STORAGE_TYPE
          valueFrom:
            configMapKeyRef:
              name: storage
              key: storage_type

        # GCP
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: "/etc/secrets/key-storage.json"

        # AZURE
        - name: AZURE_STORAGE_CONNECTION_STRING
          valueFrom:
              secretKeyRef:
                name: azure--storage-key
                key: azure_storage_connection_string

        # AWS
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
              secretKeyRef:
                name: aws--storage-key
                key: aws_access_key_id
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
              secretKeyRef:
                name: aws--storage-key
                key: aws_secret_access_key
"""

volume_postgres = """
kind: PersistentVolume
apiVersion: v1
metadata:
  name: {disk_name}
  labels:
    usage: {disk_name}
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
  name: postgres-pumpwood-transformation
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
  name: postgres-pumpwood-transformation
spec:
  replicas: 1
  selector:
    matchLabels:
      type: db
      endpoint: pumpwood-transformation-app
      function: prediction
  template:
    metadata:
      labels:
        type: db
        endpoint: pumpwood-transformation-app
        function: prediction
    spec:
      volumes:
      - name: pumpwood-transformation-data
        persistentVolumeClaim:
          claimName: postgres-pumpwood-transformation
      - name: secrets
        secret:
          secretName: pumpwood-transformation
      - name: dshm
        emptyDir:
          medium: Memory

      containers:
      - name: postgres-pumpwood-transformation
        image: timescale/timescaledb-postgis:2.3.0-pg13
        args: [
            "-c", "max_connections=1000",
            "-c", "work_mem=50MB",
            "-c", "shared_buffers=1GB",
            "-c", "max_locks_per_transaction=500",
            "-c", "max_wal_size=10GB",
            "-c", "min_wal_size=80MB"]
        imagePullPolicy: Always
        resources:
          requests:
            memory: "{requests_memory}"
            cpu:  "{requests_cpu}"
          limits:
            memory: "{limits_memory}"
            cpu:  "{limits_cpu}"
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
              name: pumpwood-transformation
              key: db_password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata

        volumeMounts:
        - name: pumpwood-transformation-data
          mountPath: /var/lib/postgresql/data/
        - name: secrets
          mountPath: /etc/secrets
          readOnly: true
        - name: dshm
          mountPath: /dev/shm
---
apiVersion : "v1"
kind: Service
metadata:
  name: postgres-pumpwood-transformation
  labels:
    type: db
    endpoint: pumpwood-transformation-app
    function: prediction
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    type: db
    endpoint: pumpwood-transformation-app
    function: prediction
"""

services__load_balancer = """
apiVersion : "v1"
kind: Service
metadata:
  name: loadbalancer-postgres-pumpwood-transformation
  labels:
    type: loadbalancer-db
    db: postgres-pumpwood-transformation
spec:
  type: LoadBalancer
  ports:
    - port: 7000
      targetPort: 5432
  selector:
    type: db
    db: postgres-pumpwood-transformation
  loadBalancerIP: {{ postgres_public_ip }}
  loadBalancerSourceRanges:
    {%- for ip in firewall_ips %}
      - {{ip}}
    {%- endfor %}
"""

test_postgres = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-pumpwood-transformation
spec:
  replicas: 1
  selector:
    matchLabels:
      type: db
      endpoint: pumpwood-transformation-app
      function: prediction
  template:
    metadata:
      labels:
        type: db
        endpoint: pumpwood-transformation-app
        function: prediction
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: dshm
        emptyDir:
          medium: Memory

      containers:
      - name: postgres-pumpwood-transformation
        image: {repository}/test-db-pumpwood-transformation:{version}
        imagePullPolicy: Always
        resources:
          requests:
            memory: "{requests_memory}"
            cpu:  "{requests_cpu}"
          limits:
            memory: "{limits_memory}"
            cpu:  "{limits_cpu}"
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: dshm
          mountPath: /dev/shm
---
apiVersion : "v1"
kind: Service
metadata:
  name: postgres-pumpwood-transformation
  labels:
    type: db
    endpoint: pumpwood-transformation-app
    function: prediction
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    type: db
    endpoint: pumpwood-transformation-app
    function: prediction
"""
