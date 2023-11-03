coordinator_deployment = """
apiVersion : "apps/v1"
kind: Deployment
metadata:
  name: trino-coordinator
spec:
  replicas: 1
  selector:
    matchLabels:
      type: db
      endpoint: trino
      function: coordinator
  template:
    metadata:
      labels:
          type: db
          endpoint: trino
          function: coordinator
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: trino--catalog-file-secret
        secret:
          secretName: trino--catalog-file-secret
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
      - name: trino-coordinator
        image: andrebaceti/trino-coordinator:430-1.1
        imagePullPolicy: IfNotPresent
        resources:
          requests:
            memory: "{requests_memory}"
            cpu:  "{requests_cpu}"
          limits:
            memory: "{limits_memory}"
            cpu:  "{limits_cpu}"
        volumeMounts:
          - name: trino--catalog-file-secret
            readOnly: true
            mountPath: /catalog
        ports:
        - containerPort: 8080
        env:
        ############
        # Metabase #
        - name: SHARED_SECRET
          valueFrom:
            secretKeyRef:
              name: trino
              key: shared_secret
---
apiVersion : "v1"
kind: Service
metadata:
  name: trino-coordinator
  labels:
      type: app
      endpoint: trino-coordinator
      function: dashboard
spec:
  type: ClusterIP
  ports:
    - port: 8080
      targetPort: 8080
  selector:
      type: db
      endpoint: trino
      function: coordinator
"""

worker_deployment = """
apiVersion : "apps/v1"
kind: Deployment
metadata:
  name: trino-worker
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      type: db
      endpoint: trino
      function: worker
  template:
    metadata:
      labels:
          type: db
          endpoint: trino
          function: worker
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: trino--catalog-file-secret
        secret:
          secretName: trino--catalog-file-secret
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
      - name: trino-worker
        image: andrebaceti/trino-worker:430-1.1
        imagePullPolicy: IfNotPresent
        resources:
          requests:
            memory: "{requests_memory}"
            cpu:  "{requests_cpu}"
          limits:
            memory: "{limits_memory}"
            cpu:  "{limits_cpu}"
        volumeMounts:
          - name: trino--catalog-file-secret
            readOnly: true
            mountPath: /catalog
        ports:
        - containerPort: 8080
        env:
        ############
        # Metabase #
        - name: SHARED_SECRET
          valueFrom:
            secretKeyRef:
              name: trino
              key: shared_secret
---
apiVersion : "v1"
kind: Service
metadata:
  name: trino-worker
  labels:
      type: app
      endpoint: trino-worker
      function: dashboard
spec:
  type: ClusterIP
  ports:
    - port: 8080
      targetPort: 8080
  selector:
      type: db
      endpoint: trino
      function: worker
"""

secrets_trino = """
apiVersion: v1
kind: Secret
metadata:
  name: trino
type: Opaque
data:
  shared_secret: {shared_secret}
"""
