import weaviate

class WeaviateHelper():

    def __init__(self):
        """
        Instantiate a weaviate object that connects to the weaviate instance
        """
        # Make sure your cluster is available on port 8080
        self.cluster_name = "http://localhost:8080"

        self.client = weaviate.Client(self.cluster_name)
        self._configure_batching(self.client)

        self.class_name = "Recipes"
        self.class_definition = {
            "class": self.class_name,
            "description": "A recipe with an ingredient list and instructions",
            "properties": [
                { 
                    "dataType": ["string"],
                    "description": "Recipe title",
                    "name": "title",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": False,
                            "vectorizePropertyName": False
                        }
                    },
                },
                {
                    # Ideally this should be a 'text' field so ingredients are 
                    # tokenised first, but this will hit Hugging Face rate limits
                    # so we use a 'string' instead
                    "dataType": ["string"],
                    "description": "Ingredient list with quantities",
                    "name": "ingredients",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": False,
                            "vectorizePropertyName": True
                        }
                    },
                },
                {
                    "dataType": ["string"],
                    "description": "Instructions for preparing the recipe",
                    "name": "directions",
                    "moduleConfig": {
                        "text2vec-huggingface": {
                            "skip": False,
                            "vectorizePropertyName": False
                        }
                    },
                }
            ],
            "moduleConfig": {
                "text2vec-huggingface": {
                    "model": "sentence-transformers/all-MiniLM-L6-v2", # A good all-round retriever
                    "options": {
                        "waitForModel": True,
                        "useGPU": False,
                        "useCache": True
                    },
                    # We don't need to include the class name, as this will unnecessarily
                    # shift all of the data in the direction of the 'recipes' vector
                    "vectorizeClassName": "false"
                }
            },
        }


    def _configure_batching(self, client):
        """
        Configure default settings for batching operations
        """
        client.batch.configure(
            batch_size=100, 
            # Dynamically update the batch size based on bandwidth
            dynamic=True,
            # Retry 3 times when a timeout error is thrown
            timeout_retries=3,
        )


    def _contains_class(self):
        """
        Check whether the desired class already exists in the Weaviate schema
        """
        return self.client.schema.contains(self.class_definition)


    def create_class(self):
        """
        Create a class in the weaviate instance
        """
        if self._contains_class():
            print(f"Class {self.class_name} already exists!")
            return
        
        self.client.schema.create_class(self.class_definition)
        print(f"Class {self.class_name} created")


    def delete_class(self):
        """
        Remove the specified class from the weaviate instance
        """
        if not self._contains_class():
            print(f"Class {self.class_name} doesn't exist!")
            return

        self.client.schema.delete_class(self.class_name)
        print(f"Class {self.class_name} deleted")


    def insert_objects(self, recipe_objects):
        """
        Add recipes to the weaviate vector index

        Recipes should be of the form:
            recipe_objects = [
                {
                    "title": "No-Bake Nut Cookies",
                    "ingredients": "1 c. firmly packed brown sugar 1/2 c. evaporated milk \
                        1/2 tsp. vanilla 1/2 c. broken nuts (pecans) 2 Tbsp. butter or margarine \
                        3 1/2 c. bite size shredded rice biscuits",
                    "directions": "In a heavy 2-quart saucepan, mix brown sugar, nuts, evaporated \
                        milk and butter or margarine. Stir over medium heat until mixture bubbles \
                        all over top. Boil and stir 5 minutes more. Take off heat. Stir in vanilla \
                        and cereal; mix well. Using 2 teaspoons, drop and shape into 30 clusters \
                        on wax paper. Let stand until firm, about 30 minutes."
                },
                ...
            ]

        Note that this prints errors if any are thrown, since `check_batch_result` is the
        default error callback function for `add_data_object`
        """
        with self.client.batch as batch:
            for object in recipe_objects:
                batch.add_data_object(data_object=object, class_name=self.class_name)


    def search(self, query):
        """
        Search the weaviate recipe index
        """
        near_text = { "concepts": [query] }
        results = (
            self.client.query
            .get(self.class_name, ["title", "ingredients", "directions"])
            .with_near_text(near_text)
            .do()
        )
        return results