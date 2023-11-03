app_deployment = """
apiVersion : "apps/v1"
kind: Deployment
metadata:
  name: metabase-app
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      type: app
      endpoint: metabase-app
      function: dashboard
  template:
    metadata:
      labels:
          type: app
          endpoint: metabase-app
          function: dashboard
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: gcp--storage-key
        secret:
          secretName: gcp--storage-key
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
      - name: metabase
        image: andrebaceti/metabase-pumpwood:v0.47.6
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
            path: api/health
            port: 3000
        ports:
        - containerPort: 3000
        env:
        ############
        # Metabase #
        - name: MB_SITE_URL
          valueFrom:
            configMapKeyRef:
              name: metabase
              key: site_url
        - name: MB_EMBEDDING_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: metabase
              key: embedding_secret_key
        - name: MB_ENCRYPTION_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: metabase
              key: encryption_secret_key

        ############
        # Database #
        - name: MB_DB_TYPE
          value: "postgres"
        - name: MB_DB_DBNAME
          value: "metabase"
        - name: MB_DB_PORT
          value: "5432"
        - name: MB_DB_USER
          value: "metabase"
        - name: MB_DB_HOST
          value: "postgres-metabase"
        - name: MB_DB_PASS
          valueFrom:
            secretKeyRef:
              name: metabase
              key: db_password
---
apiVersion : "v1"
kind: Service
metadata:
  name: metabase-app
  labels:
      type: app
      endpoint: metabase-app
      function: dashboard
spec:
  type: ClusterIP
  ports:
    - port: 3000
      targetPort: 3000
  selector:
      type: app
      endpoint: metabase-app
      function: dashboard
"""

secrets = """
apiVersion: v1
kind: Secret
metadata:
  name: metabase
type: Opaque
data:
  db_password: {db_password}
  embedding_secret_key: {embedding_secret_key}
  encryption_secret_key: {encryption_secret_key}
  ssl_key: {ssl_key}
  ssl_crt: {ssl_crt}
"""

config_map = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: metabase
data:
  site_url: "{site_url}"
"""

services__load_balancer = """
apiVersion : "v1"
kind: Service
metadata:
  name: loadbalancer-postgres-metabase
  labels:
      type: loadbalancer-db
      endpoint: metabase-app
      function: dashboard
spec:
  type: LoadBalancer
  ports:
    - port: 7000
      targetPort: 5432
  selector:
      type: db
      endpoint: metabase-app
      function: dashboard
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
  name: postgres-metabase
spec:
  replicas: 1
  selector:
    matchLabels:
      type: db
      endpoint: metabase-app
      function: dashboard
  template:
    metadata:
      labels:
        type: db
        endpoint: metabase-app
        function: dashboard
    spec:
      volumes:
      - name: metabase-data
        persistentVolumeClaim:
          claimName: postgres-metabase
      - name: secrets
        secret:
          secretName: metabase
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
      - name: postgres-metabase
        image: postgis/postgis:15-3.3-alpine
        args: [
            "-c", "max_connections=1000",
            "-c", "work_mem=50MB",
            "-c", "shared_buffers=5GB",
            "-c", "max_locks_per_transaction=500",
            "-c", "synchronous_commit=off",
            "-c", "max_wal_size=10GB",
            "-c", "min_wal_size=80MB",
            "-c", "effective_io_concurrency=200",
            "-c", "max_worker_processes=50",
            "-c", "max_parallel_workers=20",
            "-c", "max_parallel_workers_per_gather=10"]
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
          value: metabase
        - name: POSTGRES_DB
          value: metabase
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: metabase
              key: db_password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata

        volumeMounts:
        - name: metabase-data
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
  name: postgres-metabase
  labels:
    type: db
    endpoint: metabase-app
    function: dashboard
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    type: db
    endpoint: metabase-app
    function: dashboard
"""


test_postgres = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-metabase
spec:
  replicas: 1
  selector:
    matchLabels:
      type: db
      endpoint: metabase-app
      function: dashboard
  template:
    metadata:
      labels:
        type: db
        endpoint: metabase-app
        function: dashboard
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
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
      - name: postgres-metabase
        image: {repository}/test-db-metabase:{version}
        imagePullPolicy: IfNotPresent
        resources:
          requests:
            memory: "{requests_memory}"
            cpu:  "{requests_cpu}"
          limits:
            memory: "{limits_memory}"
            cpu:  "{limits_cpu}"
        volumeMounts:
        - name: dshm
          mountPath: /dev/shm
        ports:
        - containerPort: 5432
---
apiVersion : "v1"
kind: Service
metadata:
  name: postgres-metabase
  labels:
    type: db
    endpoint: metabase-app
    function: dashboard
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    type: db
    endpoint: metabase-app
    function: dashboard
"""
