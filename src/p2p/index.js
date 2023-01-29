const express = require('express');
const app = express();
const http = require('http');
const server = http.createServer(app);
const { Server } = require("socket.io");
const io = new Server(server);
const Websocket = require('ws');

const P2P_PORT =  44444;

const peers = []; // seed from dns

class P2pServer {
    constructor() {
        this.sockets = [];
    }

    listen() {
        const server = new Websocket.Server({ port: P2P_PORT });
        server.on('connection', socket => this.connectSocket(socket));

        this.connectToPeers();
        console.log(`P2P | Listening on *:${P2P_PORT}`);
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
        this.sendChain(socket);

    }
    //updating this method as this message handler updates the chain
    //by replacing it, which comes to contrary when transaction object is being sent to it
    messageHandler(socket) {
        socket.on('message', message => {
            io.emit("test")
        });
    }

    send(socket, data) {
        socket.send(data);
    }

    broadcast(data) {
        this.sockets.forEach(socket => this.send(socket, data));
    }

}
p2p = new P2pServer()
app.use(express.static("./../../static/"))


io.on('connection', (socket) => {
    console.log('NODEJS | Connected to Python');
    socket.emit('get_blockchain_updates', "akaa")
    socket.on('relay', (data) => {
        if (!data.r) {
            p2p.broadcast(data.data)
        } else {
            p2p.send(data.r, data.data)
        }
    })
});

server.listen(4999, () => {
  console.log('NODEJS | Interpython listening on *:4999');
});

p2p.listen()

