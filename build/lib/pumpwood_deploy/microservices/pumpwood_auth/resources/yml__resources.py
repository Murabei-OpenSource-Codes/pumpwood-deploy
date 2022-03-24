auth_admin_static = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pumpwood-auth-static
spec:
  replicas: 1
  selector:
    matchLabels:
      type: static
      endpoint: pumpwood-auth-app
      function: auth
  template:
    metadata:
      labels:
        type: static
        endpoint: pumpwood-auth-app
        function: auth
    spec:
      imagePullSecrets:
        - name: dockercfg
      containers:
      - name: pumpwood-auth-static
        image: {repository}/pumpwood-auth-static:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "10m"
        ports:
        - containerPort: 5000
---
apiVersion : "v1"
kind: Service
metadata:
  name: pumpwood-auth-admin-static
  labels:
    type: static
    endpoint: pumpwood-auth-app
    function: auth
spec:
  type: ClusterIP
  ports:
    - port: 5000
      targetPort: 5000
  selector:
    type: static
    endpoint: pumpwood-auth-app
    function: auth
"""

app_deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pumpwood-auth-app
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      type: app
      endpoint: pumpwood-auth-app
      function: auth
  template:
    metadata:
      labels:
        type: app
        endpoint: pumpwood-auth-app
        function: auth
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: secrets
        secret:
          secretName: pumpwood-auth
      volumes:
      - name: bucket-key
        secret:
          secretName: bucket-key
      containers:
      - name: pumpwood-auth-app
        image: {repository}/pumpwood-auth-app:{version}
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
            path: /health-check/pumpwood-auth-app/
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

        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: pumpwood-auth
              key: secret_key

        # Google
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: "/etc/secrets/key-storage.json"
        - name: STORAGE_BUCKET_NAME
          value: {bucket_name}
        - name: STORAGE_TYPE
          value: 'google_bucket'

        # Database
        - name: DB_HOST
          value: postgres-pumpwood-auth
        - name: DB_PASS
          valueFrom:
            secretKeyRef:
              name: pumpwood-auth
              key: db_password

        # Microservice
        - name: MICROSERVICE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: pumpwood-auth
              key: microservice_password

        # Email
        - name: EMAIL_HOST_USER
          valueFrom:
            secretKeyRef:
              name: pumpwood-auth
              key: email_host_user
        - name: EMAIL_HOST_PASSWORD
          valueFrom:
            secretKeyRef:
              name: pumpwood-auth
              key: email_host_password
---
apiVersion : "v1"
kind: Service
metadata:
  name: pumpwood-auth-app
  labels:
    type: app
    endpoint: pumpwood-auth-app
    function: auth
spec:
  type: ClusterIP
  ports:
    - port: 5000
      targetPort: 5000
  selector:
    type: app
    endpoint: pumpwood-auth-app
    function: auth
"""

deployment_postgres = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-pumpwood-auth
spec:
  replicas: 1
  selector:
    matchLabels:
      type: db
      endpoint: pumpwood-auth-app
      function: auth
  template:
    metadata:
      labels:
        type: db
        endpoint: pumpwood-auth-app
        function: auth
    spec:
      volumes:
      - name: postgres-pumpwood-auth-data
        persistentVolumeClaim:
          claimName: postgres-pumpwood-auth
      - name: postgres-init-configmap
        configMap:
          name: postgres-init-configmap
      - name: secrets
        secret:
          secretName: pumpwood-auth
      - name: dshm
        emptyDir:
          medium: Memory

      containers:
      - name: postgres-pumpwood-auth
        image: timescale/timescaledb-postgis:1.7.3-pg12
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
        env:
        - name: POSTGRES_USER
          value: pumpwood
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: pumpwood-auth
              key: db_password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        volumeMounts:
        - name: postgres-pumpwood-auth-data
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
  name: postgres-pumpwood-auth
  labels:
    type: db
    endpoint: pumpwood-auth-app
    function: auth
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    type: db
    endpoint: pumpwood-auth-app
    function: auth
"""

secrets = """
apiVersion: v1
kind: Secret
metadata:
  name: pumpwood-auth
type: Opaque
data:
  db_password: {db_password}
  microservice_password: {microservice_password}
  email_host_user: {email_host_user}
  email_host_password: {email_host_password}
  ssl_key: {ssl_key}
  ssl_crt: {ssl_crt}
  secret_key: {secret_key}
---
apiVersion: v1
kind: Secret
metadata:
  name: pumpwood-auth-postgres-ssl-keys
type: Opaque
data:
  ssl_key: {ssl_key}
  ssl_crt: {ssl_crt}
"""


services__load_balancer = """
apiVersion : "v1"
kind: Service
metadata:
  name: loadbalancer-postgres-pumpwood-auth
  labels:
    type: loadbalancer-db
    endpoint: pumpwood-auth-app
    function: auth
spec:
  type: LoadBalancer
  selector:
    type: db
    endpoint: pumpwood-auth-app
    function: auth
  ports:
    - port: 7000
      targetPort: 5432
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
  name: postgres-pumpwood-auth
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: {disk_size}
  volumeName: {disk_name}
"""


test_postgres = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-pumpwood-auth
spec:
  replicas: 1
  selector:
    matchLabels:
      type: db
      endpoint: pumpwood-auth-app
      function: auth
  template:
    metadata:
      labels:
        type: db
        endpoint: pumpwood-auth-app
        function: auth
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: dshm
        emptyDir:
          medium: Memory

      containers:
      - name: postgres-pumpwood-auth
        image: {repository}/test-db-pumpwood-auth:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
        - name: dshm
          mountPath: /dev/shm
        ports:
        - containerPort: 5432
---
apiVersion : "v1"
kind: Service
metadata:
  name: postgres-pumpwood-auth
  labels:
    type: db
    endpoint: pumpwood-auth-app
    function: auth
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    type: db
    endpoint: pumpwood-auth-app
    function: auth
"""
