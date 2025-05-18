import weaviate
from Helper import load_test_cases
from weaviate.util import generate_uuid5

class Weaviate:
    def __init__(self):
        self.client = weaviate.connect_to_local(
            host="localhost",
            port=8081,
            grpc_port=50051,
        )

    def create_collection(self, collection_name):
        self.client.collections.create(name=collection_name)
    

    def get_collections(self):
        print(self.client.collections.list_all()) 

    def delete_collections(self, collection_name):
        self.client.collections.delete(name=collection_name)
        
    def load_knowledge_base(self, collection_name):
        collection = self.client.collections.get(collection_name)
        
        df = load_test_cases("./static/knowledge_base.csv")
        
        # with collection.batch.dynamic() as batch:
        Pass, Fail = 0,0
        for index, row in df.iterrows():
            arow = row.to_dict()
            obj_uuid = generate_uuid5(arow["externalid"])
            try:
                collection.data.insert(
                    properties={
                    "Testcase_ID": str(arow["externalid"]),
                    "Summary": str(arow["summary"]),
                    "Precondition": str(arow["preconditions"]),
                    "Steps": str(arow["combined_text"]),   
                },
                    uuid = obj_uuid)
                Pass+=1
            except Exception as e:
                Fail+=1
                print(e)
                pass
        print("Batch import completed successfully.")
        return str(Pass), str(Fail)
        
    def get_nearest_match(self, collection_name, query, limit=5):
        collection = self.client.collections.get(collection_name)
        search_result = collection.query.near_text(query=query, limit=limit)
        # search_result = collection.query.hybrid(query=query, limit=limit)
        response = []
        for obj in search_result.objects:
            response.append(obj.properties)
        return response

    def close_client(self):
        self.client.close()  # Free up resources
    