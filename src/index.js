const express = require('express');
const app = express();
const http = require('http');
const env = require('dotenv')
const fs = require('fs');
const { Server } = require("socket.io");
const server = http.createServer(app);
const io = new Server(server);

function seed() {
    let data = fs.readFileSync('seed.json', {encoding:'utf8'});
    return JSON.parse(data)['seed']
}

env.config()

const peers = seed(); // seed from dns
let glob = null

app.get('/get_balance', (req, res) => {
    io.emit("fetch", "bal")
    glob = res
    while(glob != null) {
        continue
    }
})



const Websocket = require('ws');


class P2pServer {
    constructor() {
        this.sockets = [];
    }

    listen() {
        const server = new Websocket.Server({ port: process.env.P2P_PORT });
        server.on('connection', socket => this.connectSocket(socket));

        this.connectToPeers();
        console.log(`P2P | Listening on *:${process.env.P2P_PORT}`);
    }

    connectToPeers() {
        peers.forEach(peer => {
            const socket = new Websocket(peer);

            socket.on('open', () => this.connectSocket(socket));
        });
    }

    connectSocket(socket) {
        this.sockets.push(socket);
        this.messageHandler(socket);
        // this.sendChain(socket);

    }
    //updating this method as this message handler updates the chain
    //by replacing it, which comes to contrary when transaction object is being sent to it
    messageHandler(socket) {
        socket.on('message', (message) => {
            let socketid = this.sockets.indexOf(socket)
            message = JSON.parse(message.toString())
            message.sender = socketid
            message = JSON.stringify(message)
            io.emit("message", message)
        });
    }

    send(socket, data) {
        socket.send(data);
    }
    
    sendInd(socketid, data) {
        this.sockets[socketid].send(data)
    }

    broadcast(data) {
        this.sockets.forEach(socket => this.send(socket, data));
    }

}

console.log(" -- Initiating NODEJS SERVER -- ")
p2p = new P2pServer()
app.use(express.static("./../../static/"))


io.on('connection', (socket) => {
    console.log('NODEJS | Connected to Python');
    socket.emit('get_blockchain_updates', "akaa")
    socket.on('fetch', d => {
        console.log("DDDDD")
        glob.send(d)
        glob = null

    })
    socket.on('relay', (data) => {
        console.log("NODEJS | Recieved Relay")
        console.log(data)
        if (data.r == null) {
            p2p.broadcast(data.data)
        } else {
            p2p.sendInd(data.r, data.data)
        }
    })
});

server.listen(process.env.PORT, () => {
    console.log('NODEJS | Interpython listening on *:' + String(process.env.PORT));
});

p2p.listen()

