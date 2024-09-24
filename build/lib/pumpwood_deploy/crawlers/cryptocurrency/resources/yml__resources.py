app_deployment = """
apiVersion : "apps/v1"
kind: Deployment
metadata:
  name: crawler-cryptocurrency-app
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      type: app
      endpoint: crawler-cryptocurrency-app
      function: crawler
      data: cryptocurrency
  template:
    metadata:
      labels:
          type: app
          endpoint: crawler-cryptocurrency-app
          function: crawler
          data: cryptocurrency
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: gcp--storage-key
        secret:
          secretName: gcp--storage-key
      containers:
      - name: crawler-cryptocurrency
        image: {repository}/crawler-cryptocurrency-app:{version}
        imagePullPolicy: IfNotPresent
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
        readinessProbe:
          httpGet:
            path: /health-check/crawler-cryptocurrency-app/
            port: 5000
        env:
        - name: DEBUG
          value: "{debug}"
        - name: WORKERS_TIMEOUT
          value: "{workers_timeout}"
        - name: N_WORKERS
          value: "{n_workers}"

        # HASH_SALT
        - name: HASH_SALT
          valueFrom:
            secretKeyRef:
              name: hash-salt
              key: hash_salt

        ############
        # DATABASE #
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
              name: crawler-cryptocurrency
              key: db_password

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

        ############
        # RABBITMQ #
        - name: RABBITMQ_HOST
          value: "rabbitmq-main"
        - name: RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rabbitmq-main-secrets
              key: password

        #################
        # Microsservice #
        - name: MICROSERVICE_PASSWORD
          valueFrom:
              secretKeyRef:
                name: crawler-cryptocurrency
                key: microservice_password
        ports:
        - containerPort: 5000
---
apiVersion : "v1"
kind: Service
metadata:
  name: crawler-cryptocurrency-app
  labels:
      type: app
      endpoint: crawler-cryptocurrency-app
      function: crawler
      data: cryptocurrency
spec:
  type: ClusterIP
  ports:
    - port: 5000
      targetPort: 5000
  selector:
      type: app
      endpoint: crawler-cryptocurrency-app
      function: crawler
      data: cryptocurrency
"""


worker_candle_deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crawler-cryptocurrency--worker-candle
spec:
  replicas: 1
  selector:
    matchLabels:
      type: worker
      endpoint: crawler-cryptocurrency-app
      function: worker-candle
  template:
    metadata:
      labels:
          type: worker
          endpoint: crawler-cryptocurrency-app
          function: worker-candle
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: gcp--storage-key
        secret:
          secretName: gcp--storage-key
      containers:
      - name: crawler-cryptocurrency-worker
        image: {repository}/crawler-cryptocurrency--worker-candle:{version}
        imagePullPolicy: IfNotPresent
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
        env:
        # HASH_SALT
        - name: HASH_SALT
          valueFrom:
            secretKeyRef:
              name: hash-salt
              key: hash_salt

        # RABBITMQ
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
                name: crawler-cryptocurrency
                key: microservice_password
"""


worker_balance_deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crawler-cryptocurrency--worker-balance
spec:
  replicas: 1
  selector:
    matchLabels:
      type: worker
      endpoint: crawler-cryptocurrency-app
      function: worker-balance
  template:
    metadata:
      labels:
          type: worker
          endpoint: crawler-cryptocurrency-app
          function: worker-balance
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: gcp--storage-key
        secret:
          secretName: gcp--storage-key
      containers:
      - name: crawler-cryptocurrency-worker
        image: {repository}/crawler-cryptocurrency--worker-balance:{version}
        imagePullPolicy: IfNotPresent
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
        env:
        # HASH_SALT
        - name: HASH_SALT
          valueFrom:
            secretKeyRef:
              name: hash-salt
              key: hash_salt

        # RABBITMQ
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
                name: crawler-cryptocurrency
                key: microservice_password

        #################
        # Bitfinex Keys #
        - name: BITFINEX_API_KEY
          valueFrom:
              secretKeyRef:
                name: crawler-cryptocurrency
                key: bitfinex_api_key
        - name: BITFINEX_API_SECRET
          valueFrom:
              secretKeyRef:
                name: crawler-cryptocurrency
                key: bitfinex_api_secret
"""

