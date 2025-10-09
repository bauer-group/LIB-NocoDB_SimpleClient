"""
Meta API operations examples for NocoDB Simple Client.

This example demonstrates how to manage NocoDB structure including
workspaces, bases, tables, columns, and views programmatically.
"""

from nocodb_simple_client import NocoDBMetaClient
from nocodb_simple_client.columns import NocoDBColumns
from nocodb_simple_client.views import NocoDBViews

# Configuration
NOCODB_BASE_URL = "https://your-nocodb-instance.com"
API_TOKEN = "your-api-token-here"


def main():
    """Demonstrate Meta API operations."""

    # Initialize Meta API client
    meta_client = NocoDBMetaClient(base_url=NOCODB_BASE_URL, api_token=API_TOKEN)

    try:
        # ===================================================================
        # WORKSPACE OPERATIONS
        # ===================================================================
        print("=" * 60)
        print("WORKSPACE OPERATIONS")
        print("=" * 60)

        # List workspaces
        print("\n1. Listing workspaces...")
        workspaces = meta_client.list_workspaces()
        for workspace in workspaces:
            print(f"   • {workspace.get('title')} (ID: {workspace.get('id')})")

        # ===================================================================
        # BASE OPERATIONS
        # ===================================================================
        print("\n" + "=" * 60)
        print("BASE OPERATIONS")
        print("=" * 60)

        # List bases
        print("\n2. Listing bases...")
        bases = meta_client.list_bases()
        for base in bases:
            print(f"   • {base.get('title')} (ID: {base.get('id')})")

        if bases:
            base_id = bases[0]["id"]
            print(f"\n   Using base: {bases[0].get('title')} ({base_id})")

            # ===================================================================
            # TABLE OPERATIONS
            # ===================================================================
            print("\n" + "=" * 60)
            print("TABLE OPERATIONS")
            print("=" * 60)

            # List tables
            print("\n3. Listing tables...")
            tables = meta_client.list_tables(base_id)
            for table in tables:
                print(f"   • {table.get('title')} (ID: {table.get('id')})")

            # Create a new table
            print("\n4. Creating a new table...")
            table_data = {
                "title": "Demo Table",
                "table_name": "demo_table",
                "columns": [
                    {"title": "Title", "column_name": "title", "uidt": "SingleLineText"},
                    {
                        "title": "Status",
                        "column_name": "status",
                        "uidt": "SingleSelect",
                        "dtxp": [
                            {"title": "New", "color": "#3498db"},
                            {"title": "In Progress", "color": "#f39c12"},
                            {"title": "Done", "color": "#2ecc71"},
                        ],
                    },
                ],
            }

            new_table = meta_client.create_table(base_id, table_data)
            table_id = new_table["id"]
            print(f"   ✓ Created table: {new_table.get('title')} (ID: {table_id})")

            # Get table info
            print("\n5. Getting table information...")
            table_info = meta_client.get_table_info(table_id)
            print(f"   • Table: {table_info.get('title')}")
            print(f"   • Columns: {len(table_info.get('columns', []))}")

            # ===================================================================
            # COLUMN OPERATIONS
            # ===================================================================
            print("\n" + "=" * 60)
            print("COLUMN OPERATIONS")
            print("=" * 60)

            columns_manager = NocoDBColumns(meta_client)

            # Add various column types
            print("\n6. Adding columns...")

            # Text column
            text_col = columns_manager.create_text_column(
                table_id, title="Description", max_length=1000
            )
            print(f"   ✓ Added text column: {text_col.get('title')}")

            # Number column
            number_col = columns_manager.create_number_column(
                table_id, title="Priority", precision=3
            )
            print(f"   ✓ Added number column: {number_col.get('title')}")

            # Checkbox column
            checkbox_col = columns_manager.create_checkbox_column(
                table_id, title="Is Important", default_value=False
            )
            print(f"   ✓ Added checkbox column: {checkbox_col.get('title')}")

            # Date column
            date_col = columns_manager.create_date_column(
                table_id, title="Due Date", date_format="YYYY-MM-DD"
            )
            print(f"   ✓ Added date column: {date_col.get('title')}")

            # List all columns
            print("\n7. Listing all columns...")
            columns = columns_manager.get_columns(table_id)
            for col in columns:
                print(f"   • {col.get('title')} ({col.get('uidt')})")

            # ===================================================================
            # VIEW OPERATIONS
            # ===================================================================
            print("\n" + "=" * 60)
            print("VIEW OPERATIONS")
            print("=" * 60)

            views_manager = NocoDBViews(meta_client)

            # Create views
            print("\n8. Creating views...")

            # Grid view
            grid_view = views_manager.create_view(table_id, title="All Items", view_type="grid")
            print(f"   ✓ Created grid view: {grid_view.get('title')}")

            # Gallery view
            gallery_view = views_manager.create_view(
                table_id, title="Gallery View", view_type="gallery"
            )
            print(f"   ✓ Created gallery view: {gallery_view.get('title')}")

            # Form view
            form_view = views_manager.create_view(table_id, title="Submit Form", view_type="form")
            print(f"   ✓ Created form view: {form_view.get('title')}")

            # List all views
            print("\n9. Listing all views...")
            views = views_manager.get_views(table_id)
            for view in views:
                print(f"   • {view.get('title')} ({view.get('type')})")

            # Add filter to a view (if we have the column IDs)
            if columns:
                status_column = next((c for c in columns if c.get("title") == "Status"), None)
                if status_column and views:
                    print("\n10. Adding filter to grid view...")
                    views_manager.create_view_filter(
                        table_id,
                        grid_view["id"],
                        column_id=status_column["id"],
                        comparison_op="eq",
                        value="Done",
                        logical_op="and",
                    )
                    print("   ✓ Added filter to view")

            # ===================================================================
            # CLEANUP
            # ===================================================================
            print("\n" + "=" * 60)
            print("CLEANUP")
            print("=" * 60)

            # Delete the demo table
            print("\n11. Cleaning up (deleting demo table)...")
            meta_client.delete_table(table_id)
            print("   ✓ Deleted demo table")

        else:
            print("\n   No bases found. Please create a base in NocoDB first.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        meta_client.close()
        print("\n✓ Meta client session closed")


if __name__ == "__main__":
    main()
