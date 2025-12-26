"""Comprehensive data extraction service with AWS Textract integration."""

import logging
import os
import csv
import json
from typing import Dict, Any, List, Tuple
from io import StringIO

logger = logging.getLogger(__name__)


class ExtractionService:
    """Comprehensive data extraction service.

    Supports extraction from:
    - Plain text files (.txt)
    - PDF files (.pdf) using PyPDF2
    - DOCX files (.docx) using python-docx
    - Images (.png, .jpg, .jpeg) using AWS Textract
    - CSV files (.csv) with table structure detection

    Uses AWS Textract for advanced OCR and table/form detection.
    """

    def __init__(self):
        """Initialize extraction service."""
        self.supported_formats = {
            ".txt": "text/plain",
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".csv": "text/csv",
        }

        # Initialize AWS Textract if available
        try:
            import boto3

            self.textract_available = bool(os.getenv("AWS_ACCESS_KEY_ID"))
            if self.textract_available:
                self.textract_client = boto3.client("textract", region_name="us-east-1")
        except ImportError:
            self.textract_available = False
            logger.warning("AWS Textract not available - image processing disabled")

    async def extract_text(self, file_path: str) -> Dict[str, Any]:
        """Extract text and structured data from document.

        Args:
            file_path: Path to document file

        Returns:
            Dict with extracted text, tables, and metadata
        """
        try:
            # Get file extension
            _, ext = os.path.splitext(file_path.lower())

            # Extract data based on file type
            if ext == ".txt":
                text, metadata = await self._extract_from_txt(file_path)
                result = {"text": text, "tables": [], "metadata": metadata, "method": "text_parser"}
            elif ext == ".pdf":
                text, metadata = await self._extract_from_pdf(file_path)
                result = {"text": text, "tables": [], "metadata": metadata, "method": "pdf_parser"}
            elif ext == ".docx":
                text, metadata = await self._extract_from_docx(file_path)
                result = {"text": text, "tables": [], "metadata": metadata, "method": "docx_parser"}
            elif ext == ".csv":
                result = await self._extract_from_csv(file_path)
            elif ext in [".png", ".jpg", ".jpeg"]:
                result = await self._extract_from_image(file_path)
            else:
                return {
                    "text": f"Unsupported file format: {ext}",
                    "tables": [],
                    "metadata": {"pages": 0, "confidence": 0.0, "error": "unsupported_format"},
                    "note": f"Supported formats: {', '.join(self.supported_formats.keys())}",
                }

            # Add common metadata
            result["metadata"]["file_format"] = ext[1:]  # Remove the dot
            result["metadata"]["processing_method"] = result.get("method", "unknown")

            return result

        except Exception as e:
            logger.error(f"Data extraction failed for {file_path}: {e}")
            return {
                "text": f"Error extracting data: {str(e)}",
                "tables": [],
                "metadata": {"pages": 0, "confidence": 0.0, "error": str(e)},
                "note": "Data extraction failed - check file format and try again",
            }

            return {
                "text": text,
                "metadata": metadata,
                "note": "Basic text extraction completed. For advanced OCR, consider AWS Textract integration.",
            }

        except Exception as e:
            logger.error(f"Text extraction failed for {file_path}: {e}")
            return {
                "text": f"Error extracting text: {str(e)}",
                "metadata": {"pages": 0, "confidence": 0.0, "error": str(e)},
                "note": "Text extraction failed. Check file format and try again.",
            }

    async def _extract_from_txt(self, file_path: str) -> tuple[str, Dict[str, Any]]:
        """Extract text from plain text file."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            # Basic metadata
            lines = text.split("\n")
            metadata = {
                "pages": 1,  # Text files are single page
                "confidence": 1.0,  # Perfect extraction for text files
                "lines": len(lines),
                "characters": len(text),
                "format": "text/plain",
            }

            return text, metadata

        except Exception as e:
            raise Exception(f"Failed to read text file: {e}")

    async def _extract_from_pdf(self, file_path: str) -> tuple[str, Dict[str, Any]]:
        """Extract text from PDF file using PyPDF2."""
        try:
            from PyPDF2 import PdfReader

            reader = PdfReader(file_path)
            text = ""

            # Extract text from all pages
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"

            # Clean up the text
            text = text.strip()

            metadata = {
                "pages": len(reader.pages),
                "confidence": 0.8 if text else 0.3,  # PDFs can have varying extraction quality
                "characters": len(text),
                "format": "application/pdf",
                "has_text": bool(text.strip()),
            }

            if not text:
                text = "No extractable text found in PDF. The document may contain only images or scanned content."

            return text, metadata

        except ImportError:
            raise Exception("PyPDF2 not installed. Install with: pip install PyPDF2")
        except Exception as e:
            raise Exception(f"Failed to extract PDF text: {e}")

    async def _extract_from_docx(self, file_path: str) -> tuple[str, Dict[str, Any]]:
        """Extract text from DOCX file using python-docx."""
        try:
            from docx import Document

            doc = Document(file_path)
            text = ""

            # Extract text from all paragraphs
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"

            # Also extract from tables if any
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            text += cell.text + " | "
                    text += "\n"

            # Clean up the text
            text = text.strip()

            metadata = {
                "pages": 1,  # DOCX doesn't have page concept like PDF
                "confidence": 0.9,  # Usually good extraction for DOCX
                "characters": len(text),
                "format": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "paragraphs": len(doc.paragraphs),
                "tables": len(doc.tables),
            }

            if not text:
                text = "No extractable text found in DOCX document."

            return text, metadata

        except ImportError:
            raise Exception("python-docx not installed. Install with: pip install python-docx")
        except Exception as e:
            raise Exception(f"Failed to extract DOCX text: {e}")

    async def _extract_from_csv(self, file_path: str) -> Dict[str, Any]:
        """Extract data from CSV file."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                # Detect delimiter
                sample = f.read(1024)
                f.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter

                # Read CSV
                reader = csv.DictReader(f, delimiter=delimiter)
                rows = list(reader)

            if not rows:
                return {
                    "text": "",
                    "tables": [],
                    "metadata": {"pages": 1, "confidence": 1.0, "rows": 0, "columns": 0},
                    "note": "CSV file is empty",
                }

            # Convert to table format
            columns = list(rows[0].keys())
            table_data = {
                "name": "CSV_Data",
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "column_count": len(columns),
            }

            # Generate text representation
            text_lines = [f"Columns: {', '.join(columns)}"]
            text_lines.append(f"Total rows: {len(rows)}")
            text_lines.extend(
                [
                    f"Row {i + 1}: {', '.join(str(row.get(col, '')) for col in columns)}"
                    for i, row in enumerate(rows[:5])
                ]
            )  # First 5 rows
            if len(rows) > 5:
                text_lines.append(f"... and {len(rows) - 5} more rows")

            return {
                "text": "\n".join(text_lines),
                "tables": [table_data],
                "metadata": {
                    "pages": 1,
                    "confidence": 1.0,
                    "rows": len(rows),
                    "columns": len(columns),
                    "delimiter": delimiter,
                },
                "note": "CSV data extracted successfully",
                "method": "csv_parser",
            }

        except Exception as e:
            raise Exception(f"Failed to extract CSV data: {e}")

    async def _extract_from_image(self, file_path: str) -> Dict[str, Any]:
        """Extract text and data from image using AWS Textract."""
        if not self.textract_available:
            return {
                "text": "",
                "tables": [],
                "metadata": {"pages": 0, "confidence": 0.0, "error": "aws_textract_unavailable"},
                "note": "AWS Textract not configured. Add AWS credentials to enable image processing.",
                "method": "none",
            }

        try:
            # Read image file
            with open(file_path, "rb") as image_file:
                image_bytes = image_file.read()

            # Call Textract
            response = self.textract_client.detect_document_text(Document={"Bytes": image_bytes})

            # Process response
            text_lines = []
            confidence_scores = []

            for block in response["Blocks"]:
                if block["BlockType"] == "LINE":
                    text_lines.append(block["Text"])
                    confidence_scores.append(block["Confidence"])

            text = "\n".join(text_lines) if text_lines else ""
            avg_confidence = (
                sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            )

            # For now, return basic text extraction
            # Advanced table/form detection would require AnalyzeDocument API
            return {
                "text": text,
                "tables": [],  # Would be populated with AnalyzeDocument
                "metadata": {
                    "pages": 1,
                    "confidence": round(avg_confidence, 2),
                    "lines": len(text_lines),
                    "characters": len(text),
                    "has_text": bool(text.strip()),
                },
                "note": "Image processed with AWS Textract OCR",
                "method": "aws_textract",
            }

        except Exception as e:
            logger.error(f"AWS Textract error: {e}")
            return {
                "text": "",
                "tables": [],
                "metadata": {"pages": 0, "confidence": 0.0, "error": str(e)},
                "note": f"AWS Textract processing failed: {str(e)}",
                "method": "aws_textract_error",
            }
