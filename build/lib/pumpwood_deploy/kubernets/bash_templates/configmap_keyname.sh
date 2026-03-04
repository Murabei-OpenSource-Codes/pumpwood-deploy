SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
kubectl delete configmap {name}
kubectl create configmap {name}\
    --from-file="{keyname}=$SCRIPTPATH/{file_name}"\
    --namespace={namespace}
