import json

import pytest
from stage1 import PolicyAPI


@pytest.fixture
def api():
    return PolicyAPI()


@pytest.fixture
def foo_policy_identifier(api):
    return api.create_policy(
        json.dumps(
            {
                "name": "foo",
                "description": "my foo policy",
                "type": "Arupa",
            }
        )
    )


@pytest.fixture
def bar_policy_identifier(api):
    return api.create_policy(
        json.dumps(
            {
                "name": "bar",
                "description": "my bar policy",
                "type": "Arupa",
            }
        )
    )


class TestCreatePolicy:
    def test_empty_input(self, api):
        with pytest.raises(Exception):
            api.create_policy("")

    def test_malformed_json_input(self, api):
        with pytest.raises(Exception):
            api.create_policy("{foo")

    def test_returns_valid_json(self, api):
        policy_json = api.create_policy(
            json.dumps({"name": "foo", "description": "my foo policy", "type": "Arupa"})
        )
        assert isinstance(policy_json, str)
        json.loads(policy_json)

    def test_missing_field(self, api):
        with pytest.raises(Exception):
            api.create_policy(json.dumps({"name": "foo"}))

    @pytest.mark.parametrize(
        "invalid_name",
        [
            None,
            {"foo": "bar"},
            ["foo"],
            "foo bar",
            "foo!",
            "toolong" * 10,
        ],
    )
    def test_name_validation(self, api, invalid_name):
        with pytest.raises(Exception):
            api.create_policy(
                json.dumps(
                    {
                        "name": invalid_name,
                        "description": "my foo policy",
                    }
                )
            )

    def test_type_validation(self, api):
        with pytest.raises(Exception):
            api.create_policy(
                json.dumps(
                    {
                        "name": "foo",
                        "description": "my foo policy",
                        "type": "invalid",
                    }
                )
            )

    def test_name_must_be_unique_for_arupa_policies(self, api, foo_policy_identifier):
        with pytest.raises(Exception):
            api.create_policy(
                json.dumps(
                    {
                        "name": "foo",
                        "description": "another foo policy",
                        "type": "Arupa",
                    }
                )
            )

    def test_name_can_be_duplicated_for_frisco_policies(self, api):
        first_foo_policy_json = api.create_policy(
            json.dumps(
                {
                    "name": "foo",
                    "description": "my foo policy",
                    "type": "Frisco",
                }
            )
        )
        another_foo_policy_json = api.create_policy(
            json.dumps(
                {
                    "name": "foo",
                    "description": "another foo policy",
                    "type": "Frisco",
                }
            )
        )
        first_foo_policy_identifier = json.loads(first_foo_policy_json)
        another_foo_policy_identifier = json.loads(another_foo_policy_json)
        assert first_foo_policy_identifier != another_foo_policy_identifier


class TestReadPolicy:
    def test_invalid_or_nonexistent_identifier(self, api):
        with pytest.raises(Exception):
            api.read_policy(json.dumps("invalid"))

    def test_consistent_response_for_same_policy(self, api, foo_policy_identifier):
        assert api.read_policy(foo_policy_identifier) == api.read_policy(
            foo_policy_identifier
        )

    def test_different_response_for_different_policies(
        self, api, foo_policy_identifier, bar_policy_identifier
    ):
        assert api.read_policy(foo_policy_identifier) != api.read_policy(
            bar_policy_identifier
        )

    def test_returns_valid_json(self, api, foo_policy_identifier):
        json.loads(api.read_policy(foo_policy_identifier))

    def test_returns_dict_with_fields(self, api, foo_policy_identifier):
        policy = json.loads(api.read_policy(foo_policy_identifier))
        assert isinstance(policy, dict)
        assert policy["name"] == "foo"
        assert policy["description"] == "my foo policy"
        assert policy["type"] == "Arupa"


class TestUpdatePolicy:
    def test_invalid_or_nonexistent_identifier(self, api):
        with pytest.raises(Exception):
            api.update_policy(
                json.dumps("invalid"),
                json.dumps(
                    {
                        "name": "foo",
                        "description": "my foo policy",
                        "type": "Arupa",
                    }
                ),
            )

    def test_invalid_fields(self, api, foo_policy_identifier):
        with pytest.raises(Exception):
            api.update_policy(
                foo_policy_identifier,
                json.dumps(
                    {
                        "name": "bar",
                        "description": "my foo policy",
                        "type": "invalid",
                    }
                ),
            )

    def test_update_description(self, api, foo_policy_identifier):
        api.update_policy(
            foo_policy_identifier,
            json.dumps(
                {
                    "name": "foo",
                    "description": "my bar policy",
                    "type": "Arupa",
                }
            ),
        )
        updated_policy = json.loads(api.read_policy(foo_policy_identifier))
        assert updated_policy["name"] == "foo"
        assert updated_policy["description"] == "my bar policy"
        assert updated_policy["type"] == "Arupa"

    def test_failed_update_is_idempotent(self, api, foo_policy_identifier):
        foo_policy = api.read_policy(foo_policy_identifier)
        with pytest.raises(Exception):
            api.update_policy(
                foo_policy_identifier,
                json.dumps(
                    {
                        "name": "foo",
                        "description": "my foo policy",
                        "type": "invalid",
                    }
                ),
            )
        assert api.read_policy(foo_policy_identifier) == foo_policy


class TestDeletePolicy:
    def test_no_read_or_update_after_delete(self, api, foo_policy_identifier):
        api.read_policy(foo_policy_identifier)
        api.delete_policy(foo_policy_identifier)
        with pytest.raises(Exception):
            api.read_policy(foo_policy_identifier)
        with pytest.raises(Exception):
            api.update_policy(
                foo_policy_identifier,
                json.dumps(
                    {
                        "name": "bar",
                        "description": "my foo policy",
                        "type": "Arupa",
                    }
                ),
            )


class TestListPolicies:
    def test_returns_json(self, api):
        policies_json = api.list_policies()
        assert isinstance(policies_json, str)
        json.loads(policies_json)

    def test_returns_json_list(self, api):
        policies_json = api.list_policies()
        policies = json.loads(policies_json)
        assert isinstance(policies, list)

    def test_returns_empty_list(self, api):
        policies = json.loads(api.list_policies())
        assert len(policies) == 0

    def test_list_one(self, api, foo_policy_identifier):
        policies = json.loads(api.list_policies())
        assert len(policies) == 1
        [policy] = policies
        assert isinstance(policy, dict)
        assert policy["name"] == "foo"
        assert policy["description"] == "my foo policy"
        assert policy["type"] == "Arupa"

    def test_list_multiple(self, api, foo_policy_identifier, bar_policy_identifier):
        assert len(json.loads(api.list_policies())) == 2

    def test_failed_policy_creation_is_idempotent(self, api, foo_policy_identifier):
        first_response = api.list_policies()
        with pytest.raises(Exception):
            api.create_policy(
                json.dumps(
                    {
                        "name": "foo",
                        "description": "another foo policy",
                        "type": "Arupa",
                    }
                )
            )
        with pytest.raises(Exception):
            api.create_policy(
                json.dumps(
                    {
                        "name": "invalid!",
                        "description": "another foo policy",
                        "type": "Arupa",
                    }
                )
            )
        assert api.list_policies() == first_response
