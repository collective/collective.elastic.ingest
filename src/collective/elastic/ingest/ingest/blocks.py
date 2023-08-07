def enrichWithBlocksPlainText(content):
    content["blocks_plaintext"] = content["@components"]["collectiveelastic"][
        "blocks_plaintext"
    ]
    return content
