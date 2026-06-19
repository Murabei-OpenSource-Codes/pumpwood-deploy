SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
kubectl delete secret --ignore-not-found --namespace={{namespace}} {{name}};
kubectl create secret generic {{name}} --namespace={{namespace}}{%- for path in paths %} --from-file='{{path}}'{%- endfor %}
