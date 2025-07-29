from pymilvus import MilvusClient, DataType

client = MilvusClient(uri="http://localhost:19530")

schema = client.create_schema(auto_id=True)

schema.add_field(
    field_name="id",
    datatype=DataType.INT64,
    is_primary=True,
    auto_id=True,
)

schema.add_field(
    field_name="image_url",
    datatype=DataType.VARCHAR,
    max_length=128
)

schema.add_field(
    field_name="type",
    datatype=DataType.VARCHAR,
    max_length=32
)

schema.add_field(
    field_name="theme",
    datatype=DataType.VARCHAR,
    max_length=128
)

schema.add_field(
    field_name="title",
    datatype=DataType.VARCHAR,
    max_length=128
)

schema.add_field(
    field_name="text",
    datatype=DataType.VARCHAR,
    max_length=4096
)

schema.add_field(
    field_name="metadata",
    datatype=DataType.JSON,
    nullable=False
)

schema.add_field(
    field_name="data",
    datatype=DataType.VARCHAR,
    max_length=8128,
)

schema.add_field(
    field_name="text_dense",
    datatype=DataType.FLOAT_VECTOR,
    dim=4096
)

schema.add_field(
    field_name="image_dense",
    datatype=DataType.FLOAT_VECTOR,
    dim=4096
)

index_params = client.prepare_index_params()

# 3.4. Add indexes
index_params.add_index(
    field_name="text_dense",
    index_name="text_dense_index",
    index_type="AUTOINDEX",
    metric_type="IP"
)

index_params.add_index(
    field_name="image_dense",
    index_name="image_dense_index",
    index_type="AUTOINDEX",
    metric_type="IP"
)

if client.has_collection(collection_name="test"):
    client.drop_collection(collection_name="test")
client.create_collection(
    collection_name="test",
    dimension=4096,  # The vectors we will use in this demo has 768 dimensions
    schema=schema,
    index_params=index_params
)
