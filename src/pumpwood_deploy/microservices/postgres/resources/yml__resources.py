"""K8s manifest templates."""

deployment_postgres = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
spec:
  replicas: 1
  selector:
    matchLabels:
      type: db
      endpoint: {name}
      function: not-microservice
  template:
    metadata:
      labels:
        type: db
        endpoint: {name}
        function: not-microservice
    spec:
      volumes:
      - name: postgres-data
        persistentVolumeClaim:
          claimName: {volume_claim_name}
      - name: secrets
        secret:
          secretName: {name}
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

      # Postgres Container
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
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: {name}
              key: db_password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        volumeMounts:
        - name: postgres-data
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
  name: {name}
  labels:
    type: db
    endpoint: {name}
    function: not-microservice
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 6432
  selector:
    type: db
    endpoint: {name}
    function: not-microservice
---
apiVersion : "v1"
kind: Service
metadata:
  name: {name}-not-bouncer
  labels:
    type: db-not-bouncer
    endpoint: {name}
    function: not-microservice
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    type: db
    endpoint: {name}
    function: not-microservice
"""

secrets = """
apiVersion: v1
kind: Secret
metadata:
  name: {name}
type: Opaque
data:
  db_password: {db_password}
  ssl_key: {ssl_key}
  ssl_crt: {ssl_crt}
---
apiVersion: v1
kind: Secret
metadata:
  name: {name}-ssl-keys
type: Opaque
data:
  ssl_key: {ssl_key}
  ssl_crt: {ssl_crt}
"""
