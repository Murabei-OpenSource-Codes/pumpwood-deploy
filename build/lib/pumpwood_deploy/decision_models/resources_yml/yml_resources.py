decision_model_yml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: decision-model--{decision_model_name}
spec:
  replicas: 1
  selector:
    matchLabels:
      type: decision_model
      model_type: {decision_model_name}
      role: worker
  template:
    metadata:
      labels:
        type: decision_model
        model_type: {decision_model_name}
        role: worker
    spec:
      imagePullSecrets:
        - name: dockercfg
      containers:
      - name: decision-model--{decision_model_name}
        image: {repository}/decision-model--{decision_model_name}:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
        env:
        # RABBITMQ QUEUE
        - name: RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rabbitmq-main-secrets
              key: password

        # Microsservice
        - name: MICROSERVICE_NAME
          value: 'decision-model--{decision_model_name}'
        - name: MICROSERVICE_PASSWORD
          valueFrom:
              secretKeyRef:
                name: pumpwood-decision
                key: microservice_password
"""
