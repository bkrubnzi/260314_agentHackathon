#!/usr/bin/env bash
# hackathon-setup.sh
# Creates the IAM user and Bedrock policy for hackathon participants.
# Idempotent — safe to run multiple times, skips resources that already exist.

set -euo pipefail

ACCOUNT_ID="[ACCOUNT_ID]"
POLICY_NAME="hackathon-bedrock-haiku"
POLICY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/${POLICY_NAME}"
USERNAME="hackathon-participant"
REGION="us-west-2"
MODEL_ID="us.anthropic.claude-haiku-4-5-20251001-v1:0"

echo "==> Writing policy document..."
cat > /tmp/hackathon-bedrock-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-haiku*",
        "arn:aws:bedrock:us-west-2:382136844917:inference-profile/us.anthropic.claude-haiku*"
      ]
    }
  ]
}
EOF

echo "==> Creating IAM policy..."
if aws iam get-policy --policy-arn "$POLICY_ARN" &>/dev/null; then
  echo "    Policy already exists. Skipping."
else
  aws iam create-policy \
    --policy-name "$POLICY_NAME" \
    --policy-document file:///tmp/hackathon-bedrock-policy.json
  echo "    Policy created."
fi

echo "==> Creating IAM user..."
if aws iam get-user --user-name "$USERNAME" &>/dev/null; then
  echo "    User already exists. Skipping."
else
  aws iam create-user --user-name "$USERNAME"
  echo "    User created."
fi

echo "==> Attaching policy to user..."
if aws iam list-attached-user-policies --user-name "$USERNAME" \
    --query "AttachedPolicies[?PolicyArn=='$POLICY_ARN']" \
    --output text | grep -q "$POLICY_ARN"; then
  echo "    Policy already attached. Skipping."
else
  aws iam attach-user-policy \
    --user-name "$USERNAME" \
    --policy-arn "$POLICY_ARN"
  echo "    Policy attached."
fi

echo "==> Creating access key..."
KEY_COUNT=$(aws iam list-access-keys --user-name "$USERNAME" \
  --query 'length(AccessKeyMetadata)' --output text)
if [ "$KEY_COUNT" -gt "0" ]; then
  echo "    Access key already exists. Skipping creation."
  echo "    To view existing key IDs: aws iam list-access-keys --user-name $USERNAME"
else
  aws iam create-access-key --user-name "$USERNAME" > access-key.json
  cat access-key.json
fi

echo ""
echo "==> Running test invoke..."
echo "    (Requires AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to be set)"
if [ -n "${AWS_ACCESS_KEY_ID:-}" ] && [ -n "${AWS_SECRET_ACCESS_KEY:-}" ]; then
  aws bedrock-runtime invoke-model \
    --region "$REGION" \
    --model-id "$MODEL_ID" \
    --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":64,"messages":[{"role":"user","content":"Say hello in one sentence."}]}' \
    --cli-binary-format raw-in-base64-out \
    /tmp/bedrock-test.json && cat /tmp/bedrock-test.json
  echo ""
  echo "    Test passed."
else
  echo "    Skipping test — participant creds not set in environment."
  echo "    To test manually:"
  echo "      AWS_ACCESS_KEY_ID=<key> AWS_SECRET_ACCESS_KEY=<secret> \\"
  echo "      aws bedrock-runtime invoke-model \\"
  echo "        --region $REGION \\"
  echo "        --model-id $MODEL_ID \\"
  echo "        --body '{\"anthropic_version\":\"bedrock-2023-05-31\",\"max_tokens\":64,\"messages\":[{\"role\":\"user\",\"content\":\"Say hello in one sentence.\"}]}' \\"
  echo "        --cli-binary-format raw-in-base64-out /tmp/test.json && cat /tmp/test.json"
fi

echo ""
echo "Setup complete."
echo ""
echo "Participant env vars:"
echo "  export AWS_ACCESS_KEY_ID=<key>"
echo "  export AWS_SECRET_ACCESS_KEY=<secret>"
echo "  export AWS_DEFAULT_REGION=$REGION"
echo "  Model ID: $MODEL_ID"
