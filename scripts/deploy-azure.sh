#!/usr/bin/env bash
set -euo pipefail

command -v az >/dev/null || { echo "Azure CLI (az) is required."; exit 1; }
command -v terraform >/dev/null || { echo "Terraform is required."; exit 1; }
command -v kubectl >/dev/null || { echo "kubectl is required."; exit 1; }
command -v docker >/dev/null || { echo "Docker is required."; exit 1; }

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
terraform_dir="$project_root/infra/terraform"
image_tag="${1:-capstone}"

resource_group="$(terraform -chdir="$terraform_dir" output -raw resource_group_name)"
acr_name="$(terraform -chdir="$terraform_dir" output -raw acr_name)"
acr_login_server="$(terraform -chdir="$terraform_dir" output -raw acr_login_server)"
aks_name="$(terraform -chdir="$terraform_dir" output -raw aks_cluster_name)"
key_vault_name="$(terraform -chdir="$terraform_dir" output -raw key_vault_name)"
key_vault_identity_client_id="$(terraform -chdir="$terraform_dir" output -raw key_vault_identity_client_id)"
tenant_id="$(terraform -chdir="$terraform_dir" output -raw tenant_id)"

az acr login --name "$acr_name"

for service in ingestion processor api frontend; do
  if [ "$service" = "frontend" ]; then
    service_dir="$project_root/frontend"
  else
    service_dir="$project_root/services/$service"
  fi
  image="$acr_login_server/$service:$image_tag"
  for attempt in 1 2 3; do
    if docker buildx build --platform linux/amd64 -t "$image" -f "$service_dir/Dockerfile" --push "$service_dir"; then
      break
    fi
    if [ "$attempt" = "3" ]; then
      echo "Failed to build and push $image after 3 attempts."
      exit 1
    fi
    echo "Build or push failed for $image. Retrying..."
    sleep 10
  done
done

az aks get-credentials --resource-group "$resource_group" --name "$aks_name" --overwrite-existing

render_dir="$(mktemp -d)"
trap 'rm -rf "$render_dir"' EXIT
cp "$project_root"/k8s/*.yaml "$render_dir/"

sed \
  -e "s|ACR_LOGIN_SERVER|$acr_login_server|g" \
  -e "s|IMAGE_TAG|$image_tag|g" \
  "$render_dir/deployments.yaml" > "$render_dir/deployments.rendered.yaml"
mv "$render_dir/deployments.rendered.yaml" "$render_dir/deployments.yaml"

sed \
  -e "s|KEY_VAULT_NAME|$key_vault_name|g" \
  -e "s|KEY_VAULT_IDENTITY_CLIENT_ID|$key_vault_identity_client_id|g" \
  -e "s|AZURE_TENANT_ID|$tenant_id|g" \
  "$render_dir/secret.yaml" > "$render_dir/secret.rendered.yaml"
mv "$render_dir/secret.rendered.yaml" "$render_dir/secret.yaml"

kubectl apply -f "$render_dir/namespace.yaml"
kubectl apply -f "$render_dir/configmap.yaml"
kubectl apply -f "$render_dir/secret.yaml"
kubectl apply -f "$render_dir/services.yaml"
kubectl apply -f "$render_dir/deployments.yaml"
kubectl apply -f "$render_dir/hpa.yaml"

for deployment in secrets-sync rabbitmq ingestion processor api frontend; do
  kubectl rollout status "deployment/$deployment" -n smart-city --timeout=8m
done

echo "Waiting for the Azure public IP..."
for _ in $(seq 1 60); do
  public_ip="$(kubectl get service frontend -n smart-city -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)"
  if [ -n "$public_ip" ]; then
    echo "Public dashboard URL: http://$public_ip"
    echo "API health URL: http://$public_ip/api/health"
    echo "Ingestion health URL: http://$public_ip/ingestion/health"
    exit 0
  fi
  sleep 10
done

echo "The deployment succeeded, but Azure is still assigning the public IP."
echo "Run: kubectl get service frontend -n smart-city"
