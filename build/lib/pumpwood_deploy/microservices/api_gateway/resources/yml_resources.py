nginx_gateway_deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: apigateway-nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      type: apigateway-nginx
  template:
    metadata:
      labels:
        type: apigateway-nginx
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
      containers:
      - name: apigateway-nginx
        image: {repository}/pumpwood-nginx-ssl-gateway:{nginx_ssl_version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
        readinessProbe:
          httpGet:
            path: {health_check_url}
            port: 80
        ports:
        # Consumers Ports
        - containerPort: 80
        env:
        - name: SERVER_NAME
          value: "{server_name}"
        - name: EMAIL
          value: "{email_contact}"
"""

nginx_gateway_secrets_deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: apigateway-nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      type: apigateway-nginx
  template:
    metadata:
      labels:
        type: apigateway-nginx
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: ssl-credentials-key
        secret:
          secretName: ssl-credentials-key
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
      - name: apigateway-nginx
        image: {repository}/pumpwood-nginx-ssl-secrets-gateway:{nginx_ssl_version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: ssl-credentials-key
            readOnly: true
            mountPath: /credentials/
        readinessProbe:
          httpGet:
            path: {health_check_url}
            port: 80
        ports:
        # Consumers Ports
        - containerPort: 80
        env:
        - name: SERVER_NAME
          value: "{server_name}"
        - name: GOOGLE_PROJECT_ID
          value: "{google_project_id}"
        - name: SECRET_ID
          value: "{secret_id}"
"""

external_service = """
apiVersion : "v1"
kind: Service
metadata:
  name: apigateway-nginx
  labels:
    type: apigateway
    destination: external
spec:
  type: LoadBalancer
  selector:
    type: apigateway-nginx
  ports:
    - name: https
      port: 443
      targetPort: 443
    - name: http
      port: 80
      targetPort: 80
  loadBalancerIP: {{ public_ip }}
  loadBalancerSourceRanges:
    {%- for ip in firewall_ips %}
      - {{ip}}
    {%- endfor %}
"""

internal_service = """
apiVersion : "v1"
kind: Service
metadata:
  name: apigateway-nginx
  annotations:
      networking.gke.io/load-balancer-type: "Internal"
  labels:
    type: apigateway
    destination: external
spec:
  type: LoadBalancer
  selector:
    type: apigateway-nginx
  ports:
    - name: https
      port: 443
      targetPort: 443
    - name: http
      port: 80
      targetPort: 80
  loadBalancerIP: {public_ip}
"""
