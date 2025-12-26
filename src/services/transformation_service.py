"""Data transformation engine for applying transformation rules."""

import logging
from typing import Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TransformationRule:
    """Represents a data transformation rule."""

    operation: str
    parameters: Dict[str, Any]
    description: str


class TransformationService:
    """Applies data transformation rules to extracted document data."""

    def apply_transformations(
        self, data: Dict[str, Any], rules: List[TransformationRule]
    ) -> Dict[str, Any]:
        """Apply a list of transformation rules to the data.

        Args:
            data: Extracted document data
            rules: List of transformation rules to apply

        Returns:
            Transformed data
        """
        transformed_data = data.copy()

        for rule in rules:
            try:
                logger.info(f"Applying transformation: {rule.operation}")

                if rule.operation == "select_columns":
                    transformed_data = self._select_columns(transformed_data, rule.parameters)
                elif rule.operation == "rename_columns":
                    transformed_data = self._rename_columns(transformed_data, rule.parameters)
                elif rule.operation == "filter_rows":
                    transformed_data = self._filter_rows(transformed_data, rule.parameters)
                elif rule.operation == "sort_rows":
                    transformed_data = self._sort_rows(transformed_data, rule.parameters)
                elif rule.operation == "limit_rows":
                    transformed_data = self._limit_rows(transformed_data, rule.parameters)
                elif rule.operation == "create_table_from_text":
                    transformed_data = self._create_table_from_text(
                        transformed_data, rule.parameters
                    )
                elif rule.operation == "merge_tables":
                    transformed_data = self._merge_tables(transformed_data, rule.parameters)
                else:
                    logger.warning(f"Unknown transformation operation: {rule.operation}")

            except Exception as e:
                logger.error(f"Failed to apply transformation {rule.operation}: {e}")
                # Continue with other transformations
                continue

        return transformed_data

    def _select_columns(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Select specific columns from tables."""
        columns_to_keep = params.get("columns", [])

        if not data.get("tables"):
            return data

        transformed_tables = []
        for table in data["tables"]:
            if not table.get("columns"):
                transformed_tables.append(table)
                continue

            # Filter columns
            column_indices = []
            new_columns = []

            for i, col in enumerate(table["columns"]):
                if col in columns_to_keep:
                    column_indices.append(i)
                    new_columns.append(col)

            # Filter rows to keep only selected columns
            new_rows = []
            for row in table.get("rows", []):
                if isinstance(row, dict):
                    # Dict format
                    new_row = {col: row.get(col) for col in new_columns}
                else:
                    # List format
                    new_row = [row[i] for i in column_indices if i < len(row)]
                new_rows.append(new_row)

            transformed_table = table.copy()
            transformed_table["columns"] = new_columns
            transformed_table["rows"] = new_rows
            transformed_table["column_count"] = len(new_columns)

            transformed_tables.append(transformed_table)

        result = data.copy()
        result["tables"] = transformed_tables
        return result

    def _rename_columns(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Rename columns in tables."""
        column_mapping = params.get("mapping", {})

        if not data.get("tables"):
            return data

        transformed_tables = []
        for table in data["tables"]:
            if not table.get("columns"):
                transformed_tables.append(table)
                continue

            # Rename columns
            new_columns = [column_mapping.get(col, col) for col in table["columns"]]

            # Update column references in rows if they're dict format
            new_rows = []
            for row in table.get("rows", []):
                if isinstance(row, dict):
                    new_row = {column_mapping.get(k, k): v for k, v in row.items()}
                    new_rows.append(new_row)
                else:
                    new_rows.append(row)  # List format unchanged

            transformed_table = table.copy()
            transformed_table["columns"] = new_columns
            transformed_table["rows"] = new_rows

            transformed_tables.append(transformed_table)

        result = data.copy()
        result["tables"] = transformed_tables
        return result

    def _filter_rows(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Filter rows based on criteria."""
        filter_column = params.get("column", "")
        filter_value = params.get("value", "")
        filter_operation = params.get("operation", "equals")  # equals, contains, greater_than, etc.

        if not data.get("tables") or not filter_column:
            return data

        transformed_tables = []
        for table in data["tables"]:
            if not table.get("rows"):
                transformed_tables.append(table)
                continue

            filtered_rows = []
            for row in table["rows"]:
                if isinstance(row, dict):
                    cell_value = str(row.get(filter_column, "")).lower()
                    filter_val_lower = str(filter_value).lower()

                    should_keep = False
                    if filter_operation == "equals":
                        should_keep = cell_value == filter_val_lower
                    elif filter_operation == "contains":
                        should_keep = filter_val_lower in cell_value
                    elif filter_operation == "starts_with":
                        should_keep = cell_value.startswith(filter_val_lower)
                    else:
                        should_keep = True  # Keep all if unknown operation

                    if should_keep:
                        filtered_rows.append(row)
                else:
                    # For list format, we can't easily filter by column name
                    filtered_rows.append(row)

            transformed_table = table.copy()
            transformed_table["rows"] = filtered_rows
            transformed_table["row_count"] = len(filtered_rows)

            transformed_tables.append(transformed_table)

        result = data.copy()
        result["tables"] = transformed_tables
        return result

    def _sort_rows(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Sort rows by column values."""
        sort_column = params.get("column", "")
        sort_order = params.get("order", "asc")  # asc or desc

        if not data.get("tables") or not sort_column:
            return data

        transformed_tables = []
        for table in data["tables"]:
            if not table.get("rows"):
                transformed_tables.append(table)
                continue

            try:
                # Sort rows
                sorted_rows = sorted(
                    table["rows"],
                    key=lambda row: (
                        str(row.get(sort_column, ""))
                        if isinstance(row, dict)
                        else str(row[0] if row else "")
                    ),
                    reverse=(sort_order == "desc"),
                )

                transformed_table = table.copy()
                transformed_table["rows"] = sorted_rows

                transformed_tables.append(transformed_table)
            except Exception as e:
                logger.warning(f"Failed to sort table: {e}")
                transformed_tables.append(table)  # Keep original if sorting fails

        result = data.copy()
        result["tables"] = transformed_tables
        return result

    def _limit_rows(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Limit the number of rows in tables."""
        limit = params.get("limit", 10)

        if not data.get("tables"):
            return data

        transformed_tables = []
        for table in data["tables"]:
            if not table.get("rows"):
                transformed_tables.append(table)
                continue

            limited_rows = table["rows"][:limit]

            transformed_table = table.copy()
            transformed_table["rows"] = limited_rows
            transformed_table["row_count"] = len(limited_rows)

            transformed_tables.append(transformed_table)

        result = data.copy()
        result["tables"] = transformed_tables
        return result

    def _create_table_from_text(
        self, data: Dict[str, Any], params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a table structure from unstructured text."""
        columns = params.get("columns", [])
        extraction_rules = params.get("extraction_rules", {})

        text = data.get("text", "")
        if not text or not columns:
            return data

        # Simple table creation - extract basic patterns
        # This can be enhanced with more sophisticated NLP
        rows = []

        # For demonstration, create sample rows based on extraction rules
        sample_row = {}
        for col in columns:
            rule = extraction_rules.get(col, "")
            if "email" in rule.lower():
                sample_row[col] = "extracted@email.com"
            elif "phone" in rule.lower():
                sample_row[col] = "+1-234-567-8900"
            elif "name" in rule.lower():
                sample_row[col] = "Extracted Name"
            elif "experience" in rule.lower():
                sample_row[col] = "5 years"
            else:
                sample_row[col] = f"Extracted {col}"

        rows.append(sample_row)

        new_table = {
            "name": "Extracted Data",
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "column_count": len(columns),
        }

        result = data.copy()
        if "tables" not in result:
            result["tables"] = []
        result["tables"].append(new_table)

        return result

    def _merge_tables(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple tables into one."""
        if not data.get("tables") or len(data["tables"]) < 2:
            return data

        # Simple merge - combine all tables with same columns
        merged_table = {
            "name": "Merged Data",
            "columns": [],
            "rows": [],
            "row_count": 0,
            "column_count": 0,
        }

        # Collect all unique columns
        all_columns = set()
        for table in data["tables"]:
            all_columns.update(table.get("columns", []))

        merged_table["columns"] = list(all_columns)
        merged_table["column_count"] = len(all_columns)

        # Merge rows
        for table in data["tables"]:
            for row in table.get("rows", []):
                if isinstance(row, dict):
                    # Ensure all columns are present
                    merged_row = {}
                    for col in merged_table["columns"]:
                        merged_row[col] = row.get(col, "")
                    merged_table["rows"].append(merged_row)
                else:
                    # Convert list to dict if possible
                    merged_table["rows"].append(row)

        merged_table["row_count"] = len(merged_table["rows"])

        result = data.copy()
        result["tables"] = [merged_table]  # Replace with merged table

        return result
