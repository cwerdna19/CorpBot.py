import  asyncio, discord, datetime
from    datetime import timedelta
from    discord.ext import commands
from    Cogs import Settings, DisplayName, PickList
"""
TO DO:

-Search ticket by user name, user id, claimed, unclaimed, date
-Handle ticket expiration

-Move title, body max length, max server tickets, max user tickets, to serverstat
-Move ticket list to serverstat
    - Did this, but ticket object can't be stored in json

Need:
List of users with tickets open?
    Must include number of tickets opened per user
    User Stat with number of tickets opened?
    User Stat with number of tickets fixed

-Finish all methods

"""
def setup(bot):
    # Add the bot and deps
    settings = bot.get_cog("Settings")
    bot.add_cog(Tickets(bot, settings))

class Tickets(commands.Cog):
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
        global DisplayName
        DisplayName = self.bot.get_cog("DisplayName")
        self.title_length = 25
        self.body_length = 500
        self.max_user_tickets = 10
        self.max_server_tickets = 1000
        self.ticket_list = {}
    
    def display_ticket(self, ctx, ticket):
        ticket_embed = discord.Embed(color=ctx.author.color)
        ticket_embed.title = f'{ticket.owner_name}\'s Ticket'
        ticket_embed.add_field(name="Ticket Name", value=ticket.title)
        ticket_embed.add_field(name="Ticket ID", value=ticket.id)
        ticket_embed.add_field(name='\u200B', value='\u200B')
        ticket_embed.add_field(name="Ticket Content", value=ticket.body, inline=True)
        ticket_embed.add_field(name='\u200B', value='\u200B')
        ticket_embed.add_field(name='\u200B', value='\u200B')
        ticket_embed.add_field(name='Created on', value=ticket.date_made)
        ticket_embed.add_field(name='Expires on', value=ticket.expires_on)
        
        return ticket_embed

    class Ticket:
        """Ticket object constructor. Ticket objets are made in the process_new_ticket() method"""
        def __init__(self, title, body, owner, date, id):
            expiry_days = timedelta(days=7)
            self.title = title
            self.body = body
            self.owner_id = owner.id
            self.owner_name = owner
            self.claimed_by = None
            self.date_made = date
            self.expires_on = date + expiry_days
            self.id = id
    
    @commands.command()
    async def newticket(self, ctx):
        """Create a new ticket and add it to the ticket list"""

        def add_ticket(ticket):
            """Make a ticket list if one doesn't exist for a server
                Append the ticket object to the list."""
            server_ticket_list = self.settings.getServerStat(ctx.guild, "TicketList")
            if server_ticket_list is None:
                self.settings.setServerStat(ctx.guild, "TicketList", [])
                server_ticket_list = self.settings.getServerStat(ctx.guild, "TicketList")
            server_ticket_list.append(ticket)
            self.settings.setServerStat(ctx.guild, "TicketList", server_ticket_list)

        def is_author(m):
            """Return true if the message author is the user entered the command"""
            return m.author == ctx.message.author

        async def check_response():
            """"""
            return await self.bot.wait_for('message', check=is_author, timeout=30)

        async def get_ticket_item(intro, num):
            """Get ticket info from user
                `intro` is the message introducing the type of information requested.
                `num` is the maximum number of characters the user's message may contain."""
            await ctx.channel.send(intro)
            item = await check_response()
            if len(item.content) <= num:
                msg = f'This is what I got: `{item.content}`\nIs this correct? (yes/no/stop)'
                await ctx.channel.send(msg)
                response = await check_response()

                if response.content.lower() == 'yes':
                    return item.content
                elif response.content.lower() == 'no':
                    await get_ticket_item(intro, num)
                elif response.content.lower() == 'stop':
                    await ctx.channel.send(f'No problem, {DisplayName.name(ctx.author)}! See you later!')
                    return None
                else:
                    await ctx.channel.send('I don\'t know what to say to that. Try making your ticket again.')
                    return None
            else:
                msg = f'Sorry, that message is too long. Try making it shorter than {num} characters.'
                await ctx.channel.send(msg)
                await get_ticket_item(intro, num)

        async def process_new_ticket():
            """Call methods to get ticket info from user.
                Create ticket object and add it to the list."""
            msg = f'Need some help, *{DisplayName.name(ctx.author)}*? Let\'s make a new ticket...\n'
            await ctx.channel.send(msg)
            
            #check max ticket stats first
            server_open_tickets = self.settings.getServerStat(ctx.guild, "OpenTickets")
            #If ServerStat OpenTickets doesn't exist, set value 0
            if server_open_tickets is None:
                self.settings.setServerStat(ctx.guild, "OpenTickets", 0)
                server_open_tickets = self.settings.getServerStat(ctx.guild, "OpenTickets")
            #If ServerStat OpenTickets exceeds max, return
            if server_open_tickets >= self.max_server_tickets:
                return await ctx.channel.send(f'Sorry! The server has reached its ticket cap. Please try again later.')
            
            user_tickets_open = self.settings.getUserStat(ctx.author, ctx.guild, "TicketsOpen")
            #If UserStat TicketsOpen doesn't exist, set value 0
            if user_tickets_open is None:
                self.settings.setUserStat(ctx.author, ctx.guild, "TicketsOpen", 0)
                user_tickets_open = self.settings.getUserStat(ctx.author, ctx.guild, "TicketsOpen")
            #If UserStat TicketsOpen exceeds max, return
            if user_tickets_open >= self.max_user_tickets:
                return await ctx.channel.send(f'Sorry! You\'ve opened too many tickets at once. Try again when you have less than {self.max_user_tickets}.')
        
            msg = 'What do you need help with? This will be the title of your ticket, '
            msg += f'so please be concise ({self.title_length} characters maximum).'

            title = await get_ticket_item(msg, self.title_length)
            if title is None:
                return

            msg = f'OK! Tell me about your problem in {self.body_length} words or less.'

            body = await get_ticket_item(msg, self.body_length)
            if body is None:
                return
            
            #Increment TicketsOpen stat by one
            self.settings.incrementStat(ctx.author, ctx.guild, "TicketsOpen", 1)
            
            #Increment OpenTickets stat by one
            self.settings.setServerStat(ctx.guild, "OpenTickets", server_open_tickets+1)
                
            server_total_tickets = self.settings.getServerStat(ctx.guild, "TotalTickets")
            #If ServerStat TotalTickets doesn't exist, set value 0
            if server_total_tickets is None:
                self.settings.setServerStat(ctx.guild, "TotalTickets", 0)
                server_total_tickets = self.settings.getServerStat(ctx.guild, "TotalTickets")
            #Increment TotalTickets stat by one
            self.settings.setServerStat(ctx.guild, "TotalTickets", server_total_tickets+1)
            server_total_tickets = self.settings.getServerStat(ctx.guild, "TotalTickets")
            
            #Create ticket object
            ticket = self.Ticket(title, body, ctx.message.author, datetime.date.today(), server_total_tickets)
            
            #Show ticket to user
            msg = f'Your ticket was added to the queue. You will be notified if someone claims your ticket.\n'
            #msg += self.display_ticket(ctx, ticket)
            await ctx.channel.send(msg, embed=self.display_ticket(ctx, ticket))
            
            
            #Add ticket to server's ticket list
            add_ticket(ticket)

        try:
            await process_new_ticket()
        except asyncio.TimeoutError:
            return await ctx.channel.send('I was waiting too long, sorry! Ask me again later if you still need help.')
    
    @commands.command()
    async def showtickets(self, ctx, id : int = None, claimed : str = None):
    #Implement PagePicker from PickList.py for when tickets returned is >10
    
        tickets = self.settings.getServerStat(ctx.guild, "TicketList")
        this_ticket = None
        ticket_list = []
        ticket_titles = []
        
        #If tickets in list
        if tickets is None or len(tickets) == 0:
            return await ctx.channel.send('Sorry, I couldn\'t find any open tickets.')
        #If ticket.id was given
        if id is not None:
            if claimed is not None:
                return await ctx.channel.send(f'Please don\'t specify an ID as well as a claimed state.')
            for ticket in tickets:
                if ticket.id == id:
                    this_ticket = ticket
            if this_ticket is None:
                return await ctx.channel.send(f'Sorry, I couldn\'t find a ticket with ID {id}.')
        #If no ticket.id was given
        elif id is None:
            #If claimed is specified
            if claimed is not None:
                #Look for claimed tickets
                if claimed == 'yes':
                    for ticket in tickets:
                        if ticket.claimed_by is not None:
                            ticket_titles.append(ticket.title)
                            ticket_list.append(ticket)
                    if ticket_titles == []:
                        return await ctx.channel.send(f'Sorry, I couldn\'t find any claimed tickets.')
                #Look for unclaimed tickets
                elif claimed == 'no':
                    for ticket in tickets:
                        if ticket.claimed_by is None:
                            ticket_titles.append(ticket.title)
                            ticket_list.append(ticket)
                    if ticket_titles == []:
                        return await ctx.channel.send(f'Sorry, I couldn\'t find any unclaimed tickets.')
            #If claimed isn't specified
            elif claimed is None:
                for ticket in tickets:
                    ticket_titles.append(ticket.title)
                    ticket_list.append(ticket)
        
        if this_ticket is None:        
            index, message = await PickList.Picker(
                title = 'Please select from the following list of tickets:',
                list = ticket_titles,
                ctx = ctx
            ).pick()
            
            if index < 0:
                await message.edit(content="Ticket search canceled.")
                return
        
        ticket_embed = self.display_ticket(ctx, ticket_list[index])
                
        if message:
            return await message.edit(content=" ", embed=ticket_embed)
        else:
            return await ctx.channel.send(embed=ticket_embed)

    @commands.command()
    async def closeticket(self, ctx, *, id : int = None, user : str = None):
        #close a ticket and give credit to whomever helped you
        #must decrement stat "OpenTickets"
        #must remove ticket object from list
        #must give credit to user specified
        tickets = self.settings.getServerStat(ctx.guild, "TicketList")
        this_ticket = None
        realname = DisplayName.memberForName(user, ctx.guild)
        
        if id is None:
            return await ctx.channel.send('Please specify a ticket ID.')
        elif tickets is None or len(tickets) == 0:
            return await ctx.channel.send('Sorry, I couldn\'t find any open tickets.')
        #We have some tickets
        else:
            for ticket in tickets:
                if ticket.id == id:
                    #Check if author has permission to close this ticket
                    if ticket.owner_id == ctx.author.id:
                        this_ticket = ticket
                        break
                    else:
                        return await ctx.channel.send('You don\'t have permission to close this ticket.')
            #We have tickets but not with that ID
            if this_ticket is None:
                return await ctx.channel.send(f'Sorry, I couldn\'t find a ticket with ID {id}.')
            
            #Decrement ServerStat OpenTickets
            server_open_tickets = self.settings.getServerStat(ctx.guild, "OpenTickets")
            self.settings.setServerStat(ctx.guild, "OpenTickets", server_open_tickets-1)
            
            #Decrement ticket owner UserStat TicketsOpen
            owner_open_tickets = self.settings.getUserStat(ctx.author, ctx.guild, "TicketsOpen")
            self.settings.setUserStat(ctx.author, ctx.guild, "TicketsOpen", owner_open_tickets-1)
            
            msg = f'Ticket **{this_ticket.id}** has been removed. '
            
            #If author specified a user
            if user is not None:
                #If the user was found in the server
                if realname is not None:
                    #Give credit to user specified
                    user_ticket_credit = self.settings.getUserStat(realname, ctx.guild, "TicketCredit")
                    if user_ticket_credit is None:
                        self.settings.setUserStat(realname, ctx.guild, "TicketCredit", 1)
                    self.settings.incrementStat(realname, ctx.guild, "TicketCredit", 1)
                    
                    msg += f'*{realname}* resolved the ticket, and has been given +1 credit.'
                #User was not found in server
                else:
                    return await ctx.channel.send(f'Sorry, I can\'t find a user named *{realname}*. Please try a different name.')
            #No user specified
            else:
                msg += 'No credit was given.'
            
            #Remove the ticket from the list
            tickets.remove(this_ticket)
            self.settings.setServerStat(ctx.guild, "TicketList", tickets)
            
            return await ctx.channel.send(msg)

    @commands.command()
    async def editticket(self, ctx):
        #edit an existing ticket
        return

    @commands.command()
    async def claimticket(self, ctx):
        #claim a ticket from the queue that you want to work on
        return

    @commands.command()
    async def unclaimticket(self, ctx):
        #unclaim a ticket and add it back to the queue (maybe implement as part of $claimticket)
        return
        
    @commands.command()
    async def reset_user(self, ctx):
        #reset UserStat TicketsOpen
        self.settings.setUserStat(ctx.author, ctx.guild, "TicketsOpen", 0)
        return await ctx.channel.send(f'Reset user *{ctx.author}*\'s ticket count to 0.')
