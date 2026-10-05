from ingestion.excel_parser import parse_excel
from ingestion.csv_parser import parse_csv
from ingestion.ppt_parser import parse_ppt


def parse_document(file_path):
    """
    Select the appropriate parser based on file extension.
    """

    file_path_lower = file_path.lower()

    if file_path_lower.endswith((".xlsx", ".xls")):
        return parse_excel(file_path)

    elif file_path_lower.endswith(".csv"):
        return parse_csv(file_path)

    elif file_path_lower.endswith((".pptx", ".ppt")):
        return parse_ppt(file_path)

    else:
        raise ValueError(
            f"Unsupported file type: {file_path}"
        )