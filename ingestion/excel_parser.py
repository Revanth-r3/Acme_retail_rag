# import pandas as pd


# def parse_excel(file_path):
#     chunks = []

#     excel_file = pd.ExcelFile(file_path)

#     for sheet_name in excel_file.sheet_names:

#         df = pd.read_excel(file_path, sheet_name=sheet_name)

#         for index, row in df.iterrows():

#             text = f"Sheet: {sheet_name}\n"

#             for column in df.columns:
#                 text += f"{column}: {row[column]}\n"

#             metadata = {
#                 "source": file_path,
#                 "file_type": "excel",
#                 "sheet": sheet_name,
#                 "row": int(index) + 2
#             }

#             chunks.append({
#                 "text": text.strip(),
#                 "metadata": metadata
#             })

#     return chunks


# if __name__ == "__main__":

#     file_path = "data/sales_q1.xlsx"

#     chunks = parse_excel(file_path)

#     print(f"Number of chunks: {len(chunks)}")

#     for chunk in chunks:
#         print("\n--- CHUNK ---")
#         print(chunk["text"])
#         print("Metadata:", chunk["metadata"])

import pandas as pd
from pipeline.schemas import DocumentChunk


def parse_excel(file_path):
    chunks = []

    excel_file = pd.ExcelFile(file_path)

    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        for index, row in df.iterrows():
            text = f"Sheet: {sheet_name}\n"

            for column in df.columns:
                text += f"{column}: {row[column]}\n"

            metadata = {
                "source": file_path,
                "file_type": "excel",
                "sheet": sheet_name,
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
    file_path = "data/sales_q1.xlsx"

    chunks = parse_excel(file_path)

    print(f"Number of chunks: {len(chunks)}")

    for chunk in chunks:
        print("\n--- CHUNK ---")
        print(chunk.text)
        print("Metadata:", chunk.metadata)