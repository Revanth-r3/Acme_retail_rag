import pandas as pd
from pipeline.schemas import DocumentChunk


def parse_csv(file_path):
    chunks = []

    df = pd.read_csv(file_path)

    for index, row in df.iterrows():
        text = ""

        for column in df.columns:
            text += f"{column}: {row[column]}\n"

        metadata = {
            "source": file_path,
            "file_type": "csv",
            "row": int(index) + 2
        }

        chunks.append(
            DocumentChunk(
                text=text.strip(),
                metadata=metadata
            )
        )

    return chunks


if __name__ == "__main__":
    file_path = "data/customer_sales.csv"

    chunks = parse_csv(file_path)

    print(f"Number of chunks: {len(chunks)}")

    for chunk in chunks:
        print("\n--- CHUNK ---")
        print(chunk.text)
        print("Metadata:", chunk.metadata)