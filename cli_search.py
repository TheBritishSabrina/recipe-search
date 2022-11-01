from weaviate_helper import WeaviateHelper

if __name__ == "__main__":
    weaviate_helper = WeaviateHelper()

    while True:
        query = input("Enter search query: ")
        results = weaviate_helper.search(query)
        print(results)