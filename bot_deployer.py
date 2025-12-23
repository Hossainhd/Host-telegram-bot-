#!/usr/bin/env python3
"""
AUTO-DEPLOY BOTS TO RAILWAY
"""

import os
import requests
import json
import time
from datetime import datetime

class RailwayDeployer:
    def __init__(self):
        self.railway_token = os.getenv("RAILWAY_TOKEN")
        self.project_id = os.getenv("RAILWAY_PROJECT_ID")
        self.headers = {
            "Authorization": f"Bearer {self.railway_token}",
            "Content-Type": "application/json"
        }
    
    def create_environment(self, user_id, bot_token):
        """Create environment for user bot"""
        env_name = f"BOT_{user_id}"
        
        payload = {
            "projectId": self.project_id,
            "name": env_name,
            "value": bot_token
        }
        
        response = requests.post(
            "https://backboard.railway.app/graphql/v2",
            json={
                "query": """
                    mutation UpsertVariable($input: VariableUpsertInput!) {
                        variableUpsert(input: $input) {
                            id
                            name
                            value
                        }
                    }
                """,
                "variables": {"input": payload}
            },
            headers=self.headers
        )
        
        return response.json()
    
    def deploy_bot(self, user_id, bot_name):
        """Deploy a new bot service"""
        service_name = f"{bot_name}-{user_id}".lower().replace(" ", "-")
        
        payload = {
            "query": """
                mutation ServiceInstanceCreate($input: ServiceInstanceCreateInput!) {
                    serviceInstanceCreate(input: $input) {
                        id
                        name
                        createdAt
                    }
                }
            """,
            "variables": {
                "input": {
                    "projectId": self.project_id,
                    "name": service_name,
                    "source": {
                        "image": "python:3.11"
                    },
                    "variables": [
                        {"name": "BOT_TOKEN", "value": f"${{BOT_{user_id}}}"},
                        {"name": "OWNER_ID", "value": str(user_id)}
                    ]
                }
            }
        }
        
        response = requests.post(
            "https://backboard.railway.app/graphql/v2",
            json=payload,
            headers=self.headers
        )
        
        return response.json()

# Example usage
if __name__ == "__main__":
    deployer = RailwayDeployer()
    
    # Test deployment
    result = deployer.create_environment(123456, "test_token_here")
    print("Environment created:", result)
    
    result = deployer.deploy_bot(123456, "MyBot")
    print("Deployment started:", result)