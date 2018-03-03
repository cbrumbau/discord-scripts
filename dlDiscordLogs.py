#!/usr/bin/env python3

import argparse, datetime, re, sys
import discord

def str_date(s):
	try:
		return datetime.datetime.strptime(s, "%m-%d-%Y")
	except ValueError:
		msg = "Not a valid date: '{0}'.".format(s)
		raise argparse.ArgumentTypeError(msg)

parser = argparse.ArgumentParser()
parser.add_argument('token', action='store', help='OAuth2 token needed to communicate with Discord.')
parser.add_argument('channel', action='store', help='Channel id needed to access messages. Use developer mode to acquire the desired channel id.')
parser.add_argument('-o', '--output', action='store', default=None, help='Output text file to write message logs to, otherwise writes to stdout.')
parser.add_argument('-l', '--limit', action='store', default=sys.maxsize, type=int, help='Number of messages to retrieve. Default: max int')
parser.add_argument('-b', '--before', action='store', default=None, type=str_date, help='The date before which all returned messages must be. The date provided must be formatted MM-DD-YYYY.')
parser.add_argument('-a', '--after', action='store', default=None, type=str_date, help='The date after which all returned messages must be. The date provided must be formatted MM-DD-YYYY.')
parser.add_argument('-r', '--around', action='store', default=None, type=str_date, help='The date around which all returned messages must be. The date provided must be formatted MM-DD-YYYY.')
args = parser.parse_args()

def get_member_ids_to_names(all_messages):
	ids_to_names = dict()
	for message in all_messages:
		# Store the author
		ids_to_names[message.author.id] = message.author.name
		# Store the mentions
		if len(message.mentions):
			for member in message.mentions:
				ids_to_names[member.id] = member.name
	return ids_to_names

def format_message(message, members_dict):
	content = ""
	# Find and replace any mention ids in content with names
	if len(message.channel_mentions) or len(message.role_mentions):
		content = message.content
		if len(message.channel_mentions):
			for channel in message.channel_mentions:
				content = content.replace("<#"+channel.id+">", "<#"+channel.name+">")
		if len(message.role_mentions):
			for role in message.role_mentions:
				content = content.replace("<@"+role.id+">", "<@"+role.name+">")
	else:
		content = message.content
	# Use all known members to replace any user mentions in case people left server but have posted
	# Special characters like ! can be placed before ids (not sure why) so have to use regex
	for id in list(members_dict.keys()):
		reid = re.compile('<@.?'+id+'>')
		content = reid.sub('<@'+members_dict[id]+'>', content)
	# Return timestamp, user, any content, and any attachments
	if len(message.attachments):
		if len(message.content):
			return message.timestamp.strftime("%m/%d/%Y %H:%M:%S")+"\t"+message.author.name+"\t"+content+"\t"+",".join(attach['url'] for attach in message.attachments)
		else:
			return message.timestamp.strftime("%m/%d/%Y %H:%M:%S")+"\t"+message.author.name+"\t"+",".join(attach['url'] for attach in message.attachments)
	else:
		return message.timestamp.strftime("%m/%d/%Y %H:%M:%S")+"\t"+message.author.name+"\t"+content

client = discord.Client()

@client.event
async def on_ready():
	sys.stderr.write("Downloading messages from requested channel...\n")
	channel = client.get_channel(args.channel)
	logs = client.logs_from(channel, limit=args.limit, before=args.before, after=args.after, around=args.around)
	message_list = list()
	async for message in logs:
		message_list.append(message)
	members_dict = get_member_ids_to_names(message_list)
	# Sort message list by datetime
	message_list.sort(key=lambda x: x.timestamp)
	if args.output:
		log_file = open(args.output, 'w', encoding='UTF-8')
		for message in message_list:
			log_file.write(format_message(message, members_dict)+"\n")
		log_file.close()
	else:
		for message in message_list:
			print(format_message(message, members_dict))
	sys.stderr.write("Closing client...\n")
	await client.close()
	sys.stderr.write("Logging out from Discord...\n")
	await client.logout()
	sys.stderr.write("Finished.\n")

sys.stderr.write("Logging into Discord...\n")
client.run(args.token)