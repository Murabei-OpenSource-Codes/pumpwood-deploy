app_deployment = """
apiVersion : "apps/v1"
kind: Deployment
metadata:
  name: simple-airflow--webserver
spec:
  replicas: 1
  selector:
    matchLabels:
      type: app
      endpoint: airflow
      function: webserver
  template:
    metadata:
      labels:
        type: app
        endpoint: airflow
        function: webserver
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: gcp--storage-key
        secret:
          secretName: gcp--storage-key
      containers:
      - name: simple-airflow--webserver
        image: andrebaceti/simple-airflow:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: gcp--storage-key
            readOnly: true
            mountPath: /etc/secrets
        env:
        - name: HASH_SALT
          valueFrom:
            secretKeyRef:
              name: hash-salt
              key: hash_salt

        # AIRFLOW
        - name: AIRFLOW__WEBSERVER__SECRET_KEY_SECRET
          valueFrom:
            secretKeyRef:
              name: simple-airflow
              key: secret_key

        # DATABASE
        - name: DB_HOST
          value: "postgres-simple-airflow"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: simple-airflow
              key: db_password

        # MICROSSERVICE
        - name: MICROSERVICE_PASSWORD
          valueFrom:
              secretKeyRef:
                name: simple-airflow
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
        ports:
        - containerPort: 8080
---
apiVersion : "v1"
kind: Service
metadata:
  name: simple-airflow--webserver
  labels:
    type: app
    endpoint: airflow
    function: webserver
spec:
  type: ClusterIP
  ports:
    - port: 5000
      targetPort: 8080
  selector:
    type: app
    endpoint: airflow
    function: webserver
"""


scheduler_deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: simple-airflow--scheduler
spec:
  replicas: 1
  selector:
    matchLabels:
      type: worker
      endpoint: airflow
      function: scheduler
  template:
    metadata:
      labels:
        type: worker
        endpoint: airflow
        function: scheduler
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: gcp--storage-key
        secret:
          secretName: gcp--storage-key
      command: ["bash", "/app/start_airflow__scheduler.sh"]
      containers:
      - name: simple-airflow--scheduler
        image: andrebaceti/simple-airflow:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: gcp--storage-key
            readOnly: true
            mountPath: /etc/secrets
        env:
        - name: HASH_SALT
          valueFrom:
            secretKeyRef:
              name: hash-salt
              key: hash_salt

        # AIRFLOW
        - name: AIRFLOW__WEBSERVER__SECRET_KEY_SECRET
          valueFrom:
            secretKeyRef:
              name: simple-airflow
              key: secret_key

        # DATABASE
        - name: DB_HOST
          value: "postgres-simple-airflow"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: simple-airflow
              key: db_password

        # MICROSSERVICE
        - name: MICROSERVICE_PASSWORD
          valueFrom:
              secretKeyRef:
                name: simple-airflow
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

worker_deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: simple-airflow--worker
spec:
  replicas: 1
  selector:
    matchLabels:
      type: worker
      endpoint: airflow
      function: worker
  template:
    metadata:
      labels:
        type: worker
        endpoint: airflow
        function: worker
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: gcp--storage-key
        secret:
          secretName: gcp--storage-key
      command: ["bash", "/app/start_airflow__worker.sh"]
      containers:
      - name: simple-airflow--scheduler
        image: andrebaceti/simple-airflow:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: gcp--storage-key
            readOnly: true
            mountPath: /etc/secrets
        env:
        - name: HASH_SALT
          valueFrom:
            secretKeyRef:
              name: hash-salt
              key: hash_salt

        # DATABASE
        - name: DB_HOST
          value: "postgres-simple-airflow"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: simple-airflow
              key: db_password

        # MICROSSERVICE
        - name: MICROSERVICE_PASSWORD
          valueFrom:
              secretKeyRef:
                name: simple-airflow
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


secrets = """
apiVersion: v1
kind: Secret
metadata:
  name: simple-airflow
type: Opaque
data:
  db_password: {db_password}
  microservice_password: {microservice_password}
  secret_key: {secret_key}
"""


services__load_balancer = """
apiVersion : "v1"
kind: Service
metadata:
  name: simple-airflow--webserver
  labels:
    type: loadbalancer-app
    endpoint: simple-airflow
    function: webserver
spec:
  type: LoadBalancer
  ports:
    - port: 7000
      targetPort: 5432
  selector:
    type: app
    endpoint: airflow
    function: webserver
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
  name: postgres-pumpwood-datalake
  labels:
    usage: postgres-pumpwood-datalake
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
  name: postgres-pumpwood-datalake
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: {disk_size}
  volumeName: postgres-pumpwood-datalake
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
