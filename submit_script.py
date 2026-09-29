from tools.submit import submit

submit(
    branch_name="jules-17673150229019911014-669dd531",
    commit_message="Add tests for _build_parser in geoai_cli",
    title="Add tests for _build_parser in geoai_cli",
    description="This PR adds unit tests for `geoai_cli.py` to ensure that `_build_parser()` returns an `ArgumentParser` object and that its help string contains known subcommands like `list-tools` and `chat`."
)
