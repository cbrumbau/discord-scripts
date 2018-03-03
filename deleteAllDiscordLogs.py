#!/usr/bin/env python3

import argparse, sys
import discord

parser = argparse.ArgumentParser()
parser.add_argument('token', action='store', help='OAuth2 token needed to communicate with Discord.')
parser.add_argument('channel', action='store', help='Channel id needed to access messages. Use developer mode to acquire the desired channel id.')
args = parser.parse_args()

client = discord.Client()

@client.event
async def on_ready():
	sys.stderr.write("Deleting all messages from requested channel...\n")
	channel = client.get_channel(args.channel)
	logs = client.logs_from(channel, limit=sys.maxsize)
	message_list = list()
	async for message in logs:
		message_list.append(message)
	for message in message_list:
		await client.delete_message(message)
	sys.stderr.write("Closing client...\n")
	await client.close()
	sys.stderr.write("Logging out from Discord...\n")
	await client.logout()
	sys.stderr.write("Finished.\n")

sys.stderr.write("Logging into Discord...\n")
client.run(args.token)