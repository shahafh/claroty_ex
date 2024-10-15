class PolicyAPI:
    def __init__(self) -> None:
        pass

    def create_policy(self, json_input: str) -> str:
        raise NotImplementedError

    def read_policy(self, json_identifier: str) -> str:
        raise NotImplementedError

    def update_policy(self, json_identifier: str, json_input: str) -> None:
        raise NotImplementedError

    def delete_policy(self, json_identifier: str) -> None:
        raise NotImplementedError

    def list_policies(self) -> str:
        raise NotImplementedError

    def create_rule(self, json_policy_identifier: str, json_rule_input: str) -> str:
        raise NotImplementedError

    def read_rule(self, json_identifier: str) -> str:
        raise NotImplementedError

    def update_rule(self, json_identifier: str, json_rule_input: str) -> None:
        raise NotImplementedError

    def delete_rule(self, json_identifier: str) -> None:
        raise NotImplementedError

    def list_rules(self, json_policy_identifier: str) -> str:
        raise NotImplementedError
