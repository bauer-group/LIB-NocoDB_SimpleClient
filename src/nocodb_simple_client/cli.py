"""Command-line interface for NocoDB Simple Client.

MIT License

Copyright (c) BAUER GROUP

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import os
import sys
from pathlib import Path

try:
    import click
    from rich.console import Console
    from rich.json import JSON
    from rich.progress import Progress
    from rich.table import Table

    CLI_AVAILABLE = True
except ImportError:
    CLI_AVAILABLE = False
    click = None  # type: ignore[assignment]

if CLI_AVAILABLE:
    from .client import NocoDBClient
    from .config import load_config
    from .exceptions import NocoDBException
    from .table import NocoDBTable

    console = Console()

    @click.group()
    @click.option("--config", "-c", help="Configuration file path")
    @click.option("--base-url", "-u", help="NocoDB base URL")
    @click.option("--api-token", "-t", help="API token")
    @click.option("--debug", is_flag=True, help="Enable debug output")
    @click.pass_context
    def cli(
        ctx: click.Context,
        config: str | None,
        base_url: str | None,
        api_token: str | None,
        debug: bool,
    ) -> None:
        """NocoDB Simple Client CLI tool."""
        ctx.ensure_object(dict)

        # Load configuration
        if config:
            try:
                ctx.obj["config"] = load_config(Path(config), use_env=False)
            except Exception as e:
                console.print(f"[red]Error loading config: {e}[/red]")
                sys.exit(1)
        elif base_url and api_token:
            from .config import NocoDBConfig

            ctx.obj["config"] = NocoDBConfig(base_url=base_url, api_token=api_token)
        else:
            try:
                ctx.obj["config"] = load_config(use_env=True)
            except Exception as e:
                console.print(f"[red]Error loading config from environment: {e}[/red]")
                console.print(
                    "Please provide --config, or --base-url and --api-token, "
                    "or set environment variables"
                )
                sys.exit(1)

        if debug:
            ctx.obj["config"].debug = True
            ctx.obj["config"].log_level = "DEBUG"

        ctx.obj["config"].setup_logging()

    @cli.command()
    @click.pass_context
    def info(ctx: click.Context) -> None:
        """Display client and connection information."""
        config = ctx.obj["config"]

        table = Table(title="NocoDB Client Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Base URL", config.base_url)
        table.add_row(
            "API Token", "***" + config.api_token[-4:] if len(config.api_token) > 4 else "***"
        )
        table.add_row("Timeout", f"{config.timeout}s")
        table.add_row("Max Retries", str(config.max_retries))
        table.add_row("Verify SSL", "Yes" if config.verify_ssl else "No")
        table.add_row("Debug Mode", "Yes" if config.debug else "No")

        console.print(table)

    @cli.group()
    @click.pass_context
    def table(ctx: click.Context) -> None:
        """Table operations."""
        pass

    @table.command("list")
    @click.argument("table_id")
    @click.option("--limit", "-l", default=25, help="Number of records to retrieve")
    @click.option("--where", "-w", help="Filter conditions")
    @click.option("--sort", "-s", help="Sort criteria")
    @click.option("--fields", "-f", help="Comma-separated list of fields")
    @click.option(
        "--output",
        "-o",
        type=click.Choice(["table", "json", "csv"]),
        default="table",
        help="Output format",
    )
    @click.pass_context
    def list_records(
        ctx: click.Context,
        table_id: str,
        limit: int,
        where: str | None,
        sort: str | None,
        fields: str | None,
        output: str,
    ) -> None:
        """List records from a table."""
        config = ctx.obj["config"]

        try:
            with NocoDBClient(
                base_url=config.base_url, db_auth_token=config.api_token, timeout=config.timeout
            ) as client:
                table_obj = NocoDBTable(client, table_id)

                field_list = fields.split(",") if fields else None

                with Progress() as progress:
                    task = progress.add_task("Fetching records...", total=1)
                    records = table_obj.get_records(
                        limit=limit, where=where, sort=sort, fields=field_list
                    )
                    progress.update(task, completed=1)

                if not records:
                    console.print("[yellow]No records found[/yellow]")
                    return

                if output == "json":
                    console.print(JSON(json.dumps(records, indent=2)))
                elif output == "csv":
                    import csv
                    import io

                    output_buffer = io.StringIO()

                    if records:
                        fieldnames = records[0].keys()
                        writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(records)

                    console.print(output_buffer.getvalue())
                else:  # table format
                    if records:
                        table_display = Table(title=f"Records from {table_id}")

                        # Add columns
                        for field in records[0].keys():
                            table_display.add_column(field, overflow="fold")

                        # Add rows
                        for record in records:
                            row = [str(record.get(field, "")) for field in records[0].keys()]
                            table_display.add_row(*row)

                        console.print(table_display)
                        console.print(f"\n[green]Total records: {len(records)}[/green]")

        except NocoDBException as e:
            console.print(f"[red]NocoDB Error: {e}[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    @table.command("get")
    @click.argument("table_id")
    @click.argument("record_id")
    @click.option("--fields", "-f", help="Comma-separated list of fields")
    @click.option(
        "--output", "-o", type=click.Choice(["table", "json"]), default="json", help="Output format"
    )
    @click.pass_context
    def get_record(
        ctx: click.Context, table_id: str, record_id: str, fields: str | None, output: str
    ) -> None:
        """Get a specific record."""
        config = ctx.obj["config"]

        try:
            with NocoDBClient(
                base_url=config.base_url, db_auth_token=config.api_token, timeout=config.timeout
            ) as client:
                table_obj = NocoDBTable(client, table_id)

                field_list = fields.split(",") if fields else None
                record = table_obj.get_record(record_id, fields=field_list)

                if output == "json":
                    console.print(JSON(json.dumps(record, indent=2)))
                else:  # table format
                    table_display = Table(title=f"Record {record_id}")
                    table_display.add_column("Field", style="cyan")
                    table_display.add_column("Value", style="green")

                    for key, value in record.items():
                        table_display.add_row(key, str(value))

                    console.print(table_display)

        except NocoDBException as e:
            console.print(f"[red]NocoDB Error: {e}[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    @table.command("create")
    @click.argument("table_id")
    @click.option("--data", "-d", help="JSON data for the record")
    @click.option("--file", "-f", type=click.Path(exists=True), help="JSON file with record data")
    @click.pass_context
    def create_record(
        ctx: click.Context, table_id: str, data: str | None, file: str | None
    ) -> None:
        """Create a new record."""
        config = ctx.obj["config"]

        if not data and not file:
            console.print("[red]Either --data or --file must be provided[/red]")
            sys.exit(1)

        try:
            if file:
                with open(file) as f:
                    record_data = json.load(f)
            else:
                if data is None:
                    console.print("[red]Data cannot be None[/red]")
                    sys.exit(1)
                record_data = json.loads(data)

            with NocoDBClient(
                base_url=config.base_url, db_auth_token=config.api_token, timeout=config.timeout
            ) as client:
                table_obj = NocoDBTable(client, table_id)

                with Progress() as progress:
                    task = progress.add_task("Creating record...", total=1)
                    record_id = table_obj.insert_record(record_data)
                    progress.update(task, completed=1)

                console.print(f"[green]Record created with ID: {record_id}[/green]")

        except json.JSONDecodeError as e:
            console.print(f"[red]Invalid JSON: {e}[/red]")
            sys.exit(1)
        except NocoDBException as e:
            console.print(f"[red]NocoDB Error: {e}[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    @table.command("update")
    @click.argument("table_id")
    @click.argument("record_id")
    @click.option("--data", "-d", help="JSON data for the record")
    @click.option("--file", "-f", type=click.Path(exists=True), help="JSON file with record data")
    @click.pass_context
    def update_record(
        ctx: click.Context, table_id: str, record_id: str, data: str | None, file: str | None
    ) -> None:
        """Update an existing record."""
        config = ctx.obj["config"]

        if not data and not file:
            console.print("[red]Either --data or --file must be provided[/red]")
            sys.exit(1)

        try:
            if file:
                with open(file) as f:
                    record_data = json.load(f)
            else:
                if data is None:
                    console.print("[red]Data cannot be None[/red]")
                    sys.exit(1)
                record_data = json.loads(data)

            with NocoDBClient(
                base_url=config.base_url, db_auth_token=config.api_token, timeout=config.timeout
            ) as client:
                table_obj = NocoDBTable(client, table_id)

                with Progress() as progress:
                    task = progress.add_task("Updating record...", total=1)
                    updated_id = table_obj.update_record(record_data, record_id)
                    progress.update(task, completed=1)

                console.print(f"[green]Record updated: {updated_id}[/green]")

        except json.JSONDecodeError as e:
            console.print(f"[red]Invalid JSON: {e}[/red]")
            sys.exit(1)
        except NocoDBException as e:
            console.print(f"[red]NocoDB Error: {e}[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    @table.command("delete")
    @click.argument("table_id")
    @click.argument("record_id")
    @click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
    @click.pass_context
    def delete_record(ctx: click.Context, table_id: str, record_id: str, confirm: bool) -> None:
        """Delete a record."""
        config = ctx.obj["config"]

        if not confirm:
            if not click.confirm(f"Are you sure you want to delete record {record_id}?"):
                console.print("[yellow]Deletion cancelled[/yellow]")
                return

        try:
            with NocoDBClient(
                base_url=config.base_url, db_auth_token=config.api_token, timeout=config.timeout
            ) as client:
                table_obj = NocoDBTable(client, table_id)

                with Progress() as progress:
                    task = progress.add_task("Deleting record...", total=1)
                    deleted_id = table_obj.delete_record(record_id)
                    progress.update(task, completed=1)

                console.print(f"[green]Record deleted: {deleted_id}[/green]")

        except NocoDBException as e:
            console.print(f"[red]NocoDB Error: {e}[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    @table.command("count")
    @click.argument("table_id")
    @click.option("--where", "-w", help="Filter conditions")
    @click.pass_context
    def count_records(ctx: click.Context, table_id: str, where: str | None) -> None:
        """Count records in a table."""
        config = ctx.obj["config"]

        try:
            with NocoDBClient(
                base_url=config.base_url, db_auth_token=config.api_token, timeout=config.timeout
            ) as client:
                table_obj = NocoDBTable(client, table_id)

                with Progress() as progress:
                    task = progress.add_task("Counting records...", total=1)
                    count = table_obj.count_records(where=where)
                    progress.update(task, completed=1)

                filter_info = f" (with filter: {where})" if where else ""
                console.print(f"[green]Total records in {table_id}{filter_info}: {count}[/green]")

        except NocoDBException as e:
            console.print(f"[red]NocoDB Error: {e}[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    @cli.group()
    def files() -> None:
        """File operations."""
        pass

    @files.command("upload")
    @click.argument("table_id")
    @click.argument("record_id")
    @click.argument("field_name")
    @click.argument("file_path", type=click.Path(exists=True))
    @click.pass_context
    def upload_file(
        ctx: click.Context, table_id: str, record_id: str, field_name: str, file_path: str
    ) -> None:
        """Upload a file to a record."""
        config = ctx.obj["config"]

        try:
            with NocoDBClient(
                base_url=config.base_url, db_auth_token=config.api_token, timeout=config.timeout
            ) as client:
                table_obj = NocoDBTable(client, table_id)

                with Progress() as progress:
                    task = progress.add_task("Uploading file...", total=1)
                    table_obj.attach_file_to_record(record_id, field_name, file_path)
                    progress.update(task, completed=1)

                console.print(f"[green]File uploaded successfully to record {record_id}[/green]")

        except NocoDBException as e:
            console.print(f"[red]NocoDB Error: {e}[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    @files.command("download")
    @click.argument("table_id")
    @click.argument("record_id")
    @click.argument("field_name")
    @click.argument("output_path", type=click.Path())
    @click.pass_context
    def download_file(
        ctx: click.Context, table_id: str, record_id: str, field_name: str, output_path: str
    ) -> None:
        """Download a file from a record."""
        config = ctx.obj["config"]

        try:
            with NocoDBClient(
                base_url=config.base_url, db_auth_token=config.api_token, timeout=config.timeout
            ) as client:
                table_obj = NocoDBTable(client, table_id)

                with Progress() as progress:
                    task = progress.add_task("Downloading file...", total=1)
                    table_obj.download_file_from_record(record_id, field_name, output_path)
                    progress.update(task, completed=1)

                console.print(f"[green]File downloaded to: {output_path}[/green]")

        except NocoDBException as e:
            console.print(f"[red]NocoDB Error: {e}[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    def main() -> None:
        """Main CLI entry point."""
        try:
            cli()
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            sys.exit(130)
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            if os.getenv("NOCODB_DEBUG"):
                import traceback

                console.print(traceback.format_exc())
            sys.exit(1)

    if __name__ == "__main__":
        main()

else:

    def main() -> None:
        """Main CLI entry point when dependencies are not available."""
        print("CLI dependencies are not installed.")
        print("Please install with: pip install 'nocodb-simple-client[cli]'")
        sys.exit(1)
