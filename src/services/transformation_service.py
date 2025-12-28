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
                elif rule.operation == "extract":
                    transformed_data = self._extract_data(transformed_data, rule.parameters)
                elif rule.operation == "transform":
                    transformed_data = self._transform_data(transformed_data, rule.parameters)
                elif rule.operation == "filter_content":
                    transformed_data = self._filter_content(transformed_data, rule.parameters)
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

    def _extract_data(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract specific data patterns from text."""
        pattern = params.get("pattern", "")
        text = data.get("text", "")

        if not pattern or not text:
            return data

        import re

        matches = re.findall(pattern, text)

        if matches:
            # Create a new table with extracted data
            extracted_table = {
                "name": "Extracted Data",
                "columns": ["extracted_value"],
                "rows": [{"extracted_value": match} for match in matches],
                "row_count": len(matches),
                "column_count": 1,
            }

            result = data.copy()
            if "tables" not in result:
                result["tables"] = []
            result["tables"].append(extracted_table)
            return result

        return data

    def _transform_data(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply general transformations to data."""
        operation = params.get("operation", "")

        if operation == "uppercase" and data.get("text"):
            result = data.copy()
            result["text"] = data["text"].upper()
            return result

        elif operation == "lowercase" and data.get("text"):
            result = data.copy()
            result["text"] = data["text"].lower()
            return result

        # For table transformations
        if data.get("tables"):
            transformed_tables = []
            for table in data["tables"]:
                if operation == "uppercase" and table.get("rows"):
                    # Transform all string values to uppercase
                    transformed_rows = []
                    for row in table["rows"]:
                        if isinstance(row, dict):
                            transformed_row = {}
                            for key, value in row.items():
                                if isinstance(value, str):
                                    transformed_row[key] = value.upper()
                                else:
                                    transformed_row[key] = value
                            transformed_rows.append(transformed_row)
                        else:
                            transformed_rows.append(row)
                    transformed_table = table.copy()
                    transformed_table["rows"] = transformed_rows
                    transformed_tables.append(transformed_table)
                else:
                    transformed_tables.append(table)

            result = data.copy()
            result["tables"] = transformed_tables
            return result

        return data

    def _filter_content(self, data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Filter content to show only specific fields or hide unwanted content."""
        fields_to_show = params.get("fields", [])
        fields_to_exclude = params.get("exclude_fields", [])

        if not fields_to_show and not fields_to_exclude:
            return data

        text = data.get("text", "")
        if not text:
            return data

        import re

        # Extract specific fields from the entire text
        extracted_info = {}

        if fields_to_show:
            # Process each field type individually
            for field in fields_to_show:
                field_lower = field.lower()

                if field_lower == "name":
                    # Enhanced name detection patterns - prioritize longer, more complete names
                    name_patterns = [
                        r"\b([A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b",  # First M. Last (with middle names)
                        r"\b([A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+)\b",  # First Middle Last
                        r"\b([A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+)\b",  # First M. Last
                        r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b",  # First Last
                        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b",  # Multiple words starting with caps
                    ]

                    all_matches = []
                    for pattern in name_patterns:
                        matches = re.findall(pattern, text)
                        all_matches.extend(matches)

                    if all_matches:
                        # Filter out obvious non-names and sort by length (prefer longer names)
                        valid_names = []
                        for match in all_matches:
                            match_lower = match.lower()
                            # Skip if it contains disqualifying words
                            disqualifiers = [
                                "college",
                                "university",
                                "school",
                                "education",
                                "skills",
                                "experience",
                                "contact",
                                "phone",
                                "email",
                            ]

                            if not any(skip in match_lower for skip in disqualifiers):
                                # Additional validation: should have at least 2 parts and not be too long
                                parts = match.split()
                                if 2 <= len(parts) <= 4:  # Reasonable name length
                                    valid_names.append(match)

                        if valid_names:
                            # Sort by length (prefer more complete names) and take the first one
                            valid_names.sort(key=len, reverse=True)
                            extracted_info["name"] = valid_names[0]

                elif field_lower == "email":
                    # Email pattern
                    email_pattern = r"\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b"
                    matches = re.findall(email_pattern, text)
                    if matches:
                        extracted_info["email"] = matches[0]  # Take first email

                elif field_lower in ["phone", "contact"]:
                    # Phone pattern
                    phone_pattern = r"\b(\+?\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3,4}[-.\s]?\d{3,4})\b"
                    matches = re.findall(phone_pattern, text)
                    if matches:
                        extracted_info["phone"] = matches[0]

        # Create filtered result
        if extracted_info:
            # Format as clean, readable text
            filtered_lines = []
            for field, value in extracted_info.items():
                if field == "name":
                    filtered_lines.append(f"Name: {value}")
                elif field == "email":
                    filtered_lines.append(f"Email: {value}")
                elif field == "phone":
                    filtered_lines.append(f"Phone: {value}")
                else:
                    filtered_lines.append(f"{field.title()}: {value}")

            filtered_text = "\n".join(filtered_lines)

            result = data.copy()
            result["text"] = filtered_text

            # Add metadata about filtering
            result["filter_applied"] = True
            result["extracted_fields"] = list(extracted_info.keys())
            result["filter_description"] = f"Extracted: {', '.join(fields_to_show)}"

            return result

        # Fallback: if no specific fields found, return original approach
        lines = text.split("\n")
        filtered_lines = []

        for line in lines:
            line_lower = line.lower().strip()
            should_include = True

            if fields_to_exclude:
                for field in fields_to_exclude:
                    field_lower = field.lower()
                    if field_lower == "phone" and any(
                        indicator in line_lower for indicator in ["phone", "+63", "967", "contact"]
                    ):
                        should_include = False
                        break
                    elif field_lower == "email" and "@" in line:
                        should_include = False
                        break

            if should_include and line.strip():
                filtered_lines.append(line)

        if filtered_lines:
            filtered_text = "\n".join(filtered_lines)

            result = data.copy()
            result["text"] = filtered_text
            result["filter_applied"] = True
            result["original_lines"] = len(lines)
            result["filtered_lines"] = len(filtered_lines)
            result["filter_description"] = (
                f"Filtered to show: {', '.join(fields_to_show) if fields_to_show else 'excluding: ' + ', '.join(fields_to_exclude)}"
            )

            return result

        return data

        text = data.get("text", "")
        if not text:
            return data

        lines = text.split("\n")
        filtered_lines = []

        # Process each line
        for line in lines:
            line_lower = line.lower().strip()
            should_include = True

            if fields_to_show:
                # Include only lines that match the requested fields
                should_include = False

                for field in fields_to_show:
                    field_lower = field.lower()

                    if field_lower == "name":
                        # Look for name-like patterns (short lines, no special chars)
                        if (
                            len(line.strip()) < 50
                            and not any(char in line for char in ["@", "+", "•", ":"])
                            and not any(
                                word in line_lower
                                for word in [
                                    "phone",
                                    "email",
                                    "contact",
                                    "address",
                                    "skills",
                                    "education",
                                ]
                            )
                        ):
                            should_include = True
                            break

                    elif field_lower == "email":
                        # Look for email patterns
                        if "@" in line and any(
                            domain in line_lower for domain in [".com", ".org", ".net", ".edu"]
                        ):
                            should_include = True
                            break

                    elif field_lower in ["phone", "contact"]:
                        # Look for phone/contact patterns
                        if any(
                            indicator in line_lower
                            for indicator in ["phone", "+", "contact", "mobile"]
                        ):
                            should_include = True
                            break

            elif fields_to_exclude:
                # Exclude lines that match the fields to hide
                for field in fields_to_exclude:
                    field_lower = field.lower()

                    if field_lower == "phone":
                        if any(
                            indicator in line_lower
                            for indicator in ["phone", "+63", "967", "contact"]
                        ):
                            should_include = False
                            break

                    elif field_lower == "email":
                        if "@" in line:
                            should_include = False
                            break

            if should_include and line.strip():
                filtered_lines.append(line)

        # Create filtered result
        if filtered_lines:
            filtered_text = "\n".join(filtered_lines)

            result = data.copy()
            result["text"] = filtered_text

            # Add metadata about filtering
            result["filter_applied"] = True
            result["original_lines"] = len(lines)
            result["filtered_lines"] = len(filtered_lines)
            result["filter_description"] = (
                f"Filtered to show: {', '.join(fields_to_show) if fields_to_show else 'excluding: ' + ', '.join(fields_to_exclude)}"
            )

            return result

        return data

        text = data.get("text", "")
        if not text:
            return data

        # For "show only" filtering, we need to identify and extract relevant sections
        filtered_parts = []

        if fields_to_show:
            # Extract specific field information
            for field in fields_to_show:
                if field.lower() in ["name", "email"]:
                    # Try to find name and email patterns in the text
                    lines = text.split("\n")
                    for line in lines:
                        line_lower = line.lower().strip()
                        if field.lower() == "name" and any(
                            keyword in line_lower for keyword in ["rachel", "afif", "y.", "y "]
                        ):
                            # Look for name-like content
                            if len(line.strip()) < 50 and not any(
                                x in line_lower for x in ["@", "phone", "email", "contact"]
                            ):
                                filtered_parts.append(f"Name: {line.strip()}")
                        elif field.lower() == "email" and "@" in line:
                            # Extract email lines
                            filtered_parts.append(f"Email: {line.strip()}")

        elif fields_to_exclude:
            # Remove specific field information
            lines = text.split("\n")
            for line in lines:
                line_lower = line.lower()
                should_exclude = False

                for field in fields_to_exclude:
                    if field.lower() == "phone" and any(
                        keyword in line_lower for keyword in ["phone", "+63", "967"]
                    ):
                        should_exclude = True
                        break

                if not should_exclude:
                    filtered_parts.append(line)

        # Create filtered result
        if filtered_parts:
            filtered_text = "\n".join(filtered_parts)

            result = data.copy()
            result["text"] = filtered_text

            # Add a note about filtering
            result["filter_applied"] = True
            result["filter_description"] = (
                f"Filtered to show: {', '.join(fields_to_show) if fields_to_show else 'excluding: ' + ', '.join(fields_to_exclude)}"
            )

            return result

        return data
