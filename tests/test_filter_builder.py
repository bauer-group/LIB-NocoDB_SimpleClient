"""Tests for FilterBuilder and SortBuilder classes based on actual implementation."""

from datetime import date, datetime

from nocodb_simple_client.filter_builder import FilterBuilder, SortBuilder


class TestFilterBuilder:
    """Test FilterBuilder functionality."""

    def test_filter_builder_initialization(self):
        """Test FilterBuilder initialization."""
        fb = FilterBuilder()
        assert fb._conditions == []

    def test_simple_where_condition(self):
        """Test basic WHERE condition."""
        fb = FilterBuilder()
        result = fb.where("Status", "eq", "Active")

        assert result is fb  # Method chaining
        filter_str = fb.build()
        assert filter_str == "(Status,eq,Active)"

    def test_multiple_and_conditions(self):
        """Test multiple AND conditions."""
        fb = FilterBuilder()
        filter_str = (fb
            .where("Status", "eq", "Active")
            .and_("Age", "gt", 21)
            .build())

        assert filter_str == "(Status,eq,Active)~and(Age,gt,21)"

    def test_multiple_or_conditions(self):
        """Test multiple OR conditions."""
        fb = FilterBuilder()
        filter_str = (fb
            .where("Status", "eq", "Active")
            .or_("Status", "eq", "Pending")
            .build())

        assert filter_str == "(Status,eq,Active)~or(Status,eq,Pending)"

    def test_mixed_and_or_conditions(self):
        """Test mixed AND/OR conditions."""
        fb = FilterBuilder()
        filter_str = (fb
            .where("Status", "eq", "Active")
            .and_("Age", "gt", 21)
            .or_("Role", "eq", "Admin")
            .build())

        assert filter_str == "(Status,eq,Active)~and(Age,gt,21)~or(Role,eq,Admin)"

    def test_comparison_operators(self):
        """Test various comparison operators."""
        test_cases = [
            ("eq", "Active", "(Field,eq,Active)"),
            ("neq", "Inactive", "(Field,neq,Inactive)"),
            ("gt", 25, "(Field,gt,25)"),
            ("gte", 21, "(Field,gte,21)"),
            ("lt", 65, "(Field,lt,65)"),
            ("lte", 60, "(Field,lte,60)"),
            ("like", "%john%", "(Field,like,%john%)"),
            ("nlike", "%spam%", "(Field,nlike,%spam%)"),
            ("is", "null", "(Field,is,null)"),
            ("isnot", "null", "(Field,isnot,null)"),
            ("in", "A,B,C", "(Field,in,A,B,C)"),
            ("notin", "D,E,F", "(Field,notin,D,E,F)"),
        ]

        for operator, value, expected in test_cases:
            fb = FilterBuilder()
            filter_str = fb.where("Field", operator, value).build()
            assert filter_str == expected, f"Failed for operator {operator}"

    def test_date_value_handling(self):
        """Test handling of date values."""
        fb = FilterBuilder()
        test_date = date(2023, 12, 25)
        filter_str = fb.where("CreatedDate", "eq", test_date).build()

        assert filter_str == "(CreatedDate,eq,2023-12-25)"

    def test_datetime_value_handling(self):
        """Test handling of datetime values."""
        fb = FilterBuilder()
        test_datetime = datetime(2023, 12, 25, 14, 30, 0)
        filter_str = fb.where("CreatedAt", "gte", test_datetime).build()

        assert filter_str == "(CreatedAt,gte,2023-12-25 14:30:00)"

    def test_list_value_handling(self):
        """Test handling of list values for IN operations."""
        fb = FilterBuilder()
        values = ["Active", "Pending", "Review"]
        filter_str = fb.where("Status", "in", values).build()

        assert filter_str == "(Status,in,Active,Pending,Review)"

    def test_empty_filter_builder(self):
        """Test empty FilterBuilder."""
        fb = FilterBuilder()
        filter_str = fb.build()

        assert filter_str == ""

    def test_reset_filter_builder(self):
        """Test resetting FilterBuilder."""
        fb = FilterBuilder()
        fb.where("Status", "eq", "Active").and_("Age", "gt", 21)

        fb.reset()
        filter_str = fb.build()

        assert filter_str == ""
        assert fb._conditions == []


    def test_null_value_conditions(self):
        """Test NULL value conditions."""
        fb = FilterBuilder()

        # Test IS NULL
        filter_str = fb.where("DeletedAt", "is", None).build()
        assert filter_str == "(DeletedAt,is,None)"

        # Test IS NOT NULL
        fb.reset()
        filter_str = fb.where("Email", "isnot", None).build()
        assert filter_str == "(Email,isnot,None)"


