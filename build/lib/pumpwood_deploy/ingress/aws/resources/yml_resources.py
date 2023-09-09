"""Resorces."""

aws_alb_ingress_host = """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: alb-ingress
  namespace: dev
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/load-balancer-name: '{{ alb_name }}'
    alb.ingress.kubernetes.io/group.name: '{{ group_name }}'
    alb.ingress.kubernetes.io/ip-address-type: ipv4
    alb.ingress.kubernetes.io/scheme: internal
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS": 443}]'
    alb.ingress.kubernetes.io/ssl-redirect: '443'
    alb.ingress.kubernetes.io/healthcheck-path: {{ health_check_url }}
    alb.ingress.kubernetes.io/certificate-arn: {{ certificate_arn }}
spec:
  rules:
  - host: {{ host }}
    http:
      paths:
      - pathType: Prefix
        path: {{ path }}
        backend:
          service:
            name: {{ service_name }}
            port:
              number: {{ service_port }}
"""

aws_alb_ingress_path = """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: alb-ingress
  namespace: dev
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/load-balancer-name: '{{ alb_name }}'
    alb.ingress.kubernetes.io/group.name: '{{ group_name }}'
    alb.ingress.kubernetes.io/ip-address-type: ipv4
    alb.ingress.kubernetes.io/scheme: internal
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS": 443}]'
    alb.ingress.kubernetes.io/ssl-redirect: '443'
    alb.ingress.kubernetes.io/healthcheck-path: {{ health_check_url }}
    alb.ingress.kubernetes.io/certificate-arn: {{ certificate_arn }}
spec:
  rules:
  - http:
      paths:
      - pathType: Prefix
        path: {{ path }}
        backend:
          service:
            name: {{ service_name }}
            port:
              number: {{ service_port }}
"""

aws_nlb_healthcheck = """
apiVersion: v1
kind: Namespace
metadata:
  name: healthcheck
  labels:
    name: healthcheck
---
kind: Pod
apiVersion: v1
metadata:
  name: healthcheck-app
  namespace: healthcheck
  labels:
    app: healthcheck
spec:
  containers:
    - name: healthcheck-app
      image: andrebaceti/k8s-health-check-container:0.1
      ports:
        - containerPort: 80
      env:
      - name: HEALTH_CHECK_PATH
        value: "k8s-health-check/"
---
kind: Service
apiVersion: v1
metadata:
  name: healthcheck-service
  namespace: healthcheck
spec:
  selector:
    app: healthcheck
  ports:
    - port: 80
"""

aws_nlb_healthcheck_ingress = """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: alb-ingress-v3
  namespace: healthcheck
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/load-balancer-name: '{{ alb_name }}'
    alb.ingress.kubernetes.io/group.name: '{{ group_name }}'
    alb.ingress.kubernetes.io/ip-address-type: ipv4
    alb.ingress.kubernetes.io/scheme: internal
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS": 443}]'
    alb.ingress.kubernetes.io/healthcheck-path: '/k8s-health-check/'
    alb.ingress.kubernetes.io/certificate-arn: {{ certificate_arn }}
spec:
  rules:
  - http:
      paths:
      - pathType: Prefix
        path: "/k8s-health-check/"
        backend:
          service:
            name: healthcheck-service
            port:
              number: 80
"""
