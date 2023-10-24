deployment_yml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pumpwood-frontend-react
spec:
  replicas: 1
  selector:
    matchLabels:
      type: frontend
      function: pumpwood-default
  template:
    metadata:
      labels:
        type: frontend
        function: pumpwood-default
    spec:
      imagePullSecrets:
        - name: dockercfg
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: function
                operator: NotIn
                values:
                - system
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
      - name: pumpwood-frontend-react
        image: {repository}/pumpwood-frontend-react:{version}
        imagePullPolicy: IfNotPresent
        env:
        - name: NEXT_PUBLIC_APP_API_HOST
          value: '{gateway_public_ip}'
        - name: NEXT_PUBLIC_METABASE_SITE_URL
          value: '{gateway_public_ip}/metabase'
        - name: NEXT_PUBLIC_METABASE_SECRET_KEY
          value: 'oi-sou-a-senha-metabase'
        - name: DEBUG
          value: '{debug}'

        # Microservice
        - name: MICROSERVICE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: pumpwood-frontend-react
              key: microservice_password

        ports:
        - containerPort: 5000
---
apiVersion : "v1"
kind: Service
metadata:
  name: pumpwood-frontend-react
  labels:
    type: frontend
    function: pumpwood-default
spec:
  type: ClusterIP
  ports:
    - port: 5000
      targetPort: 5000
  selector:
    type: frontend
    function: pumpwood-default
"""

secrets_yml = """
apiVersion: v1
kind: Secret
metadata:
  name: pumpwood-frontend-react
type: Opaque
data:
  microservice_password: {microservice_password}
"""
