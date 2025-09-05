from pymilvus import MilvusClient, DataType, CollectionSchema

client = MilvusClient(uri="http://localhost:19530")

print(client.list_collections())