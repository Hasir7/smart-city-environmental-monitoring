# Terraform Azure Infrastructure

This configuration provisions the capstone environment: Resource Group, Free-tier AKS cluster, Basic ACR, burstable Azure Database for PostgreSQL, Azure Key Vault, CSI access, and optional Azure Monitor resources.

Run the exact commands from the repository root in the main `README.md`. Password variables are required and intentionally not committed.

Useful outputs:

```bash
terraform -chdir=infra/terraform output
```

Do not commit `.terraform`, state files, plan files, or real secret values.
