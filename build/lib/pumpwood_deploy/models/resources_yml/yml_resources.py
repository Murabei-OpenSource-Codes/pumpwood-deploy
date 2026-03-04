app_yml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pumpwood-model--{model_type}--app
spec:
  replicas: 1
  selector:
    matchLabels:
      type: model
      model_type: {model_type}
      role: app
  template:
    metadata:
      labels:
        type: model
        model_type: {model_type}
        role: app
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: bucket-key
        secret:
          secretName: bucket-key
      containers:
      - name: pumpwood-model--{model_type}--app
        image: {repository}/pumpwood-model--{model_type}--app:{version}
        imagePullPolicy: IfNotPresent
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: bucket-key
            readOnly: true
            mountPath: /etc/secrets
        readinessProbe:
          httpGet:
            path: /health-check/model-api/{model_type}
            port: 5000
        env:
        # Config
        - name: APP_DEBUG
          value: "False"
        - name: WORKERS_TIMEOUT
          value: "{workers_timeout}"

        # Google
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: "/etc/secrets/key-storage.json"
        - name: STORAGE_BUCKET_NAME
          value: {bucket_name}
        - name: STORAGE_TYPE
          value: 'google_bucket'

        # RABBITMQ QUEUE
        - name: RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rabbitmq-main-secrets
              key: password

        # Microsservice
        - name: MICROSERVICE_NAME
          value: 'app-model--{model_type}'
        - name: MICROSERVICE_PASSWORD
          valueFrom:
              secretKeyRef:
                name: microservice-model-secrets
                key: password
        ports:
        - containerPort: 5000
---
apiVersion : "v1"
kind: Service
metadata:
  name: modelrun--{model_type}
  labels:
    role: app
    type: model
    model_type: {model_type}
    endpoint: modelrun--{model_type}
spec:
  type: ClusterIP
  ports:
    - port: 5000
      targetPort: 5000
  selector:
      role: app
      type: model
      model_type: {model_type}
"""


estimation_yml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pumpwood-model--{model_type}--estimation-worker
spec:
  replicas: 1
  selector:
    matchLabels:
      type: model
      role: estimation
      model_type: {model_type}
  template:
    metadata:
      labels:
        type: model
        role: estimation
        model_type: {model_type}
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: bucket-key
        secret:
          secretName: bucket-key
      containers:
      - name: pumpwood-model--{model_type}--estimation
        image: {repository}/pumpwood-model--{model_type}--estimation-worker:{version}
        imagePullPolicy: IfNotPresent
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: bucket-key
            readOnly: true
            mountPath: /etc/secrets
        env:
        # Google
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: "/etc/secrets/key-storage.json"
        - name: STORAGE_BUCKET_NAME
          value: {bucket_name}
        - name: STORAGE_TYPE
          value: 'google_bucket'

        # RABBITMQ QUEUE
        - name: RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rabbitmq-main-secrets
              key: password

        # Microsservice
        - name: MICROSERVICE_NAME
          value: 'estimation-model--{model_type}'
        - name: MICROSERVICE_PASSWORD
          valueFrom:
              secretKeyRef:
                name: microservice-model-secrets
                key: password
        ports:
        - containerPort: 5000
"""

prediction_yml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pumpwood-model--{model_type}--prediction-worker
spec:
  replicas: 1
  selector:
    matchLabels:
      type: model
      role: prediction
      model_type: {model_type}
  template:
    metadata:
      labels:
        type: model
        role: prediction
        model_type: {model_type}
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: bucket-key
        secret:
          secretName: bucket-key
      containers:
      - name: pumpwood-model--{model_type}--prediction
        image: {repository}/pumpwood-model--{model_type}--prediction-worker:{version}
        imagePullPolicy: IfNotPresent
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: bucket-key
            readOnly: true
            mountPath: /etc/secrets
        env:
        # Google
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: "/etc/secrets/key-storage.json"
        - name: STORAGE_BUCKET_NAME
          value: {bucket_name}
        - name: STORAGE_TYPE
          value: 'google_bucket'

        # RABBITMQ QUEUE
        - name: RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rabbitmq-main-secrets
              key: password

        # Microsservice
        - name: MICROSERVICE_NAME
          value: 'prediction-model--{model_type}'
        - name: MICROSERVICE_PASSWORD
          valueFrom:
              secretKeyRef:
                name: microservice-model-secrets
                key: password
        ports:
        - containerPort: 5000
"""
