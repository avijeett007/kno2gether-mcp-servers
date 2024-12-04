import asyncio
import logging
import sys
from datetime import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pydantic import AnyUrl

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('calendar_server_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('calendar_server')

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarServer(Server):
    def __init__(self, name: str):
        super().__init__(name)
        self.service = None
        logger.info(f"Initializing CalendarServer with name: {name}")
        
    async def initialize(self):
        """Initialize the Google Calendar API service."""
        logger.info("Starting Google Calendar API service initialization")
        try:
            if self.service:  # If service exists, reuse it
                return

            import os.path
            import pickle

            creds = None
            token_file = 'token.pickle'
            
            # Load existing credentials if available
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)

            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                # Save credentials
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)

            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("Successfully initialized Google Calendar API service")
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar API service: {str(e)}")
            raise

server = CalendarServer("googleCalendar")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available calendar management tools."""
    logger.info("Handling list_tools request")
    tools = [
        types.Tool(
            name="create-event",
            description="Create a new calendar event. Times must be in ISO 8601 format with UTC timezone (e.g., '2024-12-04T10:00:00Z')",
            inputSchema={
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Title of the event"},
                    "description": {"type": "string", "description": "Event description"},
                    "start_time": {
                        "type": "string", 
                        "format": "date-time", 
                        "description": "Start time in ISO 8601 format with UTC timezone (e.g., '2024-12-04T10:00:00Z')"
                    },
                    "end_time": {
                        "type": "string", 
                        "format": "date-time", 
                        "description": "End time in ISO 8601 format with UTC timezone (e.g., '2024-12-04T11:00:00Z')"
                    },
                    "attendees": {
                        "type": "array",
                        "items": {"type": "string", "format": "email"},
                        "description": "List of attendee email addresses"
                    }
                },
                "required": ["summary", "start_time", "end_time"],
            },
        ),
        types.Tool(
            name="search-events",
            description="Search for calendar events. Time range must be specified in ISO 8601 format with UTC timezone",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_min": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Start time in ISO 8601 format (e.g., '2024-12-04T00:00:00Z')"
                    },
                    "time_max": {
                        "type": "string",
                        "format": "date-time",
                        "description": "End time in ISO 8601 format (e.g., '2024-12-04T23:59:59Z')"
                    },
                    "query": {
                        "type": "string",
                        "description": "Optional search term"
                    }
                },
                "required": ["time_min", "time_max"],
            },
        ),
    ]
    logger.info(f"Returning {len(tools)} tools")
    return tools

@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle calendar tool execution requests."""
    logger.info(f"Handling tool call: {name} with arguments: {arguments}")
    
    if not server.service:
        logger.info("Service not initialized, initializing now...")
        await server.initialize()

    if not arguments:
        logger.error("Missing arguments for tool call")
        raise ValueError("Missing arguments")

    try:
        if name == "create-event":
            logger.info("Creating new calendar event")
            event = {
                'summary': arguments['summary'],
                'description': arguments.get('description', ''),
                'start': {'dateTime': arguments['start_time']},
                'end': {'dateTime': arguments['end_time']},
            }
            
            if 'attendees' in arguments and arguments['attendees']:
                event['attendees'] = [{'email': email} for email in arguments['attendees']]
            
            created_event = server.service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Successfully created event with ID: {created_event['id']}")
            return [
                types.TextContent(
                    type="text",
                    text=f"Created event: {created_event['summary']}\n"
                         f"Start: {created_event['start']['dateTime']}\n"
                         f"End: {created_event['end']['dateTime']}\n"
                         f"ID: {created_event['id']}"
                )
            ]

        elif name == "search-events":
            logger.info("Searching for events")
            events_result = server.service.events().list(
                calendarId='primary',
                timeMin=arguments['time_min'],
                timeMax=arguments['time_max'],
                q=arguments.get('query', ''),
                maxResults=10,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            logger.info(f"Found {len(events)} events")
            
            if not events:
                return [types.TextContent(type="text", text="No events found")]
            
            event_list = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                event_list.append(
                    f"- {event.get('summary', 'Untitled')}\n"
                    f"  Start: {start}\n"
                    f"  End: {end}"
                )
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Found {len(events)} events:\n\n" + "\n\n".join(event_list)
                )
            ]

    except Exception as e:
        logger.error(f"Error in tool execution: {str(e)}")
        raise

    logger.error(f"Unknown tool: {name}")
    raise ValueError(f"Unknown tool: {name}")

async def main():
    logger.info("Starting calendar server")
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("Successfully created stdio server")
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="googleCalendar",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except Exception as e:
        logger.error(f"Error running server: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting main execution")
    asyncio.run(main())