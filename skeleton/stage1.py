import json
import jsonschema
from jsonschema import validate
import uuid


class POLICY_TYPE:
    ARUPA = "Arupa"
    FRISCO = "Frisco"


policy_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9_]{1,32}$",
            "maxLength": 32
        },
        "description": {
            "type": "string"
        },
        "type": {
            "type": "string",
            "enum": [POLICY_TYPE.ARUPA, POLICY_TYPE.FRISCO]
        }
    },
    "required": ["name", "description", "type"]
}

json_identifier_schema = {
    "type": "object",
    "properties": {
        "policy_id": {
            "type": "string"
        }
    },
    "required": ["policy_id"]
}


class Policy:
    def __init__(self, id: str, name: str, description: str, type) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.type = type

    def get_policy_dict(self):
        res_dict = {

            "name": self.name,
            "description": self.description,
            "type": self.type
        }

        return res_dict


class PolicyAPI:
    def __init__(self) -> None:

        # for each policy ID KEY - the VALUE is the type of policy (Arupa or Frisco)
        self.policies_all_ids_types_and_names = {}
        # saves the policy by name KEY
        self.policies_Arupa = {}
        # saves the policy by policy ID KEY
        self.policies_Frisco = {}

    def create_policy(self, json_input: str) -> str:

        # Validate the data against the schema
        try:
            policy_dict = json.loads(json_input)
            validate(instance=policy_dict, schema=policy_schema)
            # print("Validation successful!")
        except jsonschema.exceptions.ValidationError as e:
            raise e

        # creates unique id for the policy and creates a Policy Object accordingly
        policy_id = str(uuid.uuid4())
        policy_obj = Policy(
            policy_id,
            policy_dict["name"],
            policy_dict["description"],
            policy_dict["type"]
        )

        # add Policy Object to the dict of policies according to policy type.
        if policy_dict["type"] == POLICY_TYPE.ARUPA:
            if policy_dict["name"] not in self.policies_Arupa:
                self.policies_Arupa[policy_dict["name"]] = policy_obj
                self.policies_all_ids_types_and_names[policy_id] = (POLICY_TYPE.ARUPA, policy_dict["name"])
            else:
                raise Exception("ERROR: create_policy: in create Arupa type Policy - Name Already Exists")
        elif policy_dict["type"] == POLICY_TYPE.FRISCO:
            self.policies_Frisco[policy_id] = policy_obj
            self.policies_all_ids_types_and_names[policy_id] = (POLICY_TYPE.FRISCO, policy_dict["name"])

        # creates the result json dumps of the policy identifier and returns it
        res_str = json.dumps({"policy_id": policy_id})
        return res_str

    def read_policy(self, json_identifier: str) -> str:

        # Validate the data against the schema
        try:
            policy_identifier = json.loads(json_identifier)
            validate(instance=policy_identifier, schema=json_identifier_schema)
            # print("Validation successful!")
        except jsonschema.exceptions.ValidationError as e:
            raise e
        except Exception as e:
            raise e

        res_policy_obj = None

        if policy_identifier["policy_id"] in self.policies_all_ids_types_and_names:

            if self.policies_all_ids_types_and_names[policy_identifier["policy_id"]][0] == POLICY_TYPE.ARUPA:
                res_policy_obj = self.policies_Arupa[
                    self.policies_all_ids_types_and_names[policy_identifier["policy_id"]][1]]

            elif self.policies_all_ids_types_and_names[policy_identifier["policy_id"]][0] == POLICY_TYPE.FRISCO:
                res_policy_obj = self.policies_Frisco[policy_identifier["policy_id"]]

            try:
                res = json.dumps(res_policy_obj.get_policy_dict())
                return res
            except Exception as e:
                raise e

        else:
            raise Exception("ERROR: read_policy: Policy ID not found")

    # accepts an existing json_identifier, update the existing policy with the json_input fields.
    def update_policy(self, json_identifier: str, json_input: str) -> None:
        # Validate the data against the schema
        try:
            policy_identifier = json.loads(json_identifier)
            validate(instance=policy_identifier, schema=json_identifier_schema)
            policy_dict_to_update = json.loads(json_input)
            validate(instance=policy_dict_to_update, schema=policy_schema)
            # print("Validation successful!")
        except jsonschema.exceptions.ValidationError as e:
            raise e
        except Exception as e:
            raise e

        res_policy_obj = None

        if policy_identifier["policy_id"] in self.policies_all_ids_types_and_names:

            if self.policies_all_ids_types_and_names[policy_identifier["policy_id"]][0] == POLICY_TYPE.ARUPA:
                res_policy_obj = self.policies_Arupa[
                    self.policies_all_ids_types_and_names[policy_identifier["policy_id"]][1]]

            elif self.policies_all_ids_types_and_names[policy_identifier["policy_id"]][0] == POLICY_TYPE.FRISCO:
                res_policy_obj = self.policies_Frisco[policy_identifier["policy_id"]]

            # if type is changed from FRISCO to ARUPA - check the name is not duplicated.
            if res_policy_obj.type == POLICY_TYPE.FRISCO and policy_dict_to_update["type"] == POLICY_TYPE.ARUPA:
                if policy_dict_to_update["name"] not in self.policies_Arupa:
                    self.policies_all_ids_types_and_names[policy_identifier["policy_id"]] = (
                        policy_identifier["policy_id"], POLICY_TYPE.ARUPA)
                    self.policies_Frisco.pop(policy_identifier["policy_id"])
                    self.policies_Arupa[policy_identifier["policy_id"]] = res_policy_obj
                else:
                    raise Exception("ERROR: update_policy: in update Arupa type Policy - Name Already Exists")

            if res_policy_obj.type == POLICY_TYPE.ARUPA and policy_dict_to_update["type"] == POLICY_TYPE.FRISCO:
                self.policies_all_ids_types_and_names[policy_identifier["policy_id"]] = (
                    policy_identifier["policy_id"], POLICY_TYPE.FRISCO)
                self.policies_Arupa.pop(policy_identifier["policy_id"])
                self.policies_Frisco[policy_identifier["policy_id"]] = res_policy_obj

            res_policy_obj.name = policy_dict_to_update["name"]
            res_policy_obj.description = policy_dict_to_update["description"]
            res_policy_obj.type = policy_dict_to_update["type"]

            return None

        else:
            raise Exception("ERROR: update_policy: Policy ID not found")

    def delete_policy(self, json_identifier: str) -> None:
        # Validate the data against the schema
        try:
            policy_identifier = json.loads(json_identifier)
            validate(instance=policy_identifier, schema=json_identifier_schema)
            # print("Validation successful!")
        except jsonschema.exceptions.ValidationError as e:
            raise e
        except Exception as e:
            raise e

        if policy_identifier["policy_id"] in self.policies_all_ids_types_and_names:

            if self.policies_all_ids_types_and_names[policy_identifier["policy_id"]][0] == POLICY_TYPE.ARUPA:
                self.policies_Arupa.pop(self.policies_all_ids_types_and_names[policy_identifier["policy_id"]][1])

            elif self.policies_all_ids_types_and_names[policy_identifier["policy_id"]][0] == POLICY_TYPE.FRISCO:
                self.policies_Frisco.pop(policy_identifier["policy_id"])

            self.policies_all_ids_types_and_names.pop(policy_identifier["policy_id"])

            return None

        else:
            raise Exception("ERROR: read_policy: Policy ID not found")

    def list_policies(self) -> str:

        all_policies = []

        for key in self.policies_Arupa:
            all_policies.append(self.policies_Arupa[key].get_policy_dict())

        for key in self.policies_Frisco:
            all_policies.append(self.policies_Frisco[key].get_policy_dict())

        return json.dumps(all_policies)
