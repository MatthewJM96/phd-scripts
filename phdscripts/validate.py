from typing import Set


def validate_required_keys(
    required_keys: Set[str], provided_keys: Set[str], indent: int = 0
) -> bool:
    indent_str = " " * indent

    if required_keys > provided_keys:
        print(
            (
                f"{indent_str}Parameters provided do not at least include the required"
                "parameters.\n"
                f"{indent_str}    Parameters provided were: {provided_keys}\n"
                f"{indent_str}    Parameters required are: {required_keys}\n"
            )
        )
        return False
    return True
