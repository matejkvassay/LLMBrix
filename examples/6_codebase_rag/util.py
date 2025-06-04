from .data_model import ScriptBlock


def walk_blocks(self) -> list[ScriptBlock]:
    result = []
    for block in self.blocks:
        result.append(block)
        if hasattr(block.content, "body"):
            result.extend(block.content.body)
    return result