worker_order_deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crawler-cryptocurrency--worker-order
spec:
  replicas: 1
  selector:
    matchLabels:
      type: worker
      endpoint: crawler-cryptocurrency-app
      function: worker-order
  template:
    metadata:
      labels:
          type: worker
          endpoint: crawler-cryptocurrency-app
          function: worker-order
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: gcp--storage-key
        secret:
          secretName: gcp--storage-key
      containers:
      - name: crawler-cryptocurrency-worker
        image: {repository}/crawler-cryptocurrency--worker-order:{version}
        imagePullPolicy: IfNotPresent
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
        env:
        # HASH_SALT
        - name: HASH_SALT
          valueFrom:
            secretKeyRef:
              name: hash-salt
              key: hash_salt

        # RABBITMQ
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
                name: crawler-cryptocurrency
                key: microservice_password

        #################
        # Bitfinex Keys #
        - name: BITFINEX_API_KEY
          valueFrom:
              secretKeyRef:
                name: crawler-cryptocurrency
                key: bitfinex_api_key
        - name: BITFINEX_API_SECRET
          valueFrom:
              secretKeyRef:
                name: crawler-cryptocurrency
                key: bitfinex_api_secret
"""

secrets = """
apiVersion: v1
kind: Secret
metadata:
  name: crawler-cryptocurrency
type: Opaque
data:
  db_password: {db_password}
  microservice_password: {microservice_password}
  bitfinex_api_key: {bitfinex_api_key}
  bitfinex_api_secret: {bitfinex_api_secret}
  ssl_key: {ssl_key}
  ssl_crt: {ssl_crt}
"""

services__load_balancer = """
apiVersion : "v1"
kind: Service
metadata:
  name: loadbalancer-postgres-crawler-cryptocurrency
  labels:
      type: loadbalancer-db
      endpoint: crawler-cryptocurrency-app
      function: crawler
      data: cryptocurrency
spec:
  type: LoadBalancer
  ports:
    - port: 7000
      targetPort: 5432
  selector:
      type: db
      endpoint: crawler-cryptocurrency-app
      function: crawler
      data: cryptocurrency
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
  name: postgres-crawler-cryptocurrency
spec:
  replicas: 1
  selector:
    matchLabels:
        type: db
        endpoint: crawler-cryptocurrency-app
        function: crawler
        data: cryptocurrency
  template:
    metadata:
      labels:
        type: db
        endpoint: crawler-cryptocurrency-app
        function: crawler
        data: cryptocurrency
    spec:
      volumes:
      - name: crawler-cryptocurrency-data
        persistentVolumeClaim:
          claimName: postgres-crawler-cryptocurrency
      - name: secrets
        secret:
          secretName: crawler-cryptocurrency
      - name: dshm
        emptyDir:
          medium: Memory
      containers:
      # PGBouncer Container
      - name: pgbouncer
        image: bitnami/pgbouncer:1.21.0
        env:
        - name: POSTGRESQL_USERNAME
          value: pumpwood
        - name: POSTGRESQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-test-bouncer
              key: db_password
        - name: POSTGRESQL_HOST
          value: 0.0.0.0
        - name: PGBOUNCER_DATABASE
          value: pumpwood
        - name: PGBOUNCER_SET_DATABASE_USER
          value: 'yes'
        - name: PGBOUNCER_SET_DATABASE_PASSWORD
          value: 'yes'
        - name: PGBOUNCER_POOL_MODE
          value: transaction
        ports:
        - containerPort: 6432

      - name: postgres
        image: postgis/postgis:15-3.3-alpine
        args: [
            "-c", "max_connections=1000",
            "-c", "work_mem=50MB",
            "-c", "shared_buffers=1GB",
            "-c", "max_locks_per_transaction=500",
            "-c", "max_wal_size=10GB",
            "-c", "min_wal_size=80MB"]
        imagePullPolicy: IfNotPresent
        resources:
          requests:
            memory: "{requests_memory}"
            cpu:  "{requests_cpu}"
          limits:
            memory: "{limits_memory}"
            cpu:  "{limits_cpu}"
        env:
        - name: POSTGRES_USER
          value: pumpwood
        - name: POSTGRES_DB
          value: pumpwood
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: crawler-cryptocurrency
              key: db_password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata

        volumeMounts:
        - name: crawler-cryptocurrency-data
          mountPath: /var/lib/postgresql/data/
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
  name: postgres-crawler-cryptocurrency
  labels:
    type: db
    endpoint: crawler-cryptocurrency-app
    function: crawler
    data: cryptocurrency
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 6432
  selector:
    type: db
    endpoint: crawler-cryptocurrency-app
    function: crawler
    data: cryptocurrency
---
apiVersion : "v1"
kind: Service
metadata:
  name: postgres-crawler-cryptocurrency-no-bouncer
  labels:
    type: db-no-bouncer
    endpoint: crawler-cryptocurrency-app
    function: crawler
    data: cryptocurrency
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    type: db
    endpoint: crawler-cryptocurrency-app
    function: crawler
    data: cryptocurrency
"""
