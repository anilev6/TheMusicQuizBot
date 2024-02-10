def escape_markdown_v2(text):
    if type(text) != str:
        text = str(text)
    text = text.replace("\\", "\\\\")
    characters = [
        "_",
        "*",
        "[",
        "]",
        "(",
        ")",
        "~",
        "`",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]
    for char in characters:
        text = text.replace(char, "\\" + char)
    return text


def victoryna_to_text(context, victoryna_index: int) -> str:
    result = "None"
    all_victorynas = context.user_data.get("victorynas")
    if all_victorynas:
        victoryna = all_victorynas[victoryna_index]
        title = "*" + escape_markdown_v2(victoryna.get("title", "kek")) + "*"
        description = (
            "_" + escape_markdown_v2(victoryna.get("description", "kek")) + "_"
        )
        audios = "\n\n".join(
            [
                escape_markdown_v2(f"{n}. " + i.get("description"))
                for n, i in enumerate(victoryna.get("audios"), start=1)
            ]
        )
        result = "\n\n".join([title, description, audios])
    return result


def victoryna_student_results_to_text(res: dict):
    return "\n\n".join(
        [
            f"*{escape_markdown_v2(k)}* :\n_{escape_markdown_v2(v)}_"
            for k, v in res.items()
        ]
    )


def append_to_front(element, ar1: list, limit=100) -> list:
    ar1 = [element] + ar1[: limit - 1]
    return ar1


def join_dictionaries(*dicts):
    joined_dict = {}
    for dictionary in dicts:
        joined_dict.update(dictionary)
    return joined_dict
