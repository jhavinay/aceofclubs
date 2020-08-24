import asyncio
import logging
import time
import socketio
import json
import argparse

import find_src
from player.bot import Bot
from player.aoctranslate import AOCTranslate

# Information about new position, boardno, hand that we will
# need to pass to bot.reset() at the right time


# bot will be created in main
bot = None

loop = asyncio.get_event_loop()
#sio = socketio.AsyncClient(logger=True, engineio_logger=True,ssl_verify=False)
sio = socketio.AsyncClient(ssl_verify=False)
start_timer = None
seats=["N","E","S","W"]

##set these vvariables
userId=2576
sectionId=1176
#tableNo=1,only needed if jooining initially. assuming director as preseated te bot for now so no need to join seat

roundDataId=0

# Whenever boardNo is changed, the seat and hand are inconsistent
# with the boardNo and should be set to None
# It is only when both of these are non-null that we can
# start performing other operations
gboardNo=0
gseat = None
gseatIndex = None
ghand = None

def isDirty():
    return (gboardNo is None) or (gseat is None) or (ghand is None)

# Function to update the key parameters of a hand safely
def updateData(newboardNo, newSeat=None, newHand=None):
    if not isDirty and newboardNo == gboardNo:
        return
    # Assumption is that if we get information for
    # the same board number again we do not update
    if newBoardNo != gboardno:
        gboardno = newBoardNo
        gseat = newSeat
        ghand = newHand
    else:
        if newSeat:
            gseat = newSeat
        if newHand:
            ghand = newHand

    if not isDirty:
        bot.resetHand(ghand, gboardNo, gseat)
    return
            

async def send_ping():
    global start_timer
    start_timer = time.time()
    await sio.emit('ping_from_client')

@sio.event
async def pong_from_server():
    global start_timer
    latency = time.time() - start_timer
    print('latency is {0:.2f} ms'.format(latency * 1000))
    await sio.sleep(1)
    await send_ping()

#auth name space
@sio.on('connect', namespace='/auth')
async def connect():
    print('connected to auth')
    await sio.emit('login',userId, namespace='/auth')

@sio.event(namespace='/auth')
async def login(data):
    print('logged in')
    await sio.emit('join-game',{ "sectionId": sectionId }, namespace='/section')

#section namespace
@sio.event(namespace='/section')
async def chat_res(data):
    print('got chat')
        
@sio.event(namespace='/section')
async def join_game_button(data):
     print('got join_game_button')

@sio.event(namespace='/section')
async def section(data):
    print('got section')
    await sio.emit('join-table',{ "sectionId": sectionId, "roundDataId": 0 }, namespace='/mtable')

#mtable namespace
@sio.event(namespace='/mtable')
async def chat_res(data):
    print('got chat_res om mtable'+json.dumps(data))
        
@sio.event(namespace='/mtable')
async def cards(data):
     print('got cards'+json.dumps(data))
     print(data[seatIndex])
     newhand = AOCTranslate.getHand(data[seatIndex])
     # TODO: call updateData() here
     newseat=seats[index]
     updateData(newHand=newHand, newSeat=newSeat, newBoardNo=newBoardNo)


@sio.event(namespace='/mtable')
async def bid_play(data):
    print('got bid_play'+json.dumps(data))
    global roundDataId
    global gboardNo
    roundDataId=data["roundDataId"]
    tmpboard=data["boardNo"]
    bidsMade = data["bids"]
    auction = AOCTranslate.getAuction(bidsMade, boardNo)
    print("auction is {}".format(auction))
    if not isDirty:
        bot.resetAuction(auction)
    if tmpboard != boardNo:
        boardNo=tmpboard
        # TODO: call updateData() here
        print("new hand is {}".format(newhand))
    else:
        bot.applyAuctionDiff(auction)

'''
got bid_play{"roundDataId": 107672, "boardNo": 1, "status": "BID", "contract": null, "bids": ["ps ;N", "ps ;E", "1H ;S", "  X;W", "ps ;N", "1S ;E"], "nextBid": "1NX;S", "plays": [], "nextPlay": null, "claims": [], "northSees": [], "eastSees": [], "southSees": [], "westSees": [], "undo": null, "id": 2559}
'''

@sio.event(namespace='/mtable')
async def player_join(data):
    print('got player_join')
    for index, player in enumerate(data) :
        if player !=None and player["id"] ==userId:
            seat=seats[index]
            newseat = AOCTranslate.position(seat)
            updateData(newBoardno=boardno, seat=newseat)
            print("new seat is {}".format(newseat))
            global seatIndex
            seatIndex=index
            break

@sio.event(namespace='/mtable')
async def bid_made(data):
     print('got bid_made' + json.dumps(data))
     lastBid=data["lastBid"]
     print("lastBid string is " + lastBid)
     [lastBidStr,lastBidPos]=lastBid.split(sep=";")
     #register last bid, if not registered
     print("last call string is " + lastBidStr)
     if lastBid:
        lastCall = AOCTranslate.call(lastBidStr, lastbidPos)
        print("last call is {}".format(lastCall))
        bot.RegisterCall(lastbidder.caller, lastCall, lastCall.info)
     nextBid=data["nextBid"]
     if not nextBid:
        return
     [nextBidStr,nextBidPos]=nextBid.split(sep=";")
     if nextBidPos==seat:
        bidToMake, info = bot.getNextCallAndStateInfo()
        bidstr = AOCTranslate.callstring(bidToMake)
        print("making bid " +bidstr) 
        await sio.emit('bid-made',{ "sectionId": sectionId, "roundDataId": roundDataId, "bid": bidstr +" ;" +seat}, namespace='/mtable')

# in play seat at second position means whose ccardds to play, thirs position winner mean who has to play
#usefull for declarer
@sio.event(namespace='/mtable')
async def play_made(data):
    print('got play_made')
    #register last play, if not registered
     #if nextplay.winner==myposition
     #get play
     #await sio.emit('play-made',{ "sectionId": 1, roundDataId: 1, play: "cardnumber;nextplay.seat;nextplay.winner" }, namespace='/mtable')

@sio.event(namespace='/mtable')
async def claim_made(data):
    print('got claim_made')
    await sio.emit('claim-accepted',{ "sectionId": sectionId, "roundDataId": roundDataId, "vote": str(seatIndex)+"_0" }, namespace='/mtable')
    
@sio.event(namespace='/mtable')
async def undo_made(data):
    print('got undo_made')
    await sio.emit('undo-accepted',{ "sectionId": sectionId, "roundDataId": roundDataId, "vote": str(seatIndex)+"_0" }, namespace='/mtable')
   
@sio.event(namespace='/mtable')
async def api_error(data):
    print('api_error'+json.dumps(data))
   
async def start_server():
    #await sio.connect('http://192.168.43.12:3000')
    await sio.connect('https://aceofclubs.in:3000', namespaces=['/auth','/section','/mtable'])
    await sio.wait()


if __name__ == '__main__':
    mylogger = logging.getLogger(__name__)
    mylogger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        description="Create an AOC client"
    )
    parser.add_argument("--player", dest="who", default="N", choices=seats)

    args = parser.parse_args()
    mylogger.info("Creating bot for position " + args.who)
    bot = Bot.getBot(args.who)
    print(bot)

    loop.run_until_complete(start_server())
    pass
