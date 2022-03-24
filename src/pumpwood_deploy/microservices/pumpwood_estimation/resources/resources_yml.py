app_deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pumpwood-estimation-app
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      type: app
      endpoint: pumpwood-estimation-app
      function: estimation
  template:
    metadata:
      labels:
        type: app
        endpoint: pumpwood-estimation-app
        function: estimation
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: bucket-key
        secret:
          secretName: bucket-key
      containers:
      - name: pumpwood-estimation
        image: {repository}/pumpwood-estimation-app:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: bucket-key
            readOnly: true
            mountPath: /etc/secrets
        readinessProbe:
          httpGet:
            path: /health-check/pumpwood-estimation-app/
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
        - name: DB_HOST
          value: "postgres-pumpwood-estimation"
        - name: DB_USERNAME
          value: pumpwood
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: pumpwood-estimation
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
                name: pumpwood-estimation
                key: microservice_password

        # Timeout
        - name: WORKERS_TIMEOUT
          value: "{workers_timeout}"
        ports:
        - containerPort: 5000
---
apiVersion : "v1"
kind: Service
metadata:
  name: pumpwood-estimation-app
  labels:
    type: app
    endpoint: pumpwood-estimation-app
    function: estimation
spec:
  type: ClusterIP
  ports:
    - port: 5000
      targetPort: 5000
  selector:
    type: app
    endpoint: pumpwood-estimation-app
    function: estimation
"""

worker_deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pumpwood-estimation-rawdata-workers
spec:
  replicas: 1
  selector:
    matchLabels:
      type: worker
      endpoint: pumpwood-estimation-app
      function: raw-data-builder
  template:
    metadata:
      labels:
        type: worker
        endpoint: pumpwood-estimation-app
        function: raw-data-builder
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: bucket-key
        secret:
          secretName: bucket-key
      containers:
      - name: pumpwood-estimation-rawdata-workers
        image: {repository}/pumpwood-estimation-rawdata-worker:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: bucket-key
            readOnly: true
            mountPath: /etc/secrets
        env:
        # HASH_SALT
        - name: HASH_SALT
          valueFrom:
            secretKeyRef:
              name: hash-salt
              key: hash_salt

        #DATABASE
        - name: DB_HOST
          value: "postgres-pumpwood-datalake"
        - name: DB_USERNAME
          value: pumpwood
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: pumpwood-datalake
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
        - name: MICROSERVICE_NAME
          value: 'pumpwood-estimation-rawdata'
        - name: MICROSERVICE_PASSWORD
          valueFrom:
              secretKeyRef:
                name: pumpwood-estimation
                key: microservice_password
"""

secrets = """
apiVersion: v1
kind: Secret
metadata:
  name: pumpwood-estimation
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
  name: loadbalancer-postgres-pumpwood-estimation
  labels:
    type: loadbalancer-db
    db: postgres-pumpwood-estimation
spec:
  type: LoadBalancer
  ports:
    - port: 7000
      targetPort: 5432
  selector:
    type: db
    db: postgres-pumpwood-estimation
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
  name: postgres-pumpwood-estimation
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
  name: postgres-pumpwood-estimation
spec:
  replicas: 1
  selector:
    matchLabels:
      type: db
      endpoint: pumpwood-estimation-app
      function: estimation
  template:
    metadata:
      labels:
        type: db
        endpoint: pumpwood-estimation-app
        function: estimation
    spec:
      volumes:
      - name: pumpwood-estimation-data
        persistentVolumeClaim:
          claimName: postgres-pumpwood-estimation
      - name: postgres-init-configmap
        configMap:
          name: postgres-init-configmap
      - name: secrets
        secret:
          secretName: pumpwood-estimation
      - name: dshm
        emptyDir:
          medium: Memory

      containers:
      - name: postgres-pumpwood-estimation
        image: timescale/timescaledb-postgis:1.7.3-pg12
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
          limits:
            cpu: "2"
        env:
        - name: POSTGRES_USER
          value: pumpwood
        - name: POSTGRES_DB
          value: pumpwood
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: pumpwood-estimation
              key: db_password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata

        volumeMounts:
        - name: pumpwood-estimation-data
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
  name: postgres-pumpwood-estimation
  labels:
    type: db
    endpoint: pumpwood-estimation-app
    function: estimation
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    type: db
    endpoint: pumpwood-estimation-app
    function: estimation
"""

test_postgres = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-pumpwood-estimation
spec:
  replicas: 1
  selector:
    matchLabels:
      type: db
      endpoint: pumpwood-estimation-app
      function: estimation
  template:
    metadata:
      labels:
        type: db
        endpoint: pumpwood-estimation-app
        function: estimation
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: dshm
        emptyDir:
          medium: Memory

      containers:
      - name: postgres-pumpwood-estimation
        image: {repository}/test-db-pumpwood-estimation:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
          limits:
            cpu: "2"
        volumeMounts:
        - name: dshm
          mountPath: /dev/shm
---
apiVersion : "v1"
kind: Service
metadata:
  name: postgres-pumpwood-estimation
  labels:
    type: db
    endpoint: pumpwood-estimation-app
    function: estimation
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    type: db
    endpoint: pumpwood-estimation-app
    function: estimation
"""
