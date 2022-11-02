# Recipe Search
A lightweight neural search engine for recipe data

## Usage

Before use, please:
- Insert a Hugging Face API key in `docker-compose.yml` (you can get one free from huggingface.co when you create an account)
- Ensure you have the Weaviate Python client installed (pip command is `pip install weaviate-client`)

To spin up a weaviate instance, run:
```
docker compose up -d
```

Wait for this to finish, then insert data from `recipes.json` to weaviate:
```
python3 insert_data.py
```

If this runs into rate-limiting issues, generate a new API key and send through a small amount of recipes at a time (32 should work).

To start the command line search interface, run:
```
python3 cli_search.py
```

Happy searching!
