import boto3
import json

# Why we specify the profile: this tells boto3 to use the
# 'migrateiq' credentials we configured earlier (least-privilege
# IAM user), not any other AWS account that might exist on this machine.
session = boto3.Session(profile_name="migrateiq", region_name="ap-south-2")

# 'bedrock-runtime' is the specific client for INVOKING models
# (there's a separate 'bedrock' client for admin tasks like
# listing/configuring models — we don't need that one here).
client = session.client("bedrock-runtime")

# This is the model ID for Claude Haiku 4.5 via cross-region inference.
# The "apac." prefix routes the call through the APAC inference profile
# we confirmed is available in ap-south-2.
model_id = "global.anthropic.claude-haiku-4-5-20251001-v1:0"

# Bedrock's "Converse API" is the modern, unified way to talk to any
# model (Claude, Titan, Llama, etc.) with the same request shape —
# instead of each model having its own quirky JSON format.
response = client.converse(
    modelId=model_id,
    messages=[
        {
            "role": "user",
            "content": [{"text": "Say hello and confirm you are Claude Haiku, responding from ap-south-2."}]
        }
    ]
)

# Extract just the text reply from the response object
reply_text = response["output"]["message"]["content"][0]["text"]
print("Model replied:", reply_text)

# This is worth printing now because COST and PERFORMANCE tracking
# starts here, not later — every call reports exact token usage.
print("Token usage:", response["usage"])