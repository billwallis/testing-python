import json

from github_reports import utils


def test__repr_encoder_can_encode_objects():
    class Foo:
        def __repr__(self) -> str:
            return "awh yeah"

    jsn = json.dumps(
        {"foo": Foo()},
        cls=utils.ReprEncoder,
    )

    assert jsn == '{"foo": "awh yeah"}'
