app_deployment = """
apiVersion : "apps/v1"
kind: Deployment
metadata:
  name: pumpwood-datalake-app
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      type: app
      endpoint: pumpwood-datalake-app
      function: datalake
  template:
    metadata:
      labels:
        type: app
        endpoint: pumpwood-datalake-app
        function: datalake
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: gcp--storage-key
        secret:
          secretName: gcp--storage-key
      containers:
      - name: pumpwood-datalake
        image: {repository}/pumpwood-datalake-app:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: gcp--storage-key
            readOnly: true
            mountPath: /etc/secrets
        readinessProbe:
          httpGet:
            path: /health-check/pumpwood-datalake-app/
            port: 5000
        env:
        - name: DEBUG
          value: "{debug}"

        # HASH_SALT
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
              name: pumpwood-datalake
              key: db_password

        # RABBITMQ ETL
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
                name: pumpwood-datalake
                key: microservice_password

        # workers_timeout
        - name: WORKERS_TIMEOUT
          value: "{workers_timeout}"

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
        ports:
        - containerPort: 5000
---
apiVersion : "v1"
kind: Service
metadata:
  name: pumpwood-datalake-app
  labels:
    type: app
    endpoint: pumpwood-datalake-app
    function: datalake
spec:
  type: ClusterIP
  ports:
    - port: 5000
      targetPort: 5000
  selector:
    type: app
    endpoint: pumpwood-datalake-app
    function: datalake
"""


worker_deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pumpwood-datalake-dataloader-worker
spec:
  replicas: 1
  selector:
    matchLabels:
      type: worker
      endpoint: pumpwood-datalake-app
      function: dataloader
  template:
    metadata:
      labels:
          type: worker
          endpoint: pumpwood-datalake-app
          function: dataloader
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: gcp--storage-key
        secret:
          secretName: gcp--storage-key
      containers:
      - name: pumpwood-dataloader-worker
        image: {repository}/pumpwood-datalake-dataloader-worker:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: gcp--storage-key
            readOnly: true
            mountPath: /etc/secrets
        env:
        # HASH_SALT
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
              name: pumpwood-datalake
              key: db_password

        #RABBITMQ
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
                name: pumpwood-datalake
                key: microservice_password

        # Limit process
        - name: N_CHUNKS
          value: '{n_chunks}'
        - name: CHUNK_SIZE
          value: '{chunk_size}'

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

secrets = """
apiVersion: v1
kind: Secret
metadata:
  name: pumpwood-datalake
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
  name: loadbalancer-postgres-pumpwood-datalake
  labels:
      type: loadbalancer-db
      endpoint: pumpwood-datalake-app
      function: datalake
spec:
  type: LoadBalancer
  ports:
    - port: 7000
      targetPort: 5432
  selector:
      type: db
      endpoint: pumpwood-datalake-app
      function: datalake
  loadBalancerIP: {{ postgres_public_ip }}
  loadBalancerSourceRanges:
    {%- for ip in firewall_ips %}
      - {{ip}}
    {%- endfor %}
"""

deployment_postgres = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-pumpwood-datalake
spec:
  replicas: 1
  selector:
    matchLabels:
      type: db
      endpoint: pumpwood-datalake-app
      function: datalake
  template:
    metadata:
      labels:
        type: db
        endpoint: pumpwood-datalake-app
        function: datalake
    spec:
      volumes:
      - name: pumpwood-datalake-data
        persistentVolumeClaim:
          claimName: postgres-pumpwood-datalake
      - name: postgres-init-configmap
        configMap:
          name: postgres-init-configmap
      - name: secrets
        secret:
          secretName: pumpwood-datalake
      - name: dshm
        emptyDir:
          medium: Memory
      containers:
      - name: postgres-pumpwood-datalake
        image: timescale/timescaledb-postgis:1.7.3-pg12
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
          limits:
            cpu: "3"
        env:
        - name: POSTGRES_USER
          value: pumpwood
        - name: POSTGRES_DB
          value: pumpwood
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: pumpwood-datalake
              key: db_password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata

        volumeMounts:
        - name: pumpwood-datalake-data
          mountPath: /var/lib/postgresql/data/
        - name: postgres-init-configmap
          mountPath: /docker-entrypoint-initdb.d/
        - name: secrets
          mountPath: /etc/secrets
          readOnly: true
        - name: dshm
          mountPath: /dev/shm
        ports:
        - containerPort: 5432
---
apiVersion : "v1"
kind: Service
metadata:
  name: postgres-pumpwood-datalake
  labels:
    type: db
    endpoint: pumpwood-datalake-app
    function: datalake
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    type: db
    endpoint: pumpwood-datalake-app
    function: datalake
"""


test_postgres = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-pumpwood-datalake
spec:
  replicas: 1
  selector:
    matchLabels:
      type: db
      endpoint: pumpwood-datalake-app
      function: datalake
  template:
    metadata:
      labels:
        type: db
        endpoint: pumpwood-datalake-app
        function: datalake
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: dshm
        emptyDir:
          medium: Memory
      containers:
      - name: postgres-pumpwood-datalake
        image: {repository}/test-db-pumpwood-datalake:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
          limits:
            cpu: "3"
        volumeMounts:
        - name: dshm
          mountPath: /dev/shm
        ports:
        - containerPort: 5432
---
apiVersion : "v1"
kind: Service
metadata:
  name: postgres-pumpwood-datalake
  labels:
    type: db
    endpoint: pumpwood-datalake-app
    function: datalake
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    type: db
    endpoint: pumpwood-datalake-app
    function: datalake
"""
