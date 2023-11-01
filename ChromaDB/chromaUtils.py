from langchain.vectorstores import Chroma
import re

import sys, os
workingDirectory = os.getcwd()
chromaDirectory = os.path.join(workingDirectory, "ChromaDB")
if chromaDirectory not in sys.path:
    sys.path.append(chromaDirectory)

from client import persistent_client, embeddings

# retrieves an existing collection by its name. The collection returned is interacted with through LangChain's Chroma abstraction
def getCollection(collection_name):
    langchain_chroma = Chroma(
        client=persistent_client,
        collection_name=collection_name,
        embedding_function=embeddings,
    )
    return langchain_chroma

# Takes in a list of collection names and Deletes the correspondings collections
def clearCollection(list_of_collection_names):
    for collection_name in list_of_collection_names:
        try:
            persistent_client.delete_collection(name=collection_name)
            print(f"Collection {collection_name} has been deleted")
        except:
            print(collection_name)

# creates a brand new collection, assumes that clearCollection has been called prior to this
def createCollection(collection_name):
    persistent_client.get_or_create_collection(name=collection_name, embedding_function=embeddings)

def getDistinctFileNameList(collection_name):
    metadata_list = getCollection(collection_name).get()['metadatas']
    papers = [doc.get('fileName') for doc in metadata_list]
    return list(set(papers))

# returns collection names that have already been taken
def getListOfCollection():
    collections = persistent_client.list_collections()
    collections = [c.name for c in collections]
    collections.sort()
    return collections

def is_valid_name(name):
    # Condition 1: Check if the length is between 3 and 63 characters.
    condition_1 = 3 <= len(name) <= 63

    # Condition 2: Check if it starts and ends with a lowercase letter or digit,
    # and contains only dots, dashes, underscores, lowercase letters, uppercase letters, or digits.
    condition_2 = re.match(r"^[a-zA-Z0-9][a-zA-Z0-9-_.]*[a-zA-Z0-9]$", name) is not None

    # Condition 3: Check for two consecutive dots.
    condition_3 = ".." not in name

    # Condition 4: Check if it is not a valid IP address.
    def is_valid_ip(address):
        parts = address.split(".")
        if len(parts) != 4:
            return False
        for part in parts:
            if not part.isdigit() or not 0 <= int(part) <= 255:
                return False
        return True

    condition_4 = not is_valid_ip(name)

    # Combine the conditions using 'and' to get the final result.
    result = condition_1 and condition_2 and condition_3 and condition_4

    return result
