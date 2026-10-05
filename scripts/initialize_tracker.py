from pipeline.document_tracker import DocumentTracker


files = [
    "data/sales_q1.xlsx",
    "data/customer_sales.csv",
    "data/q1_business_review.pptx"
]

tracker = DocumentTracker()

for file_path in files:

    if tracker.is_indexed(file_path):
        print(f"Already tracked: {file_path}")
        continue

    tracker.mark_indexed(file_path)

    print(f"Added to tracker: {file_path}")

print("\nTracker initialized successfully.")