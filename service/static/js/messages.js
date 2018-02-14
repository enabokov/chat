import $ from 'jquery';

function getCachedMessages() {
  $.ajax({
    url: '/chat/get_cached_messages',
    method: 'GET',
    async: true,
    contentType: 'application/json; charset=utf-8',
    success: function (data) {
      sendMessage(_data.name, _data.time, _data.message)
    },
    error: function (data) {}
  });
}

function getMessage() {
  let selector = $('input')[0];
  let msg = selector.value;
  selector.value = "";
  msg.trim();
  return msg;
}


function log(message) {
  let chat_box = $('#chat_box');
  chat_box.append('<p>' + message + '</p>');
  chat_box.scrollTop(chat_box.scrollTop() + 1000);
}

function sendMessage(json_message, left=false) {
  let msg = null;
  try {
    msg = JSON.parse(json_message.toString());
  } catch (e) {
    return false;
  }
  let chat_box = $('#chat_box');
  if (!left)
    if ([].constructor === msg)
      for(let i = 0; i < msg.length; i++)
        chat_box.append('<p>(' + msg[i].time + ') ' + msg[i].name + ': ->  ' + msg[i].message + '</p>');
    else
      chat_box.append('<p>(' + msg.time + ') ' + msg.name + ': ->  ' + msg.message + '</p>');
  else
    chat_box.append('<p>' + msg.name + ' ' + msg.message + '</p>');
  chat_box.scrollTop(chat_box.scrollTop() + 1000);
}


$(function() {
  let connection = null;
  function connect() {
    disconnect();
    let wsURI = (window.location.protocol === 'https:'&&'wss://'||'ws://')+window.location.host + '/chat';
    connection = new WebSocket(wsURI);
    log('Connecting...');
    connection.onopen = function () {
      log('Connection established');
      getCachedMessages()
    };
    connection.onclose = function (event) {
      log('Disconnected...');
      connection = null;
    };
    connection.onmessage = function (event) {
      sendMessage(event.data)
    };
  }
  function disconnect() {
    if (connection != null) {
      log('Connection closing...');
      connection.send('left chat...',);
      connection.close();
      connection = null;
    }
  }

  $('.send_message')
      .on('keypress', function (event) {
        if (event.which === 13) {
            let message = getMessage(true);
            sendMessage(message);
            connection.send(message);
            return false;
        }
      })
      .on('click', function (event) {
        if (this.tagName === 'BUTTON') {
            let message = getMessage();
            sendMessage(message);
            connection.send(message);
            return false;
        }
      });
  if (window.location.host + '/chat')
    if (connection == null)
      connect();
    $('#logged_out').click(function() {
    if (connection != null)
      disconnect();
      return false;
    });
    return false;
});