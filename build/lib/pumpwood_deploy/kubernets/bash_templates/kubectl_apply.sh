SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
kubectl apply -f $SCRIPTPATH/{file} --namespace={namespace}
