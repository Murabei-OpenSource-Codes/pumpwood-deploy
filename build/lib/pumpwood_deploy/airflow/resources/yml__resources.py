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
      - name: airflow--gitkey
        secret:
          secretName: airflow--gitkey
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
          - name: airflow--gitkey
            readOnly: true
            mountPath: /ssh_keys/
        ports:
        - containerPort: 8080
        env:
        - name: HASH_SALT
          valueFrom:
            secretKeyRef:
              name: hash-salt
              key: hash_salt

        # AIRFLOW
        - name: AIRFLOW__WEBSERVER__SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: simple-airflow
              key: secret_key
        - name: AIRFLOW__CORE__FERNET_KEY
          valueFrom:
            secretKeyRef:
              name: simple-airflow
              key: fernet_key
        - name: AIRFLOW__KUBERNETES__NAMESPACE
          value: {k8s_pods_namespace}
        - name: AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER
          value: "{remote_base_log_folder}"
        - name: AIRFLOW__LOGGING__REMOTE_LOGGING
          value: "{remote_logging}"
        - name: AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID
          value: "{remote_log_conn_id}"

        # Git
        - name: GIT_SERVER
          value: "{git_server}"
        - name: GIT_REPOSITORY
          value: "{git_repository}"
        - name: GIT_BRANCH
          value: "{git_branch}"

        # DATABASE
        - name: DB_HOST
          value: "postgres-simple-airflow"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: simple-airflow
              key: db_password

        # KONG
        - name: KONG_API_URL
          value: "http://load-balancer:8001"
        - name: SERVICE_URL
          value: "http://simple-airflow--webserver:5000/"

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
      - name: airflow--gitkey
        secret:
          secretName: airflow--gitkey
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
      - name: simple-airflow--scheduler
        image: andrebaceti/simple-airflow:{version}
        imagePullPolicy: Always
        command: ["bash"]
        args: ["/airflow/start_airflow__scheduler.bash"]
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: gcp--storage-key
            readOnly: true
            mountPath: /etc/secrets
          - name: airflow--gitkey
            readOnly: true
            mountPath: /ssh_keys/
        env:
        - name: HASH_SALT
          valueFrom:
            secretKeyRef:
              name: hash-salt
              key: hash_salt

        # AIRFLOW
        - name: AIRFLOW__WEBSERVER__SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: simple-airflow
              key: secret_key
        - name: AIRFLOW__CORE__FERNET_KEY
          valueFrom:
            secretKeyRef:
              name: simple-airflow
              key: fernet_key
        - name: AIRFLOW__KUBERNETES__NAMESPACE
          value: {k8s_pods_namespace}
        - name: AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER
          value: "{remote_base_log_folder}"
        - name: AIRFLOW__LOGGING__REMOTE_LOGGING
          value: "{remote_logging}"
        - name: AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID
          value: "{remote_log_conn_id}"

        # Git
        - name: GIT_SERVER
          value: "{git_server}"
        - name: GIT_REPOSITORY
          value: "{git_repository}"
        - name: GIT_BRANCH
          value: "{git_branch}"

        # DATABASE
        - name: DB_HOST
          value: "postgres-simple-airflow"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: simple-airflow
              key: db_password

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
  replicas: {replicas}
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
      - name: airflow--gitkey
        secret:
          secretName: airflow--gitkey
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
      - name: simple-airflow--scheduler
        image: andrebaceti/simple-airflow:{version}
        imagePullPolicy: Always
        command: ["bash"]
        args: ["/airflow/start_airflow__worker.bash"]
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: gcp--storage-key
            readOnly: true
            mountPath: /etc/secrets
          - name: airflow--gitkey
            readOnly: true
            mountPath: /ssh_keys/
        ports:
        - containerPort: 8793
        env:
        - name: HASH_SALT
          valueFrom:
            secretKeyRef:
              name: hash-salt
              key: hash_salt

        # AIRFLOW
        - name: AIRFLOW__WEBSERVER__SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: simple-airflow
              key: secret_key
        - name: AIRFLOW__CORE__FERNET_KEY
          valueFrom:
            secretKeyRef:
              name: simple-airflow
              key: fernet_key
        - name: AIRFLOW__KUBERNETES__NAMESPACE
          value: {k8s_pods_namespace}
        - name: AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER
          value: "{remote_base_log_folder}"
        - name: AIRFLOW__LOGGING__REMOTE_LOGGING
          value: "{remote_logging}"
        - name: AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID
          value: "{remote_log_conn_id}"
        # Ajust log collection from workers using IP address of the POD
        - name: AIRFLOW__CORE__HOSTNAME_CALLABLE
          value: 'airflow.utils.net:get_host_ip_address'

        # Git
        - name: GIT_SERVER
          value: "{git_server}"
        - name: GIT_REPOSITORY
          value: "{git_repository}"
        - name: GIT_BRANCH
          value: "{git_branch}"

        # DATABASE
        - name: DB_HOST
          value: "postgres-simple-airflow"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: simple-airflow
              key: db_password

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
  secret_key: {secret_key}
  db_password: {db_password}
  microservice_password: {microservice_password}
  fernet_key: {fernet_key}
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

deployment_postgres = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-simple-airflow
spec:
  replicas: 1
  selector:
    matchLabels:
      type: db
      endpoint: simple-airflow-app
  template:
    metadata:
      labels:
        type: db
        endpoint: simple-airflow-app
    spec:
      volumes:
      - name: simple-airflow-data
        persistentVolumeClaim:
          claimName: postgres-simple-airflow
      - name: secrets
        secret:
          secretName: simple-airflow
      - name: dshm
        emptyDir:
          medium: Memory
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
      - name: postgres-simple-airflow
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
              name: simple-airflow
              key: db_password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata

        volumeMounts:
        - name: simple-airflow-data
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
  name: postgres-simple-airflow
  labels:
    type: db
    endpoint: simple-airflow-app
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    type: db
    endpoint: simple-airflow-app
"""


service_account = """
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: airflow--pod-launcher-role
  labels:
    tier: airflow
rules:
  - apiGroups:
      - ""
    resources:
      - "pods"
    verbs:
      - "create"
      - "list"
      - "get"
      - "patch"
      - "watch"
      - "delete"
  - apiGroups:
      - ""
    resources:
      - "pods/log"
    verbs:
      - "get"
  - apiGroups:
      - ""
    resources:
      - "pods/exec"
    verbs:
      - "create"
      - "get"
  - apiGroups:
      - ""
    resources:
      - "events"
    verbs:
      - "list"
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: airflow--pod-launcher-rolebinding
  labels:
    tier: airflow
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: airflow--pod-launcher-role
subjects:
  - kind: ServiceAccount
    name: default
    namespace: {namespace}
"""
