import sys
import json
from weaviate_helper import WeaviateHelper

def load_data(filename):
    with open(filename) as f:
        dataset = json.load(f)
    return dataset

if __name__ == "__main__":
    # Note: first run pip install weaviate-client

    print("Initialising weaviate helper...")
    weaviate_helper = WeaviateHelper()
    weaviate_helper.delete_class()
    weaviate_helper.create_class()

    print("Loading dataset...")
    dataset = load_data("recipes.json")

    print("Inserting objects into weaviate instance...")
    weaviate_helper.insert_objects(dataset)

    print("Ready to search!")
    sys.exit(0)