#!/usr/bin/env python3
"""Check Bedrock spending on AWS"""

import subprocess
import json
from datetime import datetime, timedelta

def get_bedrock_spend():
    """Query AWS Cost Explorer for Bedrock spending"""

    # Set date range: start of month to today
    today = datetime.now()
    start_of_month = today.replace(day=1).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")

    # AWS CLI command
    cmd = [
        "aws", "ce", "get-cost-and-usage",
        "--time-period", f"Start={start_of_month},End={end_date}",
        "--granularity", "DAILY",
        "--metrics", "BlendedCost",
        "--filter", json.dumps({
            "Dimensions": {
                "Key": "SERVICE",
                "Values": ["Amazon Bedrock"]
            }
        })
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        # Calculate total
        total = 0.0
        for period in data["ResultsByTime"]:
            amount = float(period["Total"]["BlendedCost"]["Amount"])
            total += amount

        print(f"📊 Bedrock Spending ({start_of_month} to {end_date})")
        print(f"💰 Total: ${total:.2f}")

        if total == 0:
            print("✅ No charges yet!")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
    except json.JSONDecodeError:
        print("❌ Failed to parse AWS response")

if __name__ == "__main__":
    get_bedrock_spend()