class TestSortBuilder:
    """Test SortBuilder functionality."""

    def test_sort_builder_initialization(self):
        """Test SortBuilder initialization."""
        sb = SortBuilder()
        assert sb._sorts == []

    def test_simple_ascending_sort(self):
        """Test simple ascending sort."""
        sb = SortBuilder()
        result = sb.asc("Name")

        assert result is sb  # Method chaining
        sort_str = sb.build()
        assert sort_str == "Name"

    def test_simple_descending_sort(self):
        """Test simple descending sort."""
        sb = SortBuilder()
        sort_str = sb.desc("CreatedAt").build()

        assert sort_str == "-CreatedAt"

    def test_multiple_sort_conditions(self):
        """Test multiple sort conditions."""
        sb = SortBuilder()
        sort_str = (sb
            .asc("Department")
            .desc("Salary")
            .asc("Name")
            .build())

        assert sort_str == "Department,-Salary,Name"

    def test_empty_sort_builder(self):
        """Test empty SortBuilder."""
        sb = SortBuilder()
        sort_str = sb.build()

        assert sort_str == ""

    def test_reset_sort_builder(self):
        """Test resetting SortBuilder."""
        sb = SortBuilder()
        sb.asc("Name").desc("CreatedAt")

        sb.reset()
        sort_str = sb.build()

        assert sort_str == ""
        assert sb._sorts == []



class TestRealWorldScenarios:
    """Test realistic filtering and sorting scenarios."""

    def test_user_management_filters(self):
        """Test realistic user management filtering scenario."""
        fb = FilterBuilder()
        filter_str = (fb
            .where("Status", "eq", "Active")
            .and_("Age", "gte", 18)
            .and_("Department", "in", ["Engineering", "Sales", "Marketing"])
            .and_("Email", "isnot", None)
            .build())

        expected = "(Status,eq,Active)~and(Age,gte,18)~and(Department,in,Engineering,Sales,Marketing)~and(Email,isnot,None)"
        assert filter_str == expected

    def test_content_management_filters(self):
        """Test content management filtering scenario."""
        fb = FilterBuilder()

        # Articles that are published or in review, not deleted, created this year
        filter_str = (fb
            .where("Status", "eq", "Published")
            .or_("Status", "eq", "Review")
            .and_("DeletedAt", "is", None)
            .and_("CreatedAt", "gte", "2023-01-01")
            .build())

        expected = "(Status,eq,Published)~or(Status,eq,Review)~and(DeletedAt,is,None)~and(CreatedAt,gte,2023-01-01)"
        assert filter_str == expected

    def test_ecommerce_product_sorting(self):
        """Test e-commerce product sorting scenario."""
        sb = SortBuilder()

        # Sort by: Featured first, then by rating desc, then by price asc, then by name
        sort_str = (sb
            .desc("Featured")
            .desc("Rating")
            .asc("Price")
            .asc("Name")
            .build())

        assert sort_str == "-Featured,-Rating,Price,Name"

    def test_search_and_filter_combination(self):
        """Test search with filters combination."""
        fb = FilterBuilder()
        search_term = "software"

        filter_str = (fb
            .where("Title", "like", f"%{search_term}%")
            .or_("Description", "like", f"%{search_term}%")
            .or_("Tags", "like", f"%{search_term}%")
            .and_("Status", "eq", "Active")
            .and_("Category", "neq", "Archive")
            .build())

        expected = "(Title,like,%software%)~or(Description,like,%software%)~or(Tags,like,%software%)~and(Status,eq,Active)~and(Category,neq,Archive)"
        assert filter_str == expected
