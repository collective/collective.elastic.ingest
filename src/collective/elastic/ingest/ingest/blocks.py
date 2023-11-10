def enrichWithBlocksPlainText(content):
    cce = content["@components"]["collectiveelastic"]
    if "blocks_plaintext" in cce:
        content["blocks_plaintext"] = cce["blocks_plaintext"]
    return content
