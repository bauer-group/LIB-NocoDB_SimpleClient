"""
Link/Relation management examples for NocoDB Simple Client.

This example demonstrates how to manage relationships between
records in different tables.
"""

from nocodb_simple_client import NocoDBClient
from nocodb_simple_client.links import NocoDBLinks

# Configuration
NOCODB_BASE_URL = "https://your-nocodb-instance.com"
API_TOKEN = "your-api-token-here"

# Example: Projects table linking to Tasks table
PROJECTS_TABLE_ID = "your-projects-table-id"
TASKS_TABLE_ID = "your-tasks-table-id"
LINK_FIELD_ID = "your-link-field-id"  # The LinkToAnotherRecord column ID


def main():
    """Demonstrate link/relation management."""

    client = NocoDBClient(base_url=NOCODB_BASE_URL, db_auth_token=API_TOKEN)
    links_manager = NocoDBLinks(client)

    try:
        print("=" * 60)
        print("LINK/RELATION MANAGEMENT EXAMPLES")
        print("=" * 60)

        # Note: For this example to work, you need:
        # 1. Two tables (e.g., Projects and Tasks)
        # 2. A LinkToAnotherRecord field in one of them
        # 3. Some existing records

        # ===================================================================
        # GET LINKED RECORDS
        # ===================================================================
        print("\n1. Getting linked records...")
        project_id = 1  # Replace with actual project ID

        linked_tasks = links_manager.get_linked_records(
            PROJECTS_TABLE_ID,
            record_id=project_id,
            link_field_id=LINK_FIELD_ID,
            fields=["Id", "Title", "Status", "Priority"],
            sort="-Priority",
            limit=25,
        )

        print(f"   Project {project_id} has {len(linked_tasks)} linked tasks:")
        for task in linked_tasks:
            print(f"   • Task {task.get('Id')}: {task.get('Title')} ({task.get('Status')})")

        # ===================================================================
        # COUNT LINKED RECORDS
        # ===================================================================
        print("\n2. Counting linked records...")
        total_tasks = links_manager.count_linked_records(
            PROJECTS_TABLE_ID, record_id=project_id, link_field_id=LINK_FIELD_ID
        )
        print(f"   Total tasks: {total_tasks}")

        # Count with filter
        completed_tasks = links_manager.count_linked_records(
            PROJECTS_TABLE_ID,
            record_id=project_id,
            link_field_id=LINK_FIELD_ID,
            where="(Status,eq,Completed)",
        )
        print(f"   Completed tasks: {completed_tasks}")

        # ===================================================================
        # LINK RECORDS
        # ===================================================================
        print("\n3. Linking records...")
        # Link tasks 10, 11, 12 to project 1
        task_ids_to_link = [10, 11, 12]

        links_manager.link_records(
            PROJECTS_TABLE_ID,
            record_id=project_id,
            link_field_id=LINK_FIELD_ID,
            linked_record_ids=task_ids_to_link,
        )
        print(f"   ✓ Linked {len(task_ids_to_link)} tasks to project {project_id}")

        # ===================================================================
        # UNLINK SPECIFIC RECORDS
        # ===================================================================
        print("\n4. Unlinking specific records...")
        task_ids_to_unlink = [10]

        links_manager.unlink_records(
            PROJECTS_TABLE_ID,
            record_id=project_id,
            link_field_id=LINK_FIELD_ID,
            linked_record_ids=task_ids_to_unlink,
        )
        print(f"   ✓ Unlinked {len(task_ids_to_unlink)} task(s) from project {project_id}")

        # ===================================================================
        # REPLACE ALL LINKS
        # ===================================================================
        print("\n5. Replacing all linked records...")
        new_task_ids = [15, 16, 17, 18]

        links_manager.replace_links(
            PROJECTS_TABLE_ID,
            record_id=project_id,
            link_field_id=LINK_FIELD_ID,
            new_linked_record_ids=new_task_ids,
        )
        print(f"   ✓ Replaced all links with {len(new_task_ids)} new tasks")

        # Verify
        new_count = links_manager.count_linked_records(
            PROJECTS_TABLE_ID, record_id=project_id, link_field_id=LINK_FIELD_ID
        )
        print(f"   New link count: {new_count}")

        # ===================================================================
        # UNLINK ALL RECORDS
        # ===================================================================
        print("\n6. Unlinking all records...")
        links_manager.unlink_all_records(
            PROJECTS_TABLE_ID, record_id=project_id, link_field_id=LINK_FIELD_ID
        )
        print(f"   ✓ Unlinked all tasks from project {project_id}")

        # ===================================================================
        # BULK LINK OPERATIONS
        # ===================================================================
        print("\n7. Performing bulk link operations...")
        operations = [
            {
                "table_id": PROJECTS_TABLE_ID,
                "record_id": 1,
                "link_field_id": LINK_FIELD_ID,
                "linked_record_ids": [20, 21],
                "action": "link",
            },
            {
                "table_id": PROJECTS_TABLE_ID,
                "record_id": 2,
                "link_field_id": LINK_FIELD_ID,
                "linked_record_ids": [22, 23],
                "action": "link",
            },
            {
                "table_id": PROJECTS_TABLE_ID,
                "record_id": 3,
                "link_field_id": LINK_FIELD_ID,
                "linked_record_ids": [24],
                "action": "unlink",
            },
        ]

        results = links_manager.bulk_link_records(operations)
        successful = sum(results)
        print(f"   ✓ Bulk operations: {successful}/{len(results)} successful")

        # ===================================================================
        # PRACTICAL EXAMPLES
        # ===================================================================
        print("\n" + "=" * 60)
        print("PRACTICAL USE CASES")
        print("=" * 60)

        print("\n8. Practical scenarios...")

        # Scenario 1: Assign multiple tasks to a project
        print("\n   Scenario 1: Assigning tasks to a new project")
        new_project_id = 100  # Hypothetical new project
        task_ids_for_project = [30, 31, 32, 33, 34]

        links_manager.link_records(
            PROJECTS_TABLE_ID,
            record_id=new_project_id,
            link_field_id=LINK_FIELD_ID,
            linked_record_ids=task_ids_for_project,
        )
        print(f"   ✓ Assigned {len(task_ids_for_project)} tasks to project {new_project_id}")

        # Scenario 2: Transfer tasks from one project to another
        print("\n   Scenario 2: Transferring tasks between projects")
        source_project = 100
        target_project = 101

        # Get tasks from source project
        tasks_to_transfer = links_manager.get_linked_records(
            PROJECTS_TABLE_ID, record_id=source_project, link_field_id=LINK_FIELD_ID, fields=["Id"]
        )
        task_ids = [task["Id"] for task in tasks_to_transfer]

        # Unlink from source
        links_manager.unlink_records(
            PROJECTS_TABLE_ID,
            record_id=source_project,
            link_field_id=LINK_FIELD_ID,
            linked_record_ids=task_ids,
        )

        # Link to target
        links_manager.link_records(
            PROJECTS_TABLE_ID,
            record_id=target_project,
            link_field_id=LINK_FIELD_ID,
            linked_record_ids=task_ids,
        )
        print(
            f"   ✓ Transferred {len(task_ids)} tasks from project {source_project} to {target_project}"
        )

        # Scenario 3: Finding all linked records with specific criteria
        print("\n   Scenario 3: Finding high-priority tasks in a project")
        high_priority_tasks = links_manager.get_linked_records(
            PROJECTS_TABLE_ID,
            record_id=project_id,
            link_field_id=LINK_FIELD_ID,
            fields=["Id", "Title", "Priority"],
            where="(Priority,eq,High)",
            sort="-CreatedAt",
        )
        print(f"   Found {len(high_priority_tasks)} high-priority tasks:")
        for task in high_priority_tasks:
            print(f"   • {task.get('Title')}")

        # Scenario 4: Link validation before operations
        print("\n   Scenario 4: Validating links before adding")
        max_tasks_per_project = 50

        current_count = links_manager.count_linked_records(
            PROJECTS_TABLE_ID, record_id=project_id, link_field_id=LINK_FIELD_ID
        )

        new_tasks_to_add = [40, 41, 42]
        if current_count + len(new_tasks_to_add) <= max_tasks_per_project:
            links_manager.link_records(
                PROJECTS_TABLE_ID,
                record_id=project_id,
                link_field_id=LINK_FIELD_ID,
                linked_record_ids=new_tasks_to_add,
            )
            print(
                f"   ✓ Added {len(new_tasks_to_add)} tasks (total: {current_count + len(new_tasks_to_add)})"
            )
        else:
            print(f"   ⚠ Cannot add tasks: would exceed maximum of {max_tasks_per_project}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        client.close()
        print("\n✓ Client session closed")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("NOTE: This example requires proper setup of linked tables")
    print("=" * 60)
    print("\nBefore running this example, you need to:")
    print("1. Create two tables (e.g., Projects and Tasks)")
    print("2. Add a LinkToAnotherRecord field to link them")
    print("3. Create some test records")
    print("4. Update the configuration constants at the top of this file")
    print("\n" + "=" * 60)

    response = input("\nHave you completed the setup? (y/n): ")
    if response.lower() == "y":
        main()
    else:
        print("\nPlease complete the setup first, then run this example again.")
