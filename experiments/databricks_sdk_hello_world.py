"""List the clusters and SQL warehouses in the workspace."""

from databricks.sdk import WorkspaceClient

from ghwh.config import settings

client = WorkspaceClient(
    host=settings.databricks_workspace_host,
    token=settings.databricks_api_token.get_secret_value(),
)

print("=== Clusters ===")
for c in client.clusters.list():
    print(f"{c.cluster_name}  id={c.cluster_id}  state={c.state}")

print("\n=== SQL Warehouses ===")
for w in client.warehouses.list():
    print(f"{w.name}  id={w.id}  state={w.state}  http_path=/sql/1.0/warehouses/{w.id}")
