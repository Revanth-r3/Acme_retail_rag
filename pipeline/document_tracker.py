import hashlib
import os
import json


class DocumentTracker:

    def __init__(
        self,
        tracker_path="./chroma_db/document_tracker.json"
    ):
        self.tracker_path = tracker_path

        os.makedirs(
            os.path.dirname(self.tracker_path),
            exist_ok=True
        )

        if os.path.exists(self.tracker_path):
            with open(self.tracker_path, "r") as f:
                self.documents = json.load(f)
        else:
            self.documents = {}

    def calculate_hash(self, file_path):
        sha256 = hashlib.sha256()

        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)

        return sha256.hexdigest()

    def is_indexed(self, file_path):
        return file_path in self.documents

    def is_unchanged(self, file_path):
        if not self.is_indexed(file_path):
            return False

        current_hash = self.calculate_hash(file_path)

        return self.documents[file_path] == current_hash

    def mark_indexed(self, file_path):
        file_hash = self.calculate_hash(file_path)

        self.documents[file_path] = file_hash

        with open(self.tracker_path, "w") as f:
            json.dump(
                self.documents,
                f,
                indent=4
            )