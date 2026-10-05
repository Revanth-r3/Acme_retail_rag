from pptx import Presentation
from pipeline.schemas import DocumentChunk


def parse_ppt(file_path):
    chunks = []

    presentation = Presentation(file_path)

    for slide_number, slide in enumerate(presentation.slides, start=1):

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

        # Extract speaker notes only if the slide has a notes slide
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
            "file_type": "pptx",
            "slide": slide_number,
            "title": title
        }

        chunks.append(
            DocumentChunk(
                text=text,
                metadata=metadata
            )
        )

    return chunks


if __name__ == "__main__":

    file_path = "data/q1_business_review.pptx"

    chunks = parse_ppt(file_path)

    print(f"Number of chunks: {len(chunks)}")

    for chunk in chunks:
        print("\n--- CHUNK ---")
        print(chunk.text)
        print("Metadata:", chunk.metadata)