import os
import shutil
import subprocess
import tempfile

from pptx import Presentation

from pipeline.schemas import DocumentChunk


LIBREOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"


def convert_ppt_to_pptx(file_path):
    """
    Convert a legacy .ppt file to .pptx using LibreOffice.
    Returns the path to the temporary .pptx file.
    """

    if not os.path.exists(LIBREOFFICE_PATH):
        raise FileNotFoundError(
            "LibreOffice was not found. "
            f"Expected executable at: {LIBREOFFICE_PATH}"
        )

    temp_dir = tempfile.mkdtemp(prefix="ppt_conversion_")

    try:
        result = subprocess.run(
            [
                LIBREOFFICE_PATH,
                "--headless",
                "--convert-to",
                "pptx",
                "--outdir",
                temp_dir,
                file_path,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            shutil.rmtree(temp_dir, ignore_errors=True)

            raise RuntimeError(
                f"LibreOffice failed to convert PPT file.\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        converted_file = os.path.join(
            temp_dir,
            f"{base_name}.pptx"
        )

        if not os.path.exists(converted_file):
            shutil.rmtree(temp_dir, ignore_errors=True)

            raise RuntimeError(
                "LibreOffice completed without creating the expected PPTX file."
            )

        return converted_file, temp_dir

    except Exception:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def parse_ppt(file_path):
    chunks = []

    extension = os.path.splitext(file_path)[1].lower()

    temp_dir = None

    if extension == ".ppt":
        parsing_file = None

        try:
            parsing_file, temp_dir = convert_ppt_to_pptx(file_path)
            presentation = Presentation(parsing_file)

        except Exception:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            raise

    elif extension == ".pptx":
        presentation = Presentation(file_path)

    else:
        raise ValueError(
            f"Unsupported PowerPoint format: {extension}. "
            "Supported formats are .ppt and .pptx"
        )

    try:
        for slide_number, slide in enumerate(
            presentation.slides,
            start=1
        ):

            slide_text = []

            # Extract slide text and tables
            for shape in slide.shapes:

                if hasattr(shape, "text") and shape.text.strip():
                    slide_text.append(shape.text.strip())

                if shape.has_table:
                    for row in shape.table.rows:
                        row_text = []

                        for cell in row.cells:
                            row_text.append(cell.text.strip())

                        slide_text.append(" | ".join(row_text))

            # Extract speaker notes
            if slide.has_notes_slide:
                notes_slide = slide.notes_slide

                for shape in notes_slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        slide_text.append(
                            "Speaker Notes: " + shape.text.strip()
                        )

            if not slide_text:
                continue

            text = "\n".join(slide_text)

            title = ""

            if slide.shapes.title:
                title = slide.shapes.title.text.strip()

            metadata = {
                "source": file_path,
                "file_type": extension.lstrip("."),
                "slide": slide_number,
                "title": title,
            }

            chunks.append(
                DocumentChunk(
                    text=text,
                    metadata=metadata
                )
            )

    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

    return chunks


if __name__ == "__main__":

    file_path = "data/q1_business_review.pptx"

    chunks = parse_ppt(file_path)

    print(f"Number of chunks: {len(chunks)}")

    for chunk in chunks:
        print("\n--- CHUNK ---")
        print(chunk.text)
        print("Metadata:", chunk.metadata)