import json
import os

from src.api.main import app

if __name__ == "__main__":
    # Generate and write OpenAPI schema to interfaces/openapi.json
    openapi_schema = app.openapi()
    output_dir = "interfaces"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "openapi.json")
    with open(output_path, "w") as f:
        json.dump(openapi_schema, f, indent=2)
    print(f"OpenAPI schema written to {output_path}")
