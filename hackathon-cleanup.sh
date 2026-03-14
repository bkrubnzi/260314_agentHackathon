#!/usr/bin/env bash
# hackathon-cleanup.sh
# Removes all AWS resources created for the hackathon.
# Idempotent — safe to run multiple times.

set -euo pipefail

POLICY_ARN="arn:aws:iam::382136844917:policy/hackathon-bedrock-haiku"
USERNAME="hackathon-participant"

echo "==> Detaching policy from user..."
if aws iam list-attached-user-policies --user-name "$USERNAME" \
    --query "AttachedPolicies[?PolicyArn=='$POLICY_ARN']" \
    --output text 2>/dev/null | grep -q "$POLICY_ARN"; then
  aws iam detach-user-policy \
    --user-name "$USERNAME" \
    --policy-arn "$POLICY_ARN"
  echo "    Policy detached."
else
  echo "    Policy already detached or user doesn't exist. Skipping."
fi

echo "==> Deleting access keys for user..."
KEYS=$(aws iam list-access-keys --user-name "$USERNAME" \
  --query 'AccessKeyMetadata[].AccessKeyId' \
  --output text 2>/dev/null || true)
if [ -n "$KEYS" ]; then
  for KEY in $KEYS; do
    aws iam delete-access-key --user-name "$USERNAME" --access-key-id "$KEY"
    echo "    Deleted access key: $KEY"
  done
else
  echo "    No access keys found. Skipping."
fi

echo "==> Deleting IAM user..."
if aws iam get-user --user-name "$USERNAME" &>/dev/null; then
  aws iam delete-user --user-name "$USERNAME"
  echo "    User '$USERNAME' deleted."
else
  echo "    User '$USERNAME' does not exist. Skipping."
fi

echo "==> Deleting non-default policy versions..."
VERSIONS=$(aws iam list-policy-versions --policy-arn "$POLICY_ARN" \
  --query 'Versions[?IsDefaultVersion==`false`].VersionId' \
  --output text 2>/dev/null || true)
if [ -n "$VERSIONS" ]; then
  for VER in $VERSIONS; do
    aws iam delete-policy-version --policy-arn "$POLICY_ARN" --version-id "$VER"
    echo "    Deleted policy version: $VER"
  done
else
  echo "    No non-default policy versions to delete. Skipping."
fi

echo "==> Deleting IAM policy..."
if aws iam get-policy --policy-arn "$POLICY_ARN" &>/dev/null; then
  aws iam delete-policy --policy-arn "$POLICY_ARN"
  echo "    Policy deleted."
else
  echo "    Policy does not exist. Skipping."
fi

echo ""
echo "Cleanup complete."
