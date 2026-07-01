SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
kubectl apply --namespace={namespace} -f "$SCRIPTPATH/{file}"
