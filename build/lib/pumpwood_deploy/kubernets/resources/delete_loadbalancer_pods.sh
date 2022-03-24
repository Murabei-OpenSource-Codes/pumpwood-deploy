#!/bin/sh
kubectl delete pods -l type=haproxy-load-balancer
kubectl delete pods -l type=nginx-ssl
