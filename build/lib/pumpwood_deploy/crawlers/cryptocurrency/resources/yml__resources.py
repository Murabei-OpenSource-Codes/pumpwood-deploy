app_deployment = """
apiVersion : "apps/v1"
kind: Deployment
metadata:
  name: crawler-cryptocurrency-app
spec:
  replicas: 1
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
      - name: bucket-key
        secret:
          secretName: bucket-key
      containers:
      - name: crawler-cryptocurrency
        image: {repository}/crawler-cryptocurrency-app:{version}
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
            path: /health-check/crawler-cryptocurrency-app/
            port: 5000
        env:
        - name: APP_DEBUG
          value: "False"

        - name: HASH_SALT
          valueFrom:
            secretKeyRef:
              name: hash-salt
              key: hash_salt

        # Database
        - name: DB_HOST
          value: "postgres-crawler-cryptocurrency"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: crawler-cryptocurrency
              key: db_password

        # Google
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: "/etc/secrets/key-storage.json"
        - name: STORAGE_BUCKET_NAME
          value: {bucket_name}
        - name: STORAGE_TYPE
          value: 'google_bucket'

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
                name: crawler-cryptocurrency
                key: microservice_password

        # workers_timeout
        - name: WORKERS_TIMEOUT
          value: "{workers_timeout}"
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


worker_deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crawler-cryptocurrency-worker
spec:
  replicas: 1
  selector:
    matchLabels:
      type: worker
      endpoint: crawler-cryptocurrency-app
  template:
    metadata:
      labels:
          type: worker
          endpoint: crawler-cryptocurrency-app
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: bucket-key
        secret:
          secretName: bucket-key
      containers:
      - name: crawler-cryptocurrency-worker
        image: {repository}/crawler-cryptocurrency-worker:{version}
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
          value: "postgres-crawler-cryptocurrency"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: crawler-cryptocurrency
              key: db_password

        # Google
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: "/etc/secrets/key-storage.json"
        - name: STORAGE_BUCKET_NAME
          value: {bucket_name}
        - name: STORAGE_TYPE
          value: 'google_bucket'

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

secrets = """
apiVersion: v1
kind: Secret
metadata:
  name: crawler-cryptocurrency
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

volume_postgres = """
kind: PersistentVolume
apiVersion: v1
metadata:
  name: postgres-crawler-cryptocurrency
  labels:
    usage: postgres-crawler-cryptocurrency
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
  name: postgres-crawler-cryptocurrency
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: {disk_size}
  volumeName: postgres-crawler-cryptocurrency
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
      - name: postgres-init-configmap
        configMap:
          name: postgres-init-configmap
      - name: secrets
        secret:
          secretName: crawler-cryptocurrency
      - name: dshm
        emptyDir:
          medium: Memory
      containers:
      - name: postgres-crawler-cryptocurrency
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
              name: crawler-cryptocurrency
              key: db_password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata

        volumeMounts:
        - name: crawler-cryptocurrency-data
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
      targetPort: 5432
  selector:
    type: db
    endpoint: crawler-cryptocurrency-app
    function: crawler
    data: cryptocurrency
"""
