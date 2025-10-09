"""Pagination handler for efficient data retrieval from NocoDB.

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

import math
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .table import NocoDBTable


class PaginatedResult:
    """Represents a paginated result set with metadata.

    Provides information about the current page, total records, and
    methods for navigation between pages.
    """

    def __init__(
        self,
        records: list[dict[str, Any]],
        current_page: int,
        page_size: int,
        total_records: int | None = None,
        has_more: bool = False,
    ) -> None:
        """Initialize a paginated result.

        Args:
            records: List of records in this page
            current_page: Current page number (1-based)
            page_size: Number of records per page
            total_records: Total number of records (if known)
            has_more: Whether there are more records available
        """
        self.records = records
        self.current_page = current_page
        self.page_size = page_size
        self.total_records = total_records
        self.has_more = has_more
        self._actual_count = len(records)

    @property
    def total_pages(self) -> int | None:
        """Get total number of pages (if total_records is known)."""
        if self.total_records is None:
            return None
        return math.ceil(self.total_records / self.page_size)

    @property
    def is_first_page(self) -> bool:
        """Check if this is the first page."""
        return self.current_page == 1

    @property
    def is_last_page(self) -> bool:
        """Check if this is the last page."""
        if self.total_pages:
            return self.current_page >= self.total_pages
        return not self.has_more

    @property
    def has_previous(self) -> bool:
        """Check if there is a previous page."""
        return self.current_page > 1

    @property
    def has_next(self) -> bool:
        """Check if there is a next page."""
        if self.total_pages:
            return self.current_page < self.total_pages
        return self.has_more

    @property
    def start_record(self) -> int:
        """Get the number of the first record in this page."""
        return (self.current_page - 1) * self.page_size + 1

    @property
    def end_record(self) -> int:
        """Get the number of the last record in this page."""
        return (self.current_page - 1) * self.page_size + self._actual_count

    def __len__(self) -> int:
        """Get the number of records in this page."""
        return len(self.records)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """Iterate over records in this page."""
        return iter(self.records)

    def __getitem__(self, index: int) -> dict[str, Any]:
        """Get a record by index."""
        record = self.records[index]
        return record if isinstance(record, dict) else {}

    def __bool__(self) -> bool:
        """Check if this page has any records."""
        return len(self.records) > 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "records": self.records,
            "pagination": {
                "current_page": self.current_page,
                "page_size": self.page_size,
                "total_records": self.total_records,
                "total_pages": self.total_pages,
                "has_more": self.has_more,
                "has_previous": self.has_previous,
                "has_next": self.has_next,
                "start_record": self.start_record,
                "end_record": self.end_record,
                "is_first_page": self.is_first_page,
                "is_last_page": self.is_last_page,
            },
        }


class PaginationHandler:
    """Handler for paginated data retrieval from NocoDB tables.

    Provides methods for efficient pagination with automatic page navigation,
    streaming, and batch processing capabilities.
    """

    def __init__(self, table: "NocoDBTable") -> None:
        """Initialize pagination handler for a table.

        Args:
            table: NocoDBTable instance to paginate
        """
        self.table = table
        self._default_page_size = 25

    def paginate(
        self,
        page: int = 1,
        page_size: int | None = None,
        sort: str | None = None,
        where: str | None = None,
        fields: list[str] | None = None,
        include_count: bool = False,
    ) -> PaginatedResult:
        """Get a specific page of records.

        Args:
            page: Page number to retrieve (1-based)
            page_size: Number of records per page
            sort: Sort criteria
            where: Filter condition
            fields: List of fields to retrieve
            include_count: Whether to include total count (slower but provides more info)

        Returns:
            PaginatedResult containing the records and pagination metadata

        Raises:
            ValueError: If page number is invalid
            NocoDBException: For API errors
        """
        if page < 1:
            raise ValueError("Page number must be 1 or greater")

        page_size = page_size or self._default_page_size
        if page_size < 1:
            raise ValueError("Page size must be 1 or greater")

        # Fetch one extra record to check if there are more pages
        fetch_limit = page_size + 1

        # Get records
        records = self.table.get_records(sort=sort, where=where, fields=fields, limit=fetch_limit)

        # Check if we have more records than requested
        has_more = len(records) > page_size
        if has_more:
            records = records[:page_size]  # Remove the extra record

        # Get total count if requested
        total_records = None
        if include_count:
            total_records = self.table.count_records(where=where)

        return PaginatedResult(
            records=records,
            current_page=page,
            page_size=page_size,
            total_records=total_records,
            has_more=has_more,
        )

    def get_first_page(
        self,
        page_size: int | None = None,
        sort: str | None = None,
        where: str | None = None,
        fields: list[str] | None = None,
    ) -> PaginatedResult:
        """Get the first page of records.

        Args:
            page_size: Number of records per page
            sort: Sort criteria
            where: Filter condition
            fields: List of fields to retrieve

        Returns:
            PaginatedResult for the first page
        """
        return self.paginate(page=1, page_size=page_size, sort=sort, where=where, fields=fields)

    def get_last_page(
        self,
        page_size: int | None = None,
        sort: str | None = None,
        where: str | None = None,
        fields: list[str] | None = None,
    ) -> PaginatedResult:
        """Get the last page of records.

        Args:
            page_size: Number of records per page
            sort: Sort criteria
            where: Filter condition
            fields: List of fields to retrieve

        Returns:
            PaginatedResult for the last page
        """
        page_size = page_size or self._default_page_size

        # Get total count to calculate last page
        total_records = self.table.count_records(where=where)
        if total_records == 0:
            return PaginatedResult([], 1, page_size, total_records, False)

        last_page = math.ceil(total_records / page_size)

        return self.paginate(
            page=last_page,
            page_size=page_size,
            sort=sort,
            where=where,
            fields=fields,
            include_count=True,
        )

    def iterate_pages(
        self,
        page_size: int | None = None,
        sort: str | None = None,
        where: str | None = None,
        fields: list[str] | None = None,
        max_pages: int | None = None,
    ) -> Iterator[PaginatedResult]:
        """Iterate through all pages of records.

        Args:
            page_size: Number of records per page
            sort: Sort criteria
            where: Filter condition
            fields: List of fields to retrieve
            max_pages: Maximum number of pages to iterate (None for all)

        Yields:
            PaginatedResult for each page

        Example:
            >>> for page in pagination_handler.iterate_pages(page_size=100):
            ...     print(f"Page {page.current_page}: {len(page.records)} records")
            ...     for record in page.records:
            ...         process_record(record)
        """
        page_size = page_size or self._default_page_size
        current_page = 1

        while True:
            if max_pages and current_page > max_pages:
                break

            page_result = self.paginate(
                page=current_page, page_size=page_size, sort=sort, where=where, fields=fields
            )

            if not page_result.records:
                break

            yield page_result

            if not page_result.has_more:
                break

            current_page += 1

    def iterate_records(
        self,
        page_size: int | None = None,
        sort: str | None = None,
        where: str | None = None,
        fields: list[str] | None = None,
        max_records: int | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Iterate through all records across all pages.

        Args:
            page_size: Number of records per page
            sort: Sort criteria
            where: Filter condition
            fields: List of fields to retrieve
            max_records: Maximum number of records to iterate (None for all)

        Yields:
            Individual record dictionaries

        Example:
            >>> for record in pagination_handler.iterate_records(page_size=1000):
            ...     process_record(record)
        """
        page_size = page_size or self._default_page_size
        records_yielded = 0

        for page in self.iterate_pages(page_size, sort, where, fields):
            for record in page.records:
                if max_records and records_yielded >= max_records:
                    return

                yield record
                records_yielded += 1

    def get_all_records(
        self,
        page_size: int | None = None,
        sort: str | None = None,
        where: str | None = None,
        fields: list[str] | None = None,
        max_records: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get all records across all pages as a single list.

        Args:
            page_size: Number of records per page for fetching
            sort: Sort criteria
            where: Filter condition
            fields: List of fields to retrieve
            max_records: Maximum number of records to retrieve

        Returns:
            List of all records

        Warning:
            This method loads all records into memory. Use iterate_records()
            for large datasets to avoid memory issues.
        """
        records = []
        for record in self.iterate_records(page_size, sort, where, fields, max_records):
            records.append(record)

        return records

    def get_page_info(
        self, where: str | None = None, page_size: int | None = None
    ) -> dict[str, Any]:
        """Get pagination information without fetching records.

        Args:
            where: Filter condition
            page_size: Number of records per page

        Returns:
            Dictionary with pagination metadata
        """
        page_size = page_size or self._default_page_size
        total_records = self.table.count_records(where=where)
        total_pages = math.ceil(total_records / page_size) if total_records > 0 else 0

        return {
            "total_records": total_records,
            "total_pages": total_pages,
            "page_size": page_size,
            "has_records": total_records > 0,
        }

    def batch_process(
        self,
        processor_func: Callable[..., Any],
        page_size: int | None = None,
        sort: str | None = None,
        where: str | None = None,
        fields: list[str] | None = None,
        max_records: int | None = None,
        progress_callback: Callable[..., Any] | None = None,
    ) -> list[Any]:
        """Process records in batches using a processor function.

        Args:
            processor_func: Function that takes a list of records and returns results
            page_size: Number of records per batch
            sort: Sort criteria
            where: Filter condition
            fields: List of fields to retrieve
            max_records: Maximum number of records to process
            progress_callback: Optional callback function for progress updates

        Returns:
            List of results from processor function

        Example:
            >>> def process_batch(records):
            ...     # Process batch of records
            ...     return [r['id'] for r in records]
            >>>
            >>> def progress(page_num, records_processed):
            ...     print(f"Processed page {page_num}, {records_processed} records total")
            >>>
            >>> results = pagination_handler.batch_process(
            ...     process_batch,
            ...     page_size=1000,
            ...     progress_callback=progress
            ... )
        """
        page_size = page_size or self._default_page_size
        results = []
        total_processed = 0

        for page_num, page in enumerate(self.iterate_pages(page_size, sort, where, fields), 1):
            if max_records and total_processed >= max_records:
                break

            # Limit records if we're approaching max_records
            records_to_process = page.records
            if max_records and total_processed + len(records_to_process) > max_records:
                remaining = max_records - total_processed
                records_to_process = records_to_process[:remaining]

            # Process the batch
            batch_result = processor_func(records_to_process)
            if batch_result is not None:
                results.append(batch_result)

            total_processed += len(records_to_process)

            # Call progress callback if provided
            if progress_callback:
                progress_callback(page_num, total_processed)

        return results

    def find_record_page(
        self,
        record_id: int | str,
        page_size: int | None = None,
        sort: str | None = None,
        where: str | None = None,
        fields: list[str] | None = None,
    ) -> tuple[int, PaginatedResult] | None:
        """Find which page contains a specific record.

        Args:
            record_id: ID of the record to find
            page_size: Number of records per page
            sort: Sort criteria
            where: Filter condition
            fields: List of fields to retrieve

        Returns:
            Tuple of (page_number, PaginatedResult) if found, None otherwise
        """
        page_size = page_size or self._default_page_size

        for page_result in self.iterate_pages(page_size, sort, where, fields):
            for record in page_result.records:
                if str(record.get("Id", "")) == str(record_id):
                    return page_result.current_page, page_result

        return None
