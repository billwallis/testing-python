import pathlib

import yaml

HERE = pathlib.Path(__file__).parent


def main() -> None:
    raw_content = (HERE / "ahoy.yaml").read_text(encoding="utf-8")
    # raw_content = (HERE / "real-example.yaml").read_text(encoding="utf-8")
    contents = yaml.safe_load_all(raw_content)
    for document in contents:
        for item in document.items():
            print(42 * "-", "\n", item, sep="")
            print(item[1])


if __name__ == "__main__":
    main()
