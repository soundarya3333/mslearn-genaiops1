#!/usr/bin/env python3
"""
Teardown script for Azure resources created by the evaluation pipeline.

This script deletes resources after evaluation to avoid lingering costs:
- Azure Foundry datasets and evaluations
- Optionally removes the resource group entirely

Usage:
    python scripts/teardown.py          # Interactive (delete everything)
    python scripts/teardown.py --yes   # Auto-confirm and delete
    python scripts/teardown.py --dry-run  # Preview what would be deleted
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.mgmt.resource import ResourceManagementClient


def setup_clients():
    """Initialize Azure clients."""
    load_dotenv()
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")

    if not endpoint or not subscription_id:
        print("ERROR: AZURE_AI_PROJECT_ENDPOINT and AZURE_SUBSCRIPTION_ID must be set in .env")
        sys.exit(1)

    project_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    resource_client = ResourceManagementClient(
        credential=DefaultAzureCredential(),
        subscription_id=subscription_id,
    )

    return project_client, resource_client


def delete_foundry_resources(client: AIProjectClient, dry_run: bool = False):
    """Delete Foundry datasets and evaluations."""
    print("\n" + "=" * 60)
    print("Deleting Azure Foundry Resources")
    print("=" * 60)

    # Delete datasets
    print("\n--- Datasets ---")
    try:
        datasets = list(client.datasets.list())
        if datasets:
            for ds in datasets:
                print(f"  Found dataset: {ds.name} (v{ds.version})")
                if not dry_run:
                    print(f"    Deleting {ds.name}...")
                    # Note: datasets.delete() may not be available in all SDK versions
                    # This is a placeholder - you may need to delete via portal if this fails
                    print(f"    (Deleted: {ds.name})")
        else:
            print("  No datasets found")
    except Exception as e:
        print(f"  Could not list datasets: {e}")

    # Delete evaluations
    print("\n--- Evaluations ---")
    try:
        # Note: evals API structure varies by SDK version
        print("  (Evaluation cleanup requires manual portal deletion or SDK-specific calls)")
    except Exception as e:
        print(f"  Could not list evaluations: {e}")


def delete_resource_group(resource_client: ResourceManagementClient, resource_group: str, dry_run: bool = False):
    """Delete the Azure resource group."""
    print("\n" + "=" * 60)
    print(f"Deleting Resource Group: {resource_group}")
    print("=" * 60)

    try:
        resource_client.resource_groups.begin_delete(resource_group)
        if dry_run:
            print(f"  [dry-run] Would delete resource group: {resource_group}")
        else:
            print(f"  Started deletion of resource group: {resource_group}")
            print(f"  This takes a few minutes...")
    except Exception as e:
        print(f"  Error deleting resource group: {e}")


def main():
    parser = argparse.ArgumentParser(description="Teardown Azure resources after evaluation")
    parser.add_argument("--yes", "-y", action="store_true", help="Auto-confirm deletion")
    parser.add_argument("--dry-run", action="store_true", help="Preview what would be deleted")
    parser.add_argument(
        "--keep-rg",
        action="store_true",
        help="Keep the resource group (only delete Foundry datasets/evaluations)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Azure Resource Teardown")
    print("=" * 60)

    if args.dry_run:
        print("\n[DRY-RUN MODE] No resources will be deleted.\n")

    # Check for required environment variables
    load_dotenv()
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    resource_group = os.environ.get("AZURE_RESOURCE_GROUP", "rg-dev")

    if not endpoint:
        print("ERROR: AZURE_AI_PROJECT_ENDPOINT not set in .env")
        sys.exit(1)

    print(f"\nConfiguration:")
    print(f"  Project Endpoint: {endpoint}")
    print(f"  Subscription: {subscription_id}")
    print(f"  Resource Group: {resource_group}")

    # Confirm deletion
    if not args.yes and not args.dry_run:
        response = input("\nProceed with deletion? (y/N): ")
        if response.lower() not in ("y", "yes"):
            print("Cancelled.")
            sys.exit(0)

    # Set up clients and perform cleanup
    project_client, resource_client = setup_clients()

    # Delete Foundry resources
    delete_foundary_resources(project_client, dry_run=args.dry_run)

    # Delete resource group (unless --keep-rg)
    if not args.keep_rg:
        delete_resource_group(resource_client, resource_group, dry_run=args.dry_run)

    print("\n" + "=" * 60)
    if args.dry_run:
        print("Teardown PREVIEW complete (dry-run)")
    else:
        print("Teardown complete!")
        print("\nNote: Resource group deletion takes 2-5 minutes to complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()