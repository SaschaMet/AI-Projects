"""
title: Search Order
author: Sascha Metzger
description: This tool can create an email.
version: 0.0.1
"""

import asyncio
import requests
import logging

logging.basicConfig(level=logging.DEBUG)


class Tools:
    def __init__(self):
        self.api_url = "http://host.docker.internal:5678/webhook/93334314-b925-4569-8127-728442bbd3b2"

    async def create_email(
        self,
        email: str,
        subject: str,
        message: str,
        __event_emitter__=None,
    ) -> dict:
        """
        Create an email with an email address, subject and message.
        Address the recipient on a personal level (treat them as a friend) and use a friendly tone. Keep the message short and to the point. Include all the necessary details while keeping it concise.

        :type string: The email to search for.
        :rtype: string: The order details.
        """

        payload = {
            "message": {
                "recipient": email,
                "subject": subject,
                "message": message,
            }
        }

        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Creating message for {email}",
                        "done": False,
                    },
                }
            )

            await asyncio.sleep(2)

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            response = response.json()

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": "Message created successfully.",
                            "done": True,
                        },
                    }
                )

                await asyncio.sleep(2)

            return "Message sent successfully."
        except requests.RequestException as e:
            error_message = f"Error sending message: {str(e)}"
            logging.debug(f"Error message:\n{error_message}")

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "error",
                        "data": {"description": error_message, "done": True},
                    }
                )

            raise Exception(error_message)
