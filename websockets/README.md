# Websockets Server

## API
There are two main endpoints:
### Listen to a websocket
  GET ws://HOSTNAME/listen/{ID}
  POST ws://HOSTNAME/broadcast/{ID}
  ```JSON
    {
        // anything you want 
    }
  ```
  
  Broadcast will send whatever body you want to all the listeners.  

  This server does not include authentication or privilege at all.  What I've done before is to make broadcast only available to the server, but listen publically available through nginx.